import matplotlib
matplotlib.use('Agg')
from automatic_plot_helper import all_folders_in_dir_with
from automatic_plot_helper import load_isings_attr
from automatic_plot_helper import load_isings_specific_path
from automatic_plot_helper import attribute_from_isings
from automatic_plot_helper import load_settings
from automatic_plot_helper import choose_copied_isings
from automatic_plot_helper import calc_normalized_fitness
from automatic_plot_helper import load_isings_from_list
import numpy as np

import matplotlib.pyplot as plt
import os
import pickle


def main_plot_parallel_sims(folder_name, plot_settings):
    if plot_settings['only_copied']:
        plot_settings['only_copied_str'] = '_only_copied_orgs'
    else:
        plot_settings['only_copied_str'] = '_all_orgs'

    if plot_settings['only_plot_certain_generations']:
        plot_settings['plot_generations_str'] = 'gen_{}_to_{}'\
            .format(plot_settings['lowest_and_highest_generations_to_be_plotted'][0],
                    plot_settings['lowest_and_highest_generations_to_be_plotted'][1])
    else:
        plot_settings['plot_generations_str'] = 'gen_all'

    if not plot_settings['only_plot']:
        attrs_lists = load_attrs(folder_name, plot_settings)
        save_plot_data(folder_name, attrs_lists, plot_settings)
    else:
        attrs_lists = load_plot_data(folder_name, plot_settings)
    plot(attrs_lists, plot_settings)


def save_plot_data(folder_name, attrs_lists, plot_settings):
    save_dir = 'save/{}/one_pop_plot_data/'.format(folder_name)
    save_name = 'plot_data_{}{}_min_ts{}_min_food{}_{}.pickle'\
        .format(plot_settings['attr'], plot_settings['only_copied_str'], plot_settings['min_ts_for_plot'],
                plot_settings['min_food_for_plot'], plot_settings['plot_generations_str'])
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    pickle_out = open(save_dir + save_name, 'wb')
    pickle.dump(attrs_lists, pickle_out)
    pickle_out.close()


def load_plot_data(folder_name, plot_settings):
    save_dir = 'save/{}/one_pop_plot_data/'.format(folder_name)
    save_name = 'plot_data_{}{}_min_ts{}_min_food{}_{}.pickle'.\
        format(plot_settings['attr'], plot_settings['only_copied_str'], plot_settings['min_ts_for_plot'],
               plot_settings['min_food_for_plot'], plot_settings['plot_generations_str'])
    print('Load plot data from: {}{}'.format(save_dir, save_name))
    try:
        file = open(save_dir+save_name, 'rb')
        attrs_lists = pickle.load(file)
        file.close()
    except Exception:
        if not plot_settings['only_plot_certain_generations']:
            save_name = 'plot_data_{}{}_min_ts{}_min_food{}.pickle'. \
                format(plot_settings['attr'], plot_settings['only_copied_str'], plot_settings['min_ts_for_plot'],
                       plot_settings['min_food_for_plot'])
            file = open(save_dir+save_name, 'rb')
            attrs_lists = pickle.load(file)
            file.close()
    return attrs_lists



def plot(attrs_lists, plot_settings):
    plt.figure(figsize=(10, 7))

    for attrs_list in attrs_lists:
        generations = np.arange(len(attrs_list))
        mean_attrs_list = [np.nanmean(gen_attrs) for gen_attrs in attrs_list]
        plt.scatter(generations, mean_attrs_list, s=2, alpha=0.2)
        if plot_settings['sliding_window']:
            slided_mean_attrs_list, slided_x_axis = slide_window(mean_attrs_list, plot_settings['sliding_window_size'])
            plt.plot(slided_x_axis, slided_mean_attrs_list, alpha=0.8, linewidth=2)
        # plt.scatter(generations, mean_attrs_list, s=20, alpha=1)
    plt.xlabel('Generation')
    plt.ylabel(plot_settings['attr'])
    plt.ylim(plot_settings['ylim'])



    save_dir = 'save/{}/figs/several_plots{}/'.format(folder_name, plot_settings['add_save_name'])
    save_name = 'several_sims_criticial_{}{}_{}_min_ts{}_min_food{}_{}.png'.\
        format(plot_settings['attr'], plot_settings['only_copied_str'], plot_settings['folder_name'],
               plot_settings['min_ts_for_plot'], plot_settings['min_food_for_plot'],
               plot_settings['plot_generations_str'])
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    plt.savefig(save_dir+save_name, bbox_inches='tight', dpi=300)


