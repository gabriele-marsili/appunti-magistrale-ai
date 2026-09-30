//
// 4-stage pipeline example. 
// Forcing one-to-one mapping of 4 stages to 4 threads.
// 
#include <deque>
#include <utility>
#include <mutex>
#include <condition_variable>
#include <iostream>
#include <omp.h>

// Bounded blocking queue based on std::deque
template<class T>
class BlockingQueue {
    std::deque<T> q;
    std::mutex m;
    std::condition_variable cv_not_full, cv_not_empty;
    const std::size_t cap;
public:
    explicit BlockingQueue(std::size_t c) : cap(c) {}

    void push(const T& v) {
        std::unique_lock<std::mutex> lk(m);
        cv_not_full.wait(lk, [&]{ return q.size() < cap; });
        q.push_back(v);
        lk.unlock();
        cv_not_empty.notify_one();
    }
    void pop(T& out) {
        std::unique_lock<std::mutex> lk(m);
        cv_not_empty.wait(lk, [&]{ return !q.empty(); });
        out = std::move(q.front());
        q.pop_front();
        lk.unlock();
        cv_not_full.notify_one();
    }
};

// A message with stop semantics
struct Msg {
    bool done;
    int  val;
    static Msg data(int x) { return {false, x}; }
    static Msg stop()      { return {true, 0}; }
};

int main() {
    const int N = 100;   
    BlockingQueue<Msg> q01(64), q12(64), q23(64); // queues between stages
    long long total = 0;

	omp_set_dynamic(0); // disable dynamic team-size adjustment
	
    // Pipeline of 4 stages 
    #pragma omp parallel num_threads(4) default(none) \
        shared(N, q01, q12, q23, total, std::cout)
    {
		int tid = omp_get_thread_num();
		if (tid == 0)  // Stage 0: source, produce 1..N
        {
            for (int x = 1; x <= N; ++x) q01.push(Msg::data(x));
            q01.push(Msg::stop());
        }
		else if (tid == 1) // Stage 1: simple map x -> x*x
        {
            for (;;) {
                Msg m;
				q01.pop(m);
                if (m.done) { q12.push(Msg::stop()); break; }
                q12.push(Msg::data(m.val * m.val));
            }
        }
		else if (tid == 2) // Stage 2: filter, keep multiples of 3
        {
            for (;;) {
                Msg m; q12.pop(m);
                if (m.done) { q23.push(Msg::stop()); break; }
                if (m.val % 3 == 0) q23.push(Msg::data(m.val));
            }
        }
		else // Stage 3: sink, compute the sum
        {
            for (;;) {
                Msg m; q23.pop(m);
                if (m.done) break;
                total += m.val;
            }
            std::cout << "Sum: " << total << "\n";
        }
    }
}
