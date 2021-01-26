import numpy as np
from heat_capacity_parameter import calc_heat_cap_param_main
from automatic_plot_helper import all_sim_names_in_parallel_folder


def dynamic_range_main(folder_name):
    delta_dicts_all_sims, deltas_dicts_all_sims = load_dynamic_range_param(folder_name)

    delta_dict = converting_list_of_dicts_to_dict_of_lists(delta_dicts_all_sims)

    for gen, mean_delta_list_each_sim in delta_dict.items():
        mean_delta_per_sim = np.mean(mean_delta_list_each_sim)
        std_delta_per_sim = np.std(mean_delta_list_each_sim)
        print('Generation {}:\nMean:{}\n Std:{}\n mean deltas OF INDIVIDUALS of all simulations:{}'.format(
            gen, mean_delta_per_sim, std_delta_per_sim, mean_delta_list_each_sim))


def converting_list_of_dicts_to_dict_of_lists(delta_dicts_all_sims):
    # converting to
    generations = list(delta_dicts_all_sims[0].keys())
    dict_sorted_by_generatons = {}
    for gen in generations:
        dict_sorted_by_generatons[gen] = []
    for delta_dict in delta_dicts_all_sims:
        for gen in generations:
            dict_sorted_by_generatons[gen].append(delta_dict[gen])
    return dict_sorted_by_generatons


def load_dynamic_range_param(folder_name):
    folder_dir = 'save/{}'.format(folder_name)
    sim_names = all_sim_names_in_parallel_folder(folder_name)
    delta_dicts_all_sims = []
    deltas_dicts_all_sims = []
    for sim_name in sim_names:
        module_settings = {}
        mean_log_beta_distance_dict, log_beta_distance_dict, beta_distance_dict, beta_index_max, betas_max_gen_dict, \
        heat_caps_max_dict, smoothed_heat_caps = calc_heat_cap_param_main(sim_name, module_settings, gaussian_kernel=True)
        delta_dict = mean_log_beta_distance_dict
        delta_list_dict = log_beta_distance_dict
        delta_dicts_all_sims.append(delta_dict)
        deltas_dicts_all_sims.append(delta_list_dict)


        # settings_list.append(load_settings(dir))
    # delta_dicts_all_sims --> men of each generation, deltas_dicts_all_sims --> each individual in a list
    return (delta_dicts_all_sims, deltas_dicts_all_sims)


if __name__ == '__main__':
    folder_name = 'sim-20210126-000843_parallel_normal_seas_heat_cap_b_1_TEST'
    dynamic_range_main(folder_name)