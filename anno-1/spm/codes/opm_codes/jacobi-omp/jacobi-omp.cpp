//
// 2-D Jacobi 5-point stencil (Jacobi relaxation)
//
#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <string>
#include <omp.h>


struct Grid {
    int rows{}, cols{};
    std::vector<float> data;
    Grid(int r, int c, float init = 0.0f)
        : rows(r), cols(c), data(std::size_t(r) * std::size_t(c), init) {}
    float& operator()(int i, int j) noexcept {
        return data[std::size_t(i) * cols + std::size_t(j)];
    }
    const float& operator()(int i, int j) const {
        return data[std::size_t(i) * cols + std::size_t(j)];
    }
};

static void initData(Grid& g) {
    for (int i = 0; i < g.rows; ++i)
        for (int j = 0; j < g.cols; ++j)
            g(i, j) = float(((i / 121) + (j / 121)) % 2);
}

static void writeOutput(const std::string& path, const Grid& g, int precision = 6) {
    std::ofstream out(path, std::ios::binary);
    if (!out) {
        std::cerr << "ERROR: cannot open output file '" << path << "'\n";
        std::exit(1);
    }
    out.setf(std::ios::fixed);
    out << std::setprecision(precision);
    for (int i = 0; i < g.rows; ++i) {
        for (int j = 0; j < g.cols; ++j) {
            out << g(i, j);
            if (j + 1 < g.cols) out << ' ';
        }
        out << '\n';
    }
}

// command line arguments
struct Args {
	int rows{};
	int cols{};
	std::string outfile;
	float eps{};
	int max_iters{10000};
};


static Args parse_args(int argc, char* argv[]) {
    Args a;
    if (argc < 5) {
        std::cerr << "Usage: " << argv[0]
                  << " <rows> <cols> <out.txt> <errThreshold> [max-iterations="
				  << a.max_iters << "]\n";
        std::exit(1);
    }

    a.rows = std::stoi(argv[1]);
    a.cols = std::stoi(argv[2]);
    if (a.rows < 1 || a.cols < 1) {
        std::cerr << "ERROR: rows/cols must be >= 1\n";
        std::exit(1);
    }
    a.outfile  = argv[3];
    a.eps      = std::stof(argv[4]);
	if (argc > 5) a.max_iters = std::stoi(argv[5]);
    return a;
}


int main(int argc, char* argv[]) {
	const auto args = parse_args(argc, argv);

    Grid A(args.rows, args.cols);
    Grid B(args.rows, args.cols);
    initData(A);
    B = A;  // same initial content

	// sanity check, if there is no interior,
	// there's nothing to iterate on
    if (args.rows < 3 || args.cols < 3) {
        writeOutput(args.outfile, A);
        std::cout << "Iterations: 0\nTime (s): 0\n";
        return 0;
    }

	// Shared state across iterations
    Grid* curr = &A;
    Grid* next = &B;

	const int R = A.rows, C = A.cols;

    std::size_t iterations = 0;
    double error   = double(args.eps) + 1.0;
	double error2  = 0.0;
	bool converged = false;

	auto t0 = omp_get_wtime();
	
#pragma omp parallel default(none) \
	shared(curr, next, R, C, iterations, error, error2, converged, args)
    {
        while (true) {

#pragma omp for schedule(static) reduction(+:error2)
            for (int i = 1; i < R - 1; ++i) {
				double local = 0.0;
                for (int j = 1; j < C - 1; ++j) {
					const float v =  0.25f * (
                        (*curr)(i + 1, j) + (*curr)(i, j - 1) +
                        (*curr)(i, j + 1) + (*curr)(i - 1, j));
					const float d = (*curr)(i, j) - v;
					(*next)(i, j) = v;
					local += double(d) * double(d);
                }
				error2 += local;
            }

            #pragma omp single nowait
            {
				error = error2;
				error2= 0.0;

				// Copy borders from curr to next (fixed boundary conditions)
                for (int j = 0; j < C; ++j) {
                    (*next)(0, j)     = (*curr)(0, j);
                    (*next)(R - 1, j) = (*curr)(R - 1, j);
                }
                for (int i = 1; i < R - 1; ++i) {
                    (*next)(i, 0)     = (*curr)(i, 0);
                    (*next)(i, C - 1) = (*curr)(i, C - 1);
                }

				// swap buffers for next sweep
                std::swap(curr, next);
                ++iterations;

                converged = (error <= args.eps);
            }  // <--- no implicit barrier because of nowait

            #pragma omp barrier
            if (converged || iterations >= std::size_t(args.max_iters)) break;
        }
    }
	auto t1 = omp_get_wtime();
	
    writeOutput(args.outfile, *curr);
    std::cout << "Iterations: " << iterations << "\n";
    std::cout << "Final error: " << error << "\n";
    std::cout << "Time (s): " << (t1-t0) << "\n";
    return 0;
}
