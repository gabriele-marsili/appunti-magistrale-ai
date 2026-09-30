#include <cstdio>
#include <chrono>
#include <thread>
#include <omp.h>


int main() {
    const int n = 20;

    // ordered loop, we can use an ordered region inside it
#pragma omp parallel for ordered schedule(dynamic) num_threads(4)
    for (int i = 0; i < n; i++) {

        int square = i * i;

		int tid= omp_get_thread_num();
		if (tid == 1 || tid == 3) {
			std::this_thread::sleep_for(std::chrono::seconds(1));
		}

		// Only this tiny part is serialized in the loop order (0,1,2,...)
#pragma omp ordered
		std::printf("i=%2d by T%d -> %3d\n", i, tid, square);
    }
    
    return 0;
}
