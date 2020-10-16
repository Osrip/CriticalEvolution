repeats=5
cores=5

# subfolder="plot_many_functions"
subfolder_add="g2000_fixed_ts_only_sub_critical"
subfolder="sim-$(date '+%Y%m%d-%H%M%S')_parallel_$subfolder_add"
# date="date +%s"
# subfolder="$date$subfolder"

command="python3 train.py -b 1 -g 2000 -t 4000 -rand_ts_lim 100 7900 -noplt -subfolder ${subfolder} -n Run_{1}"



parallel --bar --eta -j${cores} ${command} ::: $(seq ${repeats})

# seq 5 | parallel -n0 ${command} 