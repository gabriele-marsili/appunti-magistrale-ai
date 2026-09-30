#include <vector>
#include <algorithm>
#include <random>
#include <iostream>
#include <omp.h>

int main(int argc, char* argv[]) {
	if (argc!=2) {
		std::cout << "use: " << argv[0] << " size\n";
		return -1;
	}
	std::size_t size = std::stol(argv[1]);
    std::vector<double> A(size), B(size);
	
	// generate
    std::mt19937 rng(111);
    std::uniform_real_distribution<double> d(0.f, 1.f);
	std::generate(A.begin(), A.end(), [&]{ return double(d(rng)); });
	std::generate(B.begin(), B.end(), [&]{ return double(d(rng)); });

	auto t0=omp_get_wtime();
	auto sum=0.0;
#pragma omp parallel for reduction(+:sum)
	for(std::size_t i=0; i< size; ++i) {
		sum += A[i] * B[i];
	}
	auto t1=omp_get_wtime();
	std::cout << "size= " << size << "\n";
	std::cout << "Time (ms): " << (t1 - t0) * 1000.0 << " sum= " << sum << "\n";
}
