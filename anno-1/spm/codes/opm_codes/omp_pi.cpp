#include <iostream>
#include <limits>
#include <iomanip>
#include <omp.h>

static double compute_pi(std::size_t N) {
    const double step = 1.0 / static_cast<double>(N);
    double sum = 0.0;
	double   x = 0.0;
	
#pragma omp parallel for private(x) reduction(+:sum)
    for (std::size_t i = 0; i < N; ++i) {
        x = (static_cast<double>(i) + 0.5) * step;
        sum += 4.0 / (1.0 + x * x);
    }
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

