#pragma once

#include <atomic>
#include <cstddef>
#include <cstdint>
#include <new>
#include <thread>
#include <type_traits>

#if defined(__x86_64__) || defined(_M_X64)
#include <immintrin.h>
#endif

// ------------------------------------------------------------
// Utilities
// ------------------------------------------------------------

constexpr unsigned long BACKOFF_MIN = 4;
constexpr unsigned long BACKOFF_MAX = 32;
inline constexpr std::size_t CACHE_LINE_SIZE = 64;

inline constexpr bool is_power_of_two(std::size_t x) noexcept {
    return x != 0 && (x & (x - 1)) == 0;
}

inline constexpr std::size_t next_power_of_two(std::size_t x) noexcept {
    std::size_t p = 1;
    while (p < x) p <<= 1;
    return p;
}

// Backoff primitive used only in short retry loops.
// On x86 we use PAUSE, otherwise fall back to yield().
inline void cpu_relax() noexcept {
#if defined(__x86_64__) || defined(_M_X64)
    _mm_pause();
#else
    std::this_thread::yield();
#endif
}

// ------------------------------------------------------------
// Bounded lock-free MPMC pointer queue
// ------------------------------------------------------------
//
// Main idea:
// - fixed-size ring buffer
// - each cell carries a sequence number "seq"
// - producers compete on enqueue_pos_
// - consumers compete on dequeue_pos_
// - seq tells whether a slot is free, full, or belongs to a later wrap-around
//
// This queue stores pointers:
// - push/pop do not copy or move T objects
// - ownership/lifetime of pointed objects is managed by the caller
//
template <class T>
class mpmc_ptr_queue {
    static_assert(!std::is_reference_v<T>, "T must not be a reference type");

private:

    struct alignas(CACHE_LINE_SIZE) cell_t {
        // Sequence number used to detect the logical state of the slot
        // It is the key ingredient that makes the bounded MPMC protocol work
        std::atomic<std::size_t> seq;

        // Payload pointer stored in this slot.
        T* data;

        // Keep each queue cell on its own cache line.
        // This reduces false sharing between adjacent cells, since different
        // producers/consumers may concurrently access sequence numbers of
        // neighboring slots
        static constexpr std::size_t used_bytes =
            sizeof(std::atomic<std::size_t>) + sizeof(T*);

        static constexpr std::size_t pad_bytes =
            (used_bytes < CACHE_LINE_SIZE) ? (CACHE_LINE_SIZE - used_bytes) : 1;

        char pad[pad_bytes];
    };

    static_assert(sizeof(cell_t) == CACHE_LINE_SIZE,
                  "cell_t should occupy exactly one cache line");

public:
    mpmc_ptr_queue() = default;

    // Construct a queue with the requested capacity
    // If capacity is not a power of two, it is rounded up to the next one
    explicit mpmc_ptr_queue(std::size_t capacity) {
        if (!init(capacity)) {
            throw std::bad_alloc{};
        }
    }

    ~mpmc_ptr_queue() {
        delete[] buffer_;
    }

    mpmc_ptr_queue(const mpmc_ptr_queue&)            = delete;
    mpmc_ptr_queue& operator=(const mpmc_ptr_queue&) = delete;
    mpmc_ptr_queue(mpmc_ptr_queue&&)                 = delete;
    mpmc_ptr_queue& operator=(mpmc_ptr_queue&&)      = delete;

    // Late initialization variant, useful only if default construction is needed
    // Returns false if called more than once or if allocation fails.
    bool init(std::size_t capacity) {
        if (buffer_ != nullptr) {
            return false;
        }

        if (capacity < 2) {
            capacity = 2;
        }
        if (!is_power_of_two(capacity)) {
            capacity = next_power_of_two(capacity);
        }

        cell_t* tmp = new (std::nothrow) cell_t[capacity];
        if (!tmp) {
            return false;
        }

        // Initial state:
        // slot i is free for logical enqueue position i
        for (std::size_t i = 0; i < capacity; ++i) {
            tmp[i].data = nullptr;
            tmp[i].seq.store(i, std::memory_order_relaxed);
        }

        buffer_   = tmp;
        capacity_ = capacity;
        mask_     = capacity - 1;

        enqueue_pos_.store(0, std::memory_order_relaxed);
        dequeue_pos_.store(0, std::memory_order_relaxed);
        return true;
    }

    [[nodiscard]] std::size_t capacity() const noexcept {
        return capacity_;
    }

    [[nodiscard]] bool empty() const noexcept {
        return dequeue_pos_.load(std::memory_order_relaxed) ==
               enqueue_pos_.load(std::memory_order_relaxed);
    }

