#include <cstdio>

#include <omp.h> // required only for OpenMP runtime API

int main() {
  #pragma omp parallel
  {  // <- spawning of threads
	  int i = omp_get_thread_num(); // thread id starts from 0
	  int n = omp_get_num_threads();
	  std::printf("Hello from thread %d of %d\n", i, n);
  }  // <- joining of threads
}

