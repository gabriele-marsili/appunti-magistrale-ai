// base version, it draws a single pixed in a critical section
// lots of contention
#include <iostream>
#include <complex>
#include <omp.h>
#include "gfx.h"

#if defined(NO_DISPLAY)
#include <atomic>
#define DISPLAY(X)
#else
#define DISPLAY(X) X
#endif

// a very large value
const int max_iter = 50000;  

// size in pixels of the picture window
const int XSIZE = 1280;
const int YSIZE = 800;

/* Coordinates of the bounding box of the Mandelbrot set */
const double XMIN = -2.3, XMAX = 1.0;
const double SCALE = (XMAX - XMIN)*YSIZE / XSIZE;
const double YMIN = -SCALE/2, YMAX = SCALE/2;

struct pixel {
    int r, g, b;
};

const pixel colors[] = {
    { 66,  30,  15}, 
    { 25,   7,  26},
    {  9,   1,  47},
    {  4,   4,  73},
    {  0,   7, 100},
    { 12,  44, 138},
    { 24,  82, 177},
    { 57, 125, 209},
    {134, 181, 229},
    {211, 236, 248},
    {241, 233, 191},
    {248, 201,  95},
    {255, 170,   0},
    {204, 128,   0},
    {153,  87,   0},
    {106,  52,   3} };
const int NCOLORS = sizeof(colors)/sizeof(pixel);


//  z_(0)   = 0;
//  z_(n+1) = z_n * z_n + (cx + i*cy);
//
// iterates until ||z_n|| > 2, or max_iter
//
int iterate(const std::complex<double>& c) {
	std::complex<double> z=0;
	int iter = 0;
	while(iter < max_iter && std::abs(z) <= 2.0) {
		z = z*z + c;
		++iter;
	}
	return iter;
}

void drawpixel(int x, int y, int iter) {
	int r=0,g=0,b=0;
    if (iter < max_iter) {
		const int m= iter % NCOLORS;
		r = colors[m].r;
		g = colors[m].g;
		b = colors[m].b;
	}
	gfx_color(r, g, b);
    gfx_point(x, y);
}

int main(int argc, char *argv[]) {
    DISPLAY(gfx_open(XSIZE, YSIZE, "Mandelbrot Set"));
#if defined(NO_DISPLAY)	
	std::atomic<int> fake{0};
#endif	

	auto t0 = omp_get_wtime();

#pragma omp parallel for schedule(runtime) 
    for (int y = 0; y < YSIZE; ++y) {
		const double im = YMAX - (YMAX - YMIN) * y / (YSIZE - 1);
		for (int x = 0; x < XSIZE; ++x) {
            const double re = XMIN + (XMAX - XMIN) * x / (XSIZE - 1);
            const int v = iterate(std::complex<double>(re, im));
#if defined(NO_DISPLAY)
			fake.fetch_add(v,std::memory_order_relaxed);
#else
			// draws a single pixel
#pragma omp critical
			drawpixel( x, y, v);
#endif			
		}
    }
	auto t1 = omp_get_wtime();
	std::cout << "Time (ms): " << (t1 - t0) * 1000.0  << "\n";
	DISPLAY(std::cout << "Click to finish\n"; gfx_wait());
}