    // Non-blocking enqueue.
    // Returns false if the queue is full.
    //
    // Protocol summary:
    // 1. read current enqueue position
    // 2. inspect the target cell sequence number
    // 3. if seq == pos, the cell is free for this producer position
    // 4. reserve the position with CAS on enqueue_pos_
    // 5. write the pointer
    // 6. publish the cell with seq = pos + 1 (release)
    //
    [[nodiscard]] bool try_push(T* ptr) noexcept {
        unsigned long bk = BACKOFF_MIN;
        cell_t* cell;
        std::size_t pos = enqueue_pos_.load(std::memory_order_relaxed);

        for (;;) {
            cell = &buffer_[pos & mask_];

            // Acquire is needed because observing the published seq must also make
            // visible the payload write performed before the producer stored that seq.
            const std::size_t seq = cell->seq.load(std::memory_order_acquire);

            // Interpretation:
            // seq == pos     -> slot is free for this enqueue position
            // seq <  pos     -> queue appears full from this producer view
            // seq >  pos     -> another producer advanced, retry from fresh position
            const std::intptr_t diff =
                static_cast<std::intptr_t>(seq) - static_cast<std::intptr_t>(pos);

            if (diff == 0) {
                // Try to reserve this logical enqueue position.
                if (enqueue_pos_.compare_exchange_weak(
                        pos,
                        pos + 1,
                        std::memory_order_relaxed,
                        std::memory_order_relaxed)) {
                    break;
                }
            } else if (diff < 0) {
                return false; // queue full
            } else {
                pos = enqueue_pos_.load(std::memory_order_relaxed);
            }

            // exponential delay with max value
            for (unsigned i = 0; i < bk; ++i) {
                cpu_relax();
            }
            bk = (bk < BACKOFF_MAX) ? (bk << 1) : BACKOFF_MAX;
        }

        // We own this slot now.
        cell->data = ptr;

        // Publish the slot as full for the matching consumer position
        // Release pairs with the consumer acquire load of seq
        cell->seq.store(pos + 1, std::memory_order_release);
        return true;
    }

    // Non-blocking dequeue.
    // Returns false if the queue is empty.
    //
    // Protocol summary:
    // 1. read current dequeue position
    // 2. inspect the target cell sequence number
    // 3. if seq == pos + 1, the cell contains valid data for this consumer position
    // 4. reserve the position with CAS on dequeue_pos_
    // 5. read the pointer
    // 6. mark the slot reusable in the next ring cycle with
    //    seq = pos + capacity (release)
    //
    [[nodiscard]] bool try_pop(T*& ptr) noexcept {
        cell_t* cell;
        std::size_t pos = dequeue_pos_.load(std::memory_order_relaxed);
        unsigned long bk = BACKOFF_MIN;

        for (;;) {
            cell = &buffer_[pos & mask_];

            // Acquire is needed because once we observe the "full" state of the slot,
            // we must also see the payload previously written by the producer
            const std::size_t seq = cell->seq.load(std::memory_order_acquire);

            // Interpretation:
            // seq == pos + 1 -> slot is full and ready for this dequeue position
            // seq <  pos + 1 -> queue appears empty from this consumer view
            // seq >  pos + 1 -> another consumer advanced, retry from fresh position
            const std::intptr_t diff =
                static_cast<std::intptr_t>(seq) - static_cast<std::intptr_t>(pos + 1);

            if (diff == 0) {
                // Try to reserve this logical dequeue position
                if (dequeue_pos_.compare_exchange_weak(
                        pos,
                        pos + 1,
                        std::memory_order_relaxed,
                        std::memory_order_relaxed)) {
                    break;
                }
            } else if (diff < 0) {
                return false; // queue empty
            } else {
                pos = dequeue_pos_.load(std::memory_order_relaxed);
            }

            // exponential delay with max value
            for (unsigned i = 0; i < bk; ++i) {
                cpu_relax();
            }
            bk = (bk < BACKOFF_MAX) ? (bk << 1) : BACKOFF_MAX;
        }

        // We own this slot now.
        ptr = cell->data;

        // Mark the slot as free again for the next wrap-around
        // Since capacity is a power of two, this is exactly the next logical
        // sequence at which a producer may reuse the same physical cell
        cell->seq.store(pos + capacity_, std::memory_order_release);
        return true;
    }

private:
    // Separate cache lines help reduce false sharing between producers and consumers
    alignas(CACHE_LINE_SIZE) std::atomic<std::size_t> enqueue_pos_{0};
    alignas(CACHE_LINE_SIZE) std::atomic<std::size_t> dequeue_pos_{0};

    cell_t* buffer_ = nullptr;
    std::size_t capacity_ = 0;
    std::size_t mask_ = 0;
};
