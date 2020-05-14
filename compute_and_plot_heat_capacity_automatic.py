from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import list_to_blank_seperated_str
from automatic_plot_helper import load_settings
import visualize_heat_capacity_generational_automatic
import os

def main(sim_name, settings, generations = None, recorded = False):
    if generations is None:
        gen_nums = detect_all_isings(sim_name)
        generations = [gen_nums[-1]]
    cores = settings['cores']
    compute_plot_heat_capacity(sim_name, generations, cores, settings, recorded)

def compute_plot_heat_capacity(sim_name, generation_list, cores, settings, recorded):
    gens_str = list_to_blank_seperated_str(generation_list)
    if recorded:
        os.system('bash bash-heat-capacity-generational-automatic-recorded.sh {} "{}" {}'
                  .format(sim_name, gens_str, cores))
    else:
        os.system('bash bash-heat-capacity-generational-automatic.sh {} "{}" {}'.format(sim_name, gens_str, cores))
    visualize_heat_capacity_generational_automatic.main(sim_name, settings, None)

if __name__ == '__main__':
    sim_name = 'sim-20200514-013839-g_5_-t_2000_-ref_0_-nat_c_0_-dream_c_0_-rec_c_2_-c_15_-n_long_test'#'sim-20200327-220128-g_8000_-b_1_-ref_2000_-a_500_1000_2000_4000_6000_8000_-n_3_sensors'
    settings = load_settings(sim_name)
    main(sim_name, settings, recorded=True)
    # cores = 3
    # generation_list = [0, 200, 500, 1000, 2000, 4000, 6000, 7999]
    # settings = load_settings(sim_name)
    # compute_plot_heat_capacity(sim_name, generation_list, cores, settings, recorded=True)

