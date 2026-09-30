#include <iostream>
#include <limits>
#include <vector>
#include <iomanip>
#include <omp.h>


static double compute_pi(std::size_t N) {
    const double step = 1.0 / static_cast<double>(N);

	// upper bound on the n. of threads used in the next parallel session
	int num_threads = omp_get_max_threads();  
	std::vector<double> local(num_threads, 0.0);
	
#pragma omp parallel
	{
		double   x = 0.0;
		int tid = omp_get_thread_num(); 
		double r = 0.0;
		
		#pragma omp for
		for (std::size_t i = 0; i < N; ++i) {
			x = (static_cast<double>(i) + 0.5) * step;
			r += 4.0 / (1.0 + x * x);
		}
		local[tid] = r; // single write, reduce cache traffic
	}
	// final reduction
	double sum = 0.0;
#if 1
	// pure sequential reduction
	for(int i=0; i< num_threads; ++i) {
		sum += local[i];
	}
#else
	// try SIMD vectorization
	const double* p = local.data();
#pragma omp simd reduction(+:sum)
	for (int i=0; i<num_threads;++i)
		sum += p[i];
#endif
	
    return step * sum;
}


int main(int argc, char * argv[]) {
  if(argc != 2) {
     std::cout << "Usage is: " << argv[0] << " num_steps\n";
     return(-1);
  }

  const std::size_t N = static_cast<std::size_t>(std::stoull(argv[1]));
  if (N == 0) {
	  std::cerr << "ERROR: <num_steps> must be a positive integer.\n";
        return -1;
  }
  
  const auto t0 = omp_get_wtime();
  const auto pi = compute_pi(N);
  const auto t1 = omp_get_wtime();

  
  std::cout << "Pi = " << std::setprecision(std::numeric_limits<double>::digits10 +1) << pi << "\n";
  std::cout << "Pi = 3.141592653589793238 (first 18 decimal digits)\n";
  std::printf("Time %.3f (ms)\n", (t1-t0)*1000.0);
  return(0);
}

