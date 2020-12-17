import matplotlib
matplotlib.use('Agg')
from automatic_plot_helper import all_sim_names_in_parallel_folder
from heat_capacity_parameter import calc_heat_cap_param_main
from scipy.interpolate import interp1d
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
    delta_dicts_all_sims, deltas_dicts_all_sims = attrs_lists
    plot(delta_dicts_all_sims, deltas_dicts_all_sims, plot_settings)


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


def plot(delta_dicts_all_sims, deltas_dicts_all_sims, plot_settings):
    plt.figure(figsize=(10, 7))

    for delta_dict, deltas_dict in zip(delta_dicts_all_sims, deltas_dicts_all_sims):
        # Handle delta dict, which includes mean delta of each generation
        generations = list(delta_dict.keys())
        generations = np.array([int(gen) for gen in generations])
        sorted_gen_indecies = np.argsort(generations)
        generations = np.sort(generations)
        mean_attrs_list = np.array(list(delta_dict.values()))
        mean_attrs_list = mean_attrs_list[sorted_gen_indecies]

        # Handle deltas dict, which includes list of delta of each individual in a generation
        generations_ind = list(deltas_dict.keys())
        generations_ind = np.array([int(gen) for gen in generations_ind])
        sorted_gen_indecies_ind = np.argsort(generations_ind)
        generations_ind = np.sort(generations_ind)
        mean_attrs_list_ind = np.array(list(deltas_dict.values()))
        mean_attrs_list_ind = mean_attrs_list_ind[sorted_gen_indecies_ind]
        # We have a list of delta values for each generation. Unnest the lists and repeat the generations for each
        # individual, such that lists have same dimensions for plotting
        generations_unnested_ind = []
        mean_attr_list_ind_unnested = []
        for gen_ind, mean_attr_list_ind in zip(generations_ind, mean_attrs_list_ind):
            for mean_attr_ind in mean_attr_list_ind:
                generations_unnested_ind.append(gen_ind)
                mean_attr_list_ind_unnested.append(mean_attr_ind)




        if plot_settings['smooth_and_interpolate']:
            '''
            Trying to make some sort of regression, that smoothes and interpolates 
            Trying to find an alternative to moving average, where boundary values are cut off
            '''
            smoothed_mean_attrs_list = gaussian_kernel_smoothing(mean_attrs_list)

            f_interpolate = interp1d(generations, smoothed_mean_attrs_list, kind='cubic')
            x_interp = np.linspace(np.min(generations), np.max(generations), num=4000, endpoint=True)
            y_interp = f_interpolate(x_interp)
            plt.plot(x_interp, y_interp)
        if plot_settings['plot_deltas_of_individuals']:
            plt.scatter(generations_unnested_ind,  mean_attr_list_ind_unnested, s=2, alpha=0.2)
        plt.scatter(generations, mean_attrs_list, s=5, alpha=0.4)

        if plot_settings['sliding_window']:
            slided_mean_attrs_list, slided_x_axis = slide_window(mean_attrs_list, plot_settings['sliding_window_size'])
            plt.plot(slided_x_axis, slided_mean_attrs_list, alpha=0.8, linewidth=2)


    plt.xlabel('Generation')
    plt.ylabel('Delta')
    plt.ylim(plot_settings['ylim'])



    save_dir = 'save/{}/figs/several_plots{}/'.format(folder_name, plot_settings['add_save_name'])
    save_name = 'delta_vs_generations.png'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    plt.savefig(save_dir+save_name, bbox_inches='tight', dpi=300)


def load_dynamic_range_param(folder_name, plot_settings):
    folder_dir = 'save/{}'.format(folder_name)
    sim_names = all_sim_names_in_parallel_folder(folder_name)
    delta_dicts_all_sims = []
    deltas_dicts_all_sims = []
    for sim_name in sim_names:
        module_settings = {}
        mean_log_beta_distance_dict, log_beta_distance_dict, beta_distance_dict, beta_index_max, betas_max_gen_dict, \
        heat_caps_max_dict, smoothed_heat_caps = calc_heat_cap_param_main(sim_name, module_settings, gaussian_kernel=plot_settings['gaussian_kernel'])
        delta_dict = mean_log_beta_distance_dict
        delta_list_dict = log_beta_distance_dict
        delta_dicts_all_sims.append(delta_dict)
        deltas_dicts_all_sims.append(delta_list_dict)


        # settings_list.append(load_settings(dir))
    # delta_dicts_all_sims --> men of each generation, deltas_dicts_all_sims --> each individual in a list
    return (delta_dicts_all_sims, deltas_dicts_all_sims)


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


def gaussian(x, mu, sigma):

    C = 1 / (sigma * np.sqrt(2*np.pi))

    return C * np.exp(-1/2 * (x - mu)**2 / sigma**2)

def gaussian_kernel_smoothing(x):
    '''
    Convolving with gaussian kernel in order to smoothen noisy heat cap data (before eventually looking for maximum)
    '''

    # gaussian kernel with sigma=2.25. mu=0 means, that kernel is centered on the data
    # kernel = gaussian(np.linspace(-3, 3, 15), 0, 2.25)
    kernel = gaussian(np.linspace(-3, 3, 15), 0, 6)
    smoothed_x = np.convolve(x, kernel, mode='same')
    return smoothed_x

if __name__ == '__main__':
    # folder_name = 'sim-20201020-181300_parallel_TEST'
    plot_settings = {}
    # Only plot loads previously saved plotting file instead of loading all simulations to save time
    plot_settings['only_plot'] = True

    plot_settings['add_save_name'] = ''
    # plot_settings['only_plot_fittest']

    plot_settings['ylim'] = None
    # This only plots individuals that have not been mutated in previous generation (thus were fittest in previous generation)
    plot_settings['sliding_window'] = False
    plot_settings['sliding_window_size'] = 100

    plot_settings['smooth_and_interpolate'] = False
    plot_settings['plot_deltas_of_individuals'] = False

    plot_settings['gaussian_kernel'] = True

    folder_names = ['sim-20201210-200605_parallel_b1_dynamic_range_c_20_g4000_t2000_10_sims_HEL_ONLY_PLOT', 'sim-20201210-200613_parallel_b10_dynamic_range_c_20_g4000_t2000_10_sims_HEL_ONLY_PLOT', 'sim-20201211-211021_parallel_b0_1_dynamic_range_c_20_g4000_t2000_10_sims_HEL_ONLY_PLOT']
    for folder_name in folder_names:
        plot_settings['folder_name'] = folder_name
        main_plot_parallel_sims(folder_name, plot_settings)