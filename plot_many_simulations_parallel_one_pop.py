import matplotlib
matplotlib.use('Agg')
from automatic_plot_helper import all_folders_in_dir_with
from automatic_plot_helper import load_isings_attr
from automatic_plot_helper import load_isings_specific_path
from automatic_plot_helper import attribute_from_isings
from automatic_plot_helper import load_settings
from automatic_plot_helper import choose_copied_isings
from automatic_plot_helper import calc_normalized_fitness
import numpy as np

import matplotlib.pyplot as plt
import os
import pickle


def main_plot_parallel_sims(folder_name, plot_settings):
    if plot_settings['only_copied']:
        plot_settings['only_copied_str'] = '_only_copied_orgs'
    else:
        plot_settings['only_copied_str'] = '_all_orgs'

    if not plot_settings['only_plot']:
        attrs_lists = load_attrs(folder_name, plot_settings)
        save_plot_data(folder_name, attrs_lists, plot_settings)
    else:
        attrs_lists = load_plot_data(folder_name, plot_settings)
    plot(attrs_lists, plot_settings)


def save_plot_data(folder_name, attrs_lists, plot_settings):
    save_dir = 'save/{}/one_pop_plot_data/'.format(folder_name)
    save_name = 'plot_data_{}{}.pickle'.format(plot_settings['attr'], plot_settings['only_copied_str'])
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    pickle_out = open(save_dir + save_name, 'wb')
    pickle.dump(attrs_lists, pickle_out)
    pickle_out.close()


def load_plot_data(folder_name, plot_settings):
    save_dir = 'save/{}/one_pop_plot_data/'.format(folder_name)
    save_name = 'plot_data_{}{}.pickle'.format(plot_settings['attr'], plot_settings['only_copied_str'])
    print('Load plot data from: {}{}'.format(save_dir, save_name))
    file = open(save_dir+save_name, 'rb')
    attrs_lists = pickle.load(file)
    file.close()
    return attrs_lists



def plot(attrs_lists, plot_settings):
    plt.figure(figsize=(10, 7))

    for attrs_list in attrs_lists:
        generations = np.arange(len(attrs_list))
        mean_attrs_list = [np.mean(gen_attrs) for gen_attrs in attrs_list]
        plt.scatter(generations, mean_attrs_list, s=2, alpha=0.2)
        # plt.scatter(generations, mean_attrs_list, s=20, alpha=1)
    plt.xlabel('Generation')
    plt.ylabel(plot_settings['attr'])
    plt.ylim(plot_settings['ylim'])



    save_dir = 'save/{}/figs/several_plots{}/'.format(folder_name, plot_settings['add_save_name'])
    save_name = 'several_sims_criticial_{}{}_{}.png'.format(plot_settings['attr'], plot_settings['only_copied_str'], plot_settings['folder_name'])
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
        isings_list = load_isings_specific_path('{}/isings'.format(dir))
        if plot_settings['only_copied']:
            isings_list = [choose_copied_isings(isings) for isings in isings_list]
        if plot_settings['attr'] == 'norm_avg_energy' or plot_settings['attr'] == 'norm_food_and_ts_avg_energy':
            settings = load_settings(sim_name)
            calc_normalized_fitness(isings_list, plot_settings, settings)
        attrs_list = [attribute_from_isings(isings, plot_settings['attr']) for isings in isings_list]
        attrs_list_all_sims.append(attrs_list)
        del isings_list
        # settings_list.append(load_settings(dir))
    return attrs_list_all_sims


if __name__ == '__main__':
    # folder_name = 'sim-20201020-181300_parallel_TEST'
    plot_settings = {}
    plot_settings['only_plot'] = False

    plot_settings['add_save_name'] = ''
    plot_settings['attr'] = 'norm_food_and_ts_avg_energy' #'norm_avg_energy'
    # plot_settings['only_plot_fittest']
    if plot_settings['attr'] == 'norm_food_and_ts_avg_energy':
        plot_settings['ylim'] = (-0.0001, 0.00025)
    else:
        plot_settings['ylim'] = (-0.001, 0.015)
    # This only plots individuals that have not been mutated in previous generation (thus were fittest in previous generation)
    plot_settings['only_copied'] = False

    # folder_names = ['sim-20201022-190625_parallel_b1_rand_seas_g4000_t2000', 'sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000', 'sim-20201022-190605_parallel_b1_rand_seas_g4000_t2000', 'sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000'] #
    # folder_names = ['sim-20201019-154142_parallel_parallel_mean_4000_ts_b1_rand_ts', 'sim-20201019-154106_parallel_parallel_mean_4000_ts_b1_fixed_ts', 'sim-20201019-153950_parallel_parallel_mean_4000_ts_b10_fixed_ts', 'sim-20201019-153921_parallel_parallel_mean_4000_ts_b10_rand_ts']
    folder_names = ['sim-20201022-190625_parallel_b1_rand_seas_g4000_t2000', 'sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000', 'sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000']
    for folder_name in folder_names:
        plot_settings['folder_name'] = folder_name
        main_plot_parallel_sims(folder_name, plot_settings)