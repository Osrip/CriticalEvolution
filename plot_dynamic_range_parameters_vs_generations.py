import matplotlib
matplotlib.use('Agg')
from automatic_plot_helper import all_sim_names_in_parallel_folder
from heat_capacity_parameter import calc_heat_cap_param_main
import numpy as np

import matplotlib.pyplot as plt
import os
import pickle


def main_plot_parallel_sims(folder_name, plot_settings):

    if not plot_settings['only_plot']:
        attrs_lists = load_dynamic_range_param(folder_name, plot_settings)
        save_plot_data(folder_name, attrs_lists, plot_settings)
    else:
        attrs_lists = load_plot_data(folder_name, plot_settings)
    plot(attrs_lists, plot_settings)


def save_plot_data(folder_name, attrs_lists, plot_settings):
    save_dir = 'save/{}/one_pop_plot_data/'.format(folder_name)
    save_name = 'plot_dynamic_range_param_data.pickle'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    pickle_out = open(save_dir + save_name, 'wb')
    pickle.dump(attrs_lists, pickle_out)
    pickle_out.close()


def load_plot_data(folder_name, plot_settings):
    save_dir = 'save/{}/one_pop_plot_data/'.format(folder_name)
    save_name = 'plot_dynamic_range_param_data.pickle'
    print('Load plot data from: {}{}'.format(save_dir, save_name))

    file = open(save_dir+save_name, 'rb')
    attrs_lists = pickle.load(file)
    file.close()

    return attrs_lists





def plot(delta_dicts_all_sims, plot_settings):
    plt.figure(figsize=(10, 7))

    for delta_dict in delta_dicts_all_sims:
        generations = list(delta_dict.keys())
        mean_attrs_list = delta_dict.values()
        plt.scatter(generations, mean_attrs_list, s=2, alpha=0.2)
        if plot_settings['sliding_window']:
            slided_mean_attrs_list, slided_x_axis = slide_window(mean_attrs_list, plot_settings['sliding_window_size'])
            plt.plot(slided_x_axis, slided_mean_attrs_list, alpha=0.8, linewidth=2)
        # plt.scatter(generations, mean_attrs_list, s=20, alpha=1)
    plt.xlabel('Generation')
    plt.ylabel(plot_settings['attr'])
    plt.ylim(plot_settings['ylim'])



    save_dir = 'save/{}/figs/several_plots{}/'.format(folder_name, plot_settings['add_save_name'])
    save_name = 'several_sims_criticial_{}{}_{}_min_ts{}_min_food{}_{}.png'. \
        format(plot_settings['attr'], plot_settings['only_copied_str'], plot_settings['folder_name'],
               plot_settings['min_ts_for_plot'], plot_settings['min_food_for_plot'],
               plot_settings['plot_generations_str'])
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    plt.savefig(save_dir+save_name, bbox_inches='tight', dpi=300)


def load_dynamic_range_param(folder_name, plot_settings):
    folder_dir = 'save/{}'.format(folder_name)
    sim_names = all_sim_names_in_parallel_folder(folder_name)
    delta_dicts_all_sims = []
    for sim_name in sim_names:
        module_settings = {}
        mean_log_beta_distance_dict, log_beta_distance_dict, beta_distance_dict, beta_index_max, betas_max_gen_dict, \
        heat_caps_max_dict, smoothed_heat_caps = calc_heat_cap_param_main(sim_name, module_settings, gaussian_kernel=plot_settings['gaussian_kernel'])
        delta_dict = mean_log_beta_distance_dict
        delta_dicts_all_sims.append(delta_dict)


        # settings_list.append(load_settings(dir))
    return delta_dicts_all_sims


def below_threshold_nan(isings_list, sim_settings):
    for i, isings in enumerate(isings_list):
        if isings[0].time_steps < plot_settings['min_ts_for_plot']:
            isings_list[i] = None
        if sim_settings['random_food_seasons']:
            if isings[0].food_in_env < plot_settings['min_food_for_plot']:
                isings_list[i] = None
    return isings_list

def slide_window(iterable, win_size):
    slided = []
    x_axis_gens = []
    n = 0
    while n+win_size < len(iterable)-1:
        mean = np.nanmean(iterable[n:n+win_size])
        slided.append(mean)
        x_axis_gens.append(n+int(win_size/2))
        n += 1
    return slided, x_axis_gens


if __name__ == '__main__':
    # folder_name = 'sim-20201020-181300_parallel_TEST'
    plot_settings = {}
    # Only plot loads previously saved plotting file instead of loading all simulations to save time
    plot_settings['only_plot'] = False

    plot_settings['add_save_name'] = ''
    # plot_settings['only_plot_fittest']

    plot_settings['ylim'] = None
    # This only plots individuals that have not been mutated in previous generation (thus were fittest in previous generation)
    plot_settings['sliding_window'] = True
    plot_settings['sliding_window_size'] = 100

    plot_settings['gaussian_kernel'] = True

    folder_names = ['sim-20201216-150319_parallel_Test_dynamic_range_param_many_heat_caps_compressed']
    for folder_name in folder_names:
        plot_settings['folder_name'] = folder_name
        main_plot_parallel_sims(folder_name, plot_settings)