def load_attrs(folder_name, plot_settings):
    folder_dir = 'save/{}'.format(folder_name)
    dir_list = all_folders_in_dir_with(folder_dir, 'sim')
    attrs_list_all_sims = []
    settings_list = []
    for dir in dir_list:
        sim_name = dir[(dir.rfind('save/')+5):]
        settings = load_settings(sim_name)

        if plot_settings['only_plot_certain_generations']:
            load_generations = np.arange(plot_settings['lowest_and_highest_generations_to_be_plotted'][0],
                                         plot_settings['lowest_and_highest_generations_to_be_plotted'][1]+1)
            isings_list = load_isings_from_list(sim_name, load_generations)
        else:
            isings_list = load_isings_specific_path('{}/isings'.format(dir))


        if plot_settings['only_copied']:
            isings_list = [choose_copied_isings(isings) for isings in isings_list]
        if plot_settings['attr'] == 'norm_avg_energy' or plot_settings['attr'] == 'norm_food_and_ts_avg_energy':

            calc_normalized_fitness(isings_list, plot_settings, settings)

        isings_list = below_threshold_nan(isings_list, settings)
        attrs_list = [attribute_from_isings(isings, plot_settings['attr']) if isings is not None else np.nan
                      for isings in isings_list]
        attrs_list_all_sims.append(attrs_list)
        del isings_list
        # settings_list.append(load_settings(dir))
    return attrs_list_all_sims


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
    plot_settings['only_plot'] = True

    plot_settings['add_save_name'] = ''
    plot_settings['attr'] = 'norm_food_and_ts_avg_energy' #'norm_avg_energy'
    # plot_settings['only_plot_fittest']
    if plot_settings['attr'] == 'norm_food_and_ts_avg_energy':
        plot_settings['ylim'] = (-0.0001, 0.00025)
    else:
        plot_settings['ylim'] = (-0.001, 0.015)
    # This only plots individuals that have not been mutated in previous generation (thus were fittest in previous generation)
    plot_settings['only_copied'] = True
    plot_settings['sliding_window'] = True
    plot_settings['sliding_window_size'] = 200

    # ONLY PLOT HAS TO BE FALSE FOR FOLLOWING SETTINGS to work:
    plot_settings['min_ts_for_plot'] = 200
    plot_settings['min_food_for_plot'] = 0

    plot_settings['only_plot_certain_generations'] = True
    plot_settings['lowest_and_highest_generations_to_be_plotted'] = [0, 1000]

    # folder_names = ['sim-20201022-190625_parallel_b1_rand_seas_g4000_t2000', 'sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000', 'sim-20201022-190605_parallel_b1_rand_seas_g4000_t2000', 'sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000'] #
    # folder_names = ['sim-20201019-154142_parallel_parallel_mean_4000_ts_b1_rand_ts', 'sim-20201019-154106_parallel_parallel_mean_4000_ts_b1_fixed_ts', 'sim-20201019-153950_parallel_parallel_mean_4000_ts_b10_fixed_ts', 'sim-20201019-153921_parallel_parallel_mean_4000_ts_b10_rand_ts']
    # folder_names = ['sim-20201022-190625_parallel_b1_rand_seas_g4000_t2000', 'sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000', 'sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000']
    folder_names =['sim-20201022-184145_parallel_TEST']
    #folder_names = ['sim-20201105-202517_parallel_b10_random_ts_2000_lim_100_3900', 'sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000']
    for folder_name in folder_names:
        plot_settings['folder_name'] = folder_name
        main_plot_parallel_sims(folder_name, plot_settings)