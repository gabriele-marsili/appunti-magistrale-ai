//
// The program shows how to define a custom reduction
//
//
#include <iostream>
#include <unordered_map>
#include <omp.h>

// user-defined merge function for two unordered_map
void merge_hash(std::unordered_map<int,int>& out, const std::unordered_map<int,int>& in) {
    for (const auto &kv : in) {
        out[kv.first] += kv.second;
    }
}

// Define a custom reduction for std::unordered_map<int,int>
// Syntax: reduction(identifie: type-list : combiner) initializer(initializer-expression)
// omp_out, omp_in, omp_priv, omp_orig are special names that can be used inside the definition
 #pragma omp declare reduction(hash_merge : std::unordered_map<int,int> : merge_hash(omp_out, omp_in)) initializer(omp_priv = omp_orig)

int main() {
    const int N = 20000;
    // global_map will be the reduction variable that collects counts from all iterations
    std::unordered_map<int,int> global_map;
    
    // Parallel loop that updates each thread's private copy of global_map. The steps are:
	// - At loop entry, each thread gets a private global_map and it is initialized by omp_priv = omp_orig.
	// - Since global_map was empty, each thread starts from an empty map.
	// - Each thread updates its own private map inside the loop. 
	// - At the implicit barrier, OpenMP reduces all private maps using the combiner.
	//   by repeatedly calling merge_hash(omp_out, omp_in) until only one map remains, which becomes the final global_map.
    #pragma omp parallel for reduction(hash_merge: global_map)
    for (int i = 0; i < N; i++) {
        int key = i % 10;
        global_map[key] += 1;
    }
    
    // global_map contains the merged result
    for (const auto &p : global_map) {
        std::cout << "Key: " << p.first << ", Count: " << p.second << std::endl;
    }
    
    return 0;
}
