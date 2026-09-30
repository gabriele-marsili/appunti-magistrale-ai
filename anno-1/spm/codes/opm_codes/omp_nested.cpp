#include <cstdio>
#include <omp.h>

// execute with OMP_NESTED=true ./omp_nested
// execute with OMP_MAX_ACTIVE_LEVELS=3 ./omp_nested
int main() {

	//omp_set_nested(1);  // deprecated
	

#pragma omp parallel num_threads(3)
    {
		std::printf("Level %d/%d - (). Hi from thread %d of %d\n",
					omp_get_level(),
					omp_get_max_active_levels(),
					omp_get_thread_num(),
					omp_get_num_threads());       

		int parent = omp_get_thread_num();
		
		#pragma omp parallel num_threads(2) //nested 
        {
			std::printf("Level %d/%d - (parent %d) Hi from thread %d of %d\n",
						omp_get_level(),omp_get_max_active_levels(), parent,
						omp_get_thread_num(), omp_get_num_threads());       

			int parent = omp_get_thread_num();
			
			#pragma omp parallel num_threads(2) // nested again
            {
				std::printf("Level %d/%d - (parent %d) Hi from thread %d of %d\n",
							omp_get_level(),omp_get_max_active_levels(), parent,
							omp_get_thread_num(), omp_get_num_threads());
            }
        }
    }
    return 0;
}
