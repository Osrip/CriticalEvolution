repeats=5
cores=5

# subfolder="plot_many_functions"
subfolder="sim-$(date '+%d%m%Y-%H%M%S')test"
# date="date +%s"
# subfolder="$date$subfolder"

# command="python3 train_different_betas.py -g_2000 -rand_ts -rand ts lim 100 3900 -iso -c 4 -no_trace -b_jump -subfolder ${subfolder}"
command="python3 train_different_betas.py -g 20 -t 20 -iso -no_trace -b_jump -noplt -subfolder ${subfolder} -n Run_{1}"



parallel --bar --eta -j${cores} ${command} ::: $(seq ${repeats})

# seq 5 | parallel -n0 ${command} 