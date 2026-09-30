#!/bin/bash

#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:00:05
#SBATCH --output=run-pi_%j.log
#SBATCH --error=run-pi_%j.err

THREADS="1 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30"
RESULTS=results_pi_${SLURM_JOB_ID}.csv
echo "threads,time" > "$RESULTS"
NITERATIONS=1000000000

export OMP_PROC_BIND=close
export OMP_PLACES=cores
for t in $THREADS; do
    export OMP_NUM_THREADS=$t
    srun ./omp_pi $NITERATIONS | awk -v th="$t" '/Time/ { printf "%d,%f\n", th, $2}' >> "$RESULTS"
done


