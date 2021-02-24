import compute_and_plot_heat_capacity_automatic
from automatic_plot_helper import all_sim_names_in_parallel_folder
from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import load_settings
from automatic_plot_helper import save_settings
import numpy as np

def compute_heat_cap_retrospectively(folder_name, every_nth_gen, heat_cap_settings):
    sim_names = all_sim_names_in_parallel_folder(folder_name)
    for sim_name in sim_names:
        gens_in_curr_sim = detect_all_isings(sim_name)
        number_of_gens_calculate = int(len(gens_in_curr_sim) / every_nth_gen)
        gens = np.linspace(gens_in_curr_sim[0], gens_in_curr_sim[-1], number_of_gens_calculate).astype(int)
        orig_settings = load_settings(sim_name)
        for key, val in heat_cap_settings.items():
            orig_settings[key] = val
        save_settings(sim_name, orig_settings)

        compute_and_plot_heat_capacity_automatic.main(sim_name, orig_settings, generations=gens, recorded=True, add_subfolder_to_sim_name=False)


if __name__ == '__main__':
    settings = {}
    #  Only use those entries in settings, that are also used by traibn.py. The settings file of every sim will be
    # overwritten with the here given entries
    settings['cores'] = 10
    settings['plot_heat_cap'] = False
    settings['heat_capacity_props'] = [2, 5, -2, 2, 4, 40] # default: [100, 10, -2, 2, 100, 40]
    every_nth_gen = 20

    folder_names = ['sim-20210224-190549_parallel_test_resrospective_heat_cap']
    for folder_name in folder_names:
        compute_heat_cap_retrospectively(folder_name, every_nth_gen, settings)
