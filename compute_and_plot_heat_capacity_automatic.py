from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import list_to_blank_seperated_str
from automatic_plot_helper import load_settings
import visualize_heat_capacity_generational_automatic
import os

def main(sim_name, settings):
    gen_nums = detect_all_isings(sim_name)
    generations = [0, gen_nums[-1]]
    cores = 5
    compute_plot_heat_capacity(sim_name, generations, cores, settings)

def compute_plot_heat_capacity(sim_name, generation_list, cores, settings):
    gens_str = list_to_blank_seperated_str(generation_list)
    os.system('bash bash-heat-capacity-generational-automatic.sh {} "{}" {}'.format(sim_name, gens_str, cores))
    visualize_heat_capacity_generational_automatic.main(sim_name, settings, generation_list)

if __name__ == '__main__':
    sim_name = 'sim-20200327-215801-g_8000_-b_0.1_-ref_2000_-a_500_1000_2000_4000_6000_8000_-n_4_sensors'
    cores = 22
    generation_list = [0, 4000, 7999]
    settings = load_settings(sim_name)
    compute_plot_heat_capacity(sim_name, generation_list, cores, settings)

