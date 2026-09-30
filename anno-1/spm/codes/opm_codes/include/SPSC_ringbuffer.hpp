// it requires at least C++20 
#pragma once
#include <atomic>
#include <cstddef>
#include <utility>
#include <new>
#include <vector>
#include <stdexcept>

namespace spsc {

inline constexpr std::size_t cacheline = 64;

template <typename T>
class ringBuffer {
	// Since capacity_ is a power of two, index wrap-around can be implemented
	// with a cheap bit mask instead of a "expensive" modulo operation

	// Put each shared index on a separate cache line
	// This avoids false sharing between producer and consumer
    struct alignas(cacheline) padded_index {
        std::atomic<std::size_t> v;
    };

	// Fixed-size preallocated storage
	// This simple implementation assumes that T is default-constructible
	// and assignable, because elements are written into existing slots
    std::vector<T> buf_;

	// Runtime capacity and mask.
	// The mask is valid because the constructor requires capacity_ to be a power of two
    std::size_t capacity_;
    std::size_t mask_;

	// Ownership rule:
	// - only the consumer updates head_
	// - only the producer updates tail_
	// Each thread may access its own index with relaxed ordering
	// Acquire/release is needed only when observing the index owned by the other side
	//
	// padded_index forces head_ and tail_ to lay in different cache lines
    padded_index head_{std::atomic<std::size_t>{0}};
    padded_index tail_{std::atomic<std::size_t>{0}};

    // Local caches of the other side's index
	// They reduce the number of atomic loads on the shared indices and thus
	// reduce coherence traffic in the fast path
    std::size_t prod_head_cache_ = 0; // producer's last-seen head
    std::size_t cons_tail_cache_ = 0; // consumer's last-seen tail

    static bool is_power_of_two(std::size_t x) {
        return x != 0 && (x & (x - 1)) == 0;
    }

public:
	// non-copiable non-movable ringBuffer
    explicit ringBuffer(std::size_t capacity_pow2)
        : buf_(capacity_pow2),
          capacity_(capacity_pow2),
          mask_(capacity_pow2 - 1) {
        if (!is_power_of_two(capacity_pow2))
            throw std::invalid_argument("ringBuffer capacity must be a power of two");
    }

	ringBuffer(ringBuffer&&) = delete;
    ringBuffer(const ringBuffer&) = delete;
    ringBuffer& operator=(const ringBuffer&) = delete;
	ringBuffer& operator=(ringBuffer&&) = delete;
	
    // --- Non-blocking API ---
    template <class... Args>
    bool emplace(Args&&... args) {
		// The producer owns tail_, so reading its own index does not require
		// synchronization with the consumer (relaxed is enough here)
        const auto tail = tail_.v.load(std::memory_order_relaxed);
        const std::size_t next = (tail + 1) & mask_;

        if (next == prod_head_cache_) {
			// head_ is owned by the consumer
			// We use acquire when observing it, so that once we see the consumer
			// has advanced head_, that observation is properly ordered with the
			// consumer's earlier reads from the buffer
            prod_head_cache_ = head_.v.load(std::memory_order_acquire);
            if (next == prod_head_cache_)
				return false; // buffer full
        }

		// constructs a temporary T, then assigns into the slot:
		// uses move-assignment if available, otherwise copy-assignment
        buf_[tail] = T(std::forward<Args>(args)...);             
		
		// First write the payload into the reserved slot
		// Then publish the new tail with release ordering
		// The release store makes the payload visible to the consumer:
		// if the consumer later observes this tail value with acquire,
		// it is guaranteed to see the payload already written
        tail_.v.store(next, std::memory_order_release);   
        return true;
    }

	// Non-blocking push for the producer
	// Returns false immediately if the queue appears full
    bool try_push(const T& x)  { return emplace(x); }
    bool try_push(T&& x)       { return emplace(std::move(x)); }  

	// Non-blocking pop for the consumer
	// Returns false immediately if the queue appears empty
    bool try_pop(T& out) {
		// The consumer owns head_, so reading its own index does not require
		// synchronization with the producer (relaxed is enough here)
        const auto head = head_.v.load(std::memory_order_relaxed);

        if (head == cons_tail_cache_) {
			// tail_ is owned by the producer
			// We use acquire when observing it, so that after seeing a new tail value,
			// the consumer is guaranteed to see the corresponding payload writes
            cons_tail_cache_ = tail_.v.load(std::memory_order_acquire);
            if (head == cons_tail_cache_) return false; // buffer empty
        }

		// read element and advance head
        out = std::move(buf_[head]);
		const std::size_t next = (head + 1) & mask_;
		
		// Read the payload first, then publish the new head with release ordering
		// This release store tells the producer that the slot has been consumed
		// and can be reused safely
        head_.v.store(next, std::memory_order_release);
        return true;
    }

    // --- Blocking API ---
	
	// Blocking emplace for the producer
	// If the queue is full, wait until the consumer advances head_
    template <class... Args>
    void emplace_wait(Args&&... args) {
		const auto tail = tail_.v.load(std::memory_order_relaxed);
		const std::size_t next = (tail + 1) & mask_;		
        while( next == prod_head_cache_ ) { // no space available
			std::size_t expected = prod_head_cache_;
			prod_head_cache_ = head_.v.load(std::memory_order_acquire);
			if (next == prod_head_cache_) {
				// Wait while head_ is still equal to the cached value
				// atomic::wait(expected) blocks until the atomic value changes from expected
				head_.v.wait(expected,std::memory_order_acquire);
			} else break;
		}
		
		// Publish the new element exactly as in the non-blocking case,
		// then wake up one consumer that may be waiting for data
		buf_[tail] = T(std::forward<Args>(args)...);		
		tail_.v.store(next, std::memory_order_release);
		tail_.v.notify_one();
    }

	// Blocking push
	// If the queue is full, wait until head_ changes, meaning that the consumer
	// has freed at least one slot
    void push_wait(const T& x)  { emplace_wait(x); }
    void push_wait(T&& x)       { emplace_wait(std::move(x)); }

	// Blocking pop
	// If the queue is empty, wait until tail_ changes, meaning that the producer
	// has published at least one new item
    void pop_wait(T& out) {
		const auto head = head_.v.load(std::memory_order_relaxed);

		while( head == cons_tail_cache_ ) { // no data available
			std::size_t expected = cons_tail_cache_;
			cons_tail_cache_ = tail_.v.load(std::memory_order_acquire);
			if (head == cons_tail_cache_) {
				// Wait while tail_ is still equal to the cached value
				// The consumer wakes up when the producer publishes a new tail value
				tail_.v.wait(expected, std::memory_order_acquire);
			} else break;
		}
		// Consume the element, publish the new head, then wake up
		// one producer that may be waiting for free space
		out = std::move(buf_[head]);
		const std::size_t next = (head + 1) & mask_;
		head_.v.store(next, std::memory_order_release);
		head_.v.notify_one();
    }
	
	// Diagnostic helpers
	// These queries are fine for observation/debugging, but their result is only
	// a snapshot and may become stale immediately in a concurrent execution
    bool empty() const {
        auto h = head_.v.load(std::memory_order_acquire);
        auto t = tail_.v.load(std::memory_order_acquire);
        return h == t;
    }
    bool full() const {
        auto h = head_.v.load(std::memory_order_acquire);
        auto t = tail_.v.load(std::memory_order_acquire);
        return ((t + 1) & mask_) == h;
    }
    std::size_t capacity() const { return capacity_; }
};

} // namespace spsc
