/*
 * Inclusive and exclusive scan implemented in OpenMP
 *
 */

#include <vector>
#include <iostream>
#include <omp.h>

template<class T, class Op>
void omp_inclusive_scan(const std::vector<T>& a, std::vector<T>& y,	T identity, Op op) {
    const std::size_t n = a.size();
    if (n == 0) { y.clear(); return; }
    y.resize(n);
	
    std::vector<T> block_sum;  // one slot per thread

    // local inclusive scans and capture each block's total
    #pragma omp parallel
    {
        const int tid = omp_get_thread_num();
        const int nth = omp_get_num_threads();

		// Allocate and initialize one slot per thread to 'identity'.
        // Only one thread does this. All threads wait at the implicit barrier here.
		#pragma omp single
		block_sum.assign(nth, identity);

        // contiguous chunk per thread
		std::size_t chunk = (n + nth - 1) / nth;
		std::size_t b = std::min(tid * chunk, n);
		std::size_t e = std::min(b + chunk, n);

		// local inclusive scan within the block
		T run = identity;
		for (auto i = b; i < e; ++i) {
			run = op(run, a[i]);  // left fold
			y[i] = run;
		}
		block_sum[tid] = run; // total of each block

#pragma omp barrier

        // compute the left-to-right prefix
		// after this, block_sum[t] holds the offset that precedes block t
        #pragma omp single
        {
            T off = identity;
            for (auto t = 0; t < nth; ++t) {
                T tmp = block_sum[t]; block_sum[t] = off;  off = op(off, tmp);
            }
        } // implicit barrier

		// all threads adjust their partition
		const T off = block_sum[tid];
		for (auto i = b; i < e; ++i)
			y[i] = op(off, y[i]);
    }
}

template<class T, class Op>
void omp_exclusive_scan(const std::vector<T>& a, std::vector<T>& y,
						T identity, Op op) {
    const std::size_t n = a.size();
    if (n == 0) { y.clear(); return; }
    y.resize(n);

    std::vector<T> block_sum;  // one slot per thread

    #pragma omp parallel
    {
        const int tid = omp_get_thread_num();
        const int nth = omp_get_num_threads();

		// Allocate and initialize one slot per thread to 'identity'.
        // Only one thread does this. All threads wait at the implicit barrier here.
		#pragma omp single
		block_sum.assign(nth, identity);

		// contiguous partitions
		std::size_t chunk = (n + nth - 1) / nth;
		std::size_t b = std::min(tid * chunk, n);
		std::size_t e = std::min(b + chunk, n);
		
        // local exclusive scan
        T run = identity;
        for (auto i = b; i < e; ++i) {
            y[i] = run;          // value before a[i]
            run = op(run, a[i]); // accumulate a[i]
        }
        block_sum[tid] = run;

        #pragma omp barrier

        // prefix of block sums in left-to-right order, done by one thread		
        #pragma omp single
        {
            T off = identity;
            for (auto t = 0; t < nth; ++t) {
                T tmp = block_sum[t];
                block_sum[t] = off;
                off = op(off, tmp);
            }
        } // implicit barrier here

        // add offset of previous blocks on the left
        const T off = block_sum[tid];
        for (auto i = b; i < e; ++i)
			y[i] = op(off, y[i]);
    }
}


int main() {
	std::vector<int> x{-2,4,2,-1,-1,1,-3,2,1,4,1,5};

    std::vector<int> inc, exc;
    omp_inclusive_scan(x, inc, 0, std::plus<int>{});
    omp_exclusive_scan(x, exc, 0, std::plus<int>{});

	std::cout << "x:         ";
	for (auto v : x) std::cout << v << ' ';
    std::cout << "\ninclusive: ";
    for (auto v : inc) std::cout << v << ' ';
    std::cout << "\nexclusive: ";
    for (auto v : exc) std::cout << v << ' ';
    std::cout << '\n';
}
