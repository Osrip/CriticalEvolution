repeats=10
cores=10

# subfolder="plot_many_functions"
subfolder_add="g1000_rand_ts"
subfolder="sim-$(date '+%Y%m%d-%H%M%S')_parallel_$subfolder_add"
# date="date +%s"
# subfolder="$date$subfolder"

command="python3 train_different_betas.py -g 1000 -rand_ts -rand_ts_lim 100 3900 -iso -no_trace -b_jump -noplt -subfolder ${subfolder} -n Run_{1}"



parallel --bar --eta -j${cores} ${command} ::: $(seq ${repeats})

# seq 5 | parallel -n0 ${command} 