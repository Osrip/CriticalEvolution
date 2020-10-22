from automatic_plot_helper import all_folders_in_dir_with
from automatic_plot_helper import load_isings_attr
from automatic_plot_helper import load_isings_specific_path
from automatic_plot_helper import attribute_from_isings
from automatic_plot_helper import load_settings
from automatic_plot_helper import choose_copied_isings
from plot_many_simulations_parallel_two_populations import calc_normalized_fitness
import numpy as np
import matplotlib.pyplot as plt
import os


def main_plot_parallel_sims(folder_name, plot_settings):
    attrs_lists = load_attrs(folder_name, plot_settings)
    plot(attrs_lists, plot_settings)



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
    save_name = 'several_sims_criticial_{}.png'.format(plot_settings['attr'])
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    plt.savefig(save_dir+save_name, bbox_inches='tight', dpi=300)


def load_attrs(folder_name, plot_settings):
    folder_dir = 'save/{}'.format(folder_name)
    dir_list = all_folders_in_dir_with(folder_dir, 'sim')
    attrs_list_all_sims = []
    settings_list = []
    for dir in dir_list:
        isings_list = load_isings_specific_path('{}/isings'.format(dir))
        if plot_settings['only_copied']:
            isings_list = [choose_copied_isings(isings) for isings in isings_list]
        if plot_settings['attr'] == 'norm_avg_energy' or plot_settings['attr'] == 'norm_food_and_ts_avg_energy':
            calc_normalized_fitness(isings_list, plot_settings)
        attrs_list = [attribute_from_isings(isings, plot_settings['attr']) for isings in isings_list]
        attrs_list_all_sims.append(attrs_list)
        del isings_list
        # settings_list.append(load_settings(dir))
    return attrs_list_all_sims


if __name__ == '__main__':
    # folder_name = 'sim-20201020-181300_parallel_TEST'
    plot_settings = {}
    plot_settings['add_save_name'] = ''
    plot_settings['attr'] = 'norm_avg_energy'
    # plot_settings['only_plot_fittest']
    plot_settings['ylim'] = (-0.001, 0.015)
    # This only plots individuals that have not been mutated in previous generation (thus were fittest in previous generation)
    plot_settings['only_copied'] = False

    folder_names = ['sim-20201019-154142_parallel_parallel_mean_4000_ts_b1_rand_ts', 'sim-20201019-154106_parallel_parallel_mean_4000_ts_b1_fixed_ts', 'sim-20201019-153950_parallel_parallel_mean_4000_ts_b10_fixed_ts', 'sim-20201019-153921_parallel_parallel_mean_4000_ts_b10_rand_ts']
    for folder_name in folder_names:

        main_plot_parallel_sims(folder_name, plot_settings)