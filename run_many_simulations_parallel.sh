repeats=2
cores=2

# subfolder="plot_many_functions"
subfolder_add="TEST"
subfolder="sim-$(date '+%Y%m%d-%H%M%S')_parallel_$subfolder_add"
# date="date +%s"
# subfolder="$date$subfolder"

command="python3 train.py -b 1 -g 100 -t 5 -rec_c 50 -c_props 20 20 -2 2 20 40 -rand_ts_lim 100 7900 -noplt -subfolder ${subfolder} -n Run_{1}"



parallel --bar --eta -j${cores} ${command} ::: $(seq ${repeats})

# seq 5 | parallel -n0 ${command} 