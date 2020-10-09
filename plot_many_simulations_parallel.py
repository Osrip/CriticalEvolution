import os
import numpy as np
from automatic_plot_helper import all_folders_in_dir_with
from automatic_plot_helper import load_isings_attr
from automatic_plot_helper import load_isings_specific_path
from automatic_plot_helper import attribute_from_isings
import matplotlib.pylab as plt
import pickle

from isolated_population_helper import seperate_isolated_populations


def plot_any_simulations_parallel(folder_name, plot_settings, load_plot_data_only):
    add_name = '_seperated'
    if not load_plot_data_only:
        attrs_list_critical, attrs_list_sub_critical = load_seperated_simulations(folder_name, plot_settings)

        save_plot_data(folder_name, (attrs_list_critical, attrs_list_sub_critical), add_name)
    else:
        attrs_list_critical, attrs_list_sub_critical = load_plot_data(folder_name, add_name)

    plot_seperated_sims(attrs_list_critical, attrs_list_sub_critical, folder_name)


def save_plot_data(folder_name, plot_data, add_name):
    save_folder = 'save/{}/plot_data/'.format(folder_name)
    save_name = '{}plot_data{}.pickle'.format(folder_name, add_name)
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    pickle_out = open(save_folder+save_name, 'wb')
    pickle.dump(plot_data, pickle_out)
    pickle_out.close()


def load_plot_data(folder_name, add_name):
    load_folder = 'save/{}/plot_data/'.format(folder_name)
    load_name = '{}plot_data{}.pickle'.format(folder_name, add_name)
    file = open(load_folder+load_name, 'rb')
    plot_data = pickle.load(file)
    file.close()
    return plot_data


def plot_seperated_sims(attrs_list_critical, attrs_list_sub_critical, folder_name):
    plt.figure(figsize=(10, 7))
    generations = np.arange(len(attrs_list_critical))
    for attrs_crit, attrs_sub in zip(attrs_list_critical, attrs_list_sub_critical):

        plt.plot(generations, attrs_crit, c=plot_settings['color']['critical'], s=4)
        plt.plot(generations, attrs_sub, c=plot_settings['color']['sub_critical'], s=4)

    save_dir = 'save/{}/figs/several_sim_plots{}/'.format(folder_name, plot_settings['add_save_name'])
    save_name = 'several_sims.png'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    plt.savefig(save_dir+save_name, bbox_inches='tight')


def load_simulations_single_population(folder_name, plot_settings):
    '''
    Untested!!
    '''
    folder_dir = 'save/{}'.format(folder_name)
    dir_list = all_folders_in_dir_with(folder_dir, 'sim')
    attrs_lists_sims = []
    for sim_name in dir_list:
        attrs_list = load_isings_attr(sim_name, plot_settings['attr'])
        attrs_lists_sims.append(attrs_list)
    return attrs_lists_sims


def load_seperated_simulations(folder_name, plot_settings):
    folder_dir = 'save/{}'.format(folder_name)
    dir_list = all_folders_in_dir_with(folder_dir, 'sim')
    for dir in dir_list:
        isings_list = load_isings_specific_path('{}/isings'.format(dir))
        isings_list_seperated = seperate_isolated_populations(isings_list)
        isings_list_critical = isings_list_seperated[0]
        isings_list_sub_critical = isings_list_seperated[0]
        attrs_list_critical = [attribute_from_isings(isings_crit, plot_settings['attr']) for isings_crit in isings_list_critical]
        attrs_list_sub_critical = [attribute_from_isings(isings_sub, plot_settings['attr']) for isings_sub in isings_list_sub_critical]

    return attrs_list_critical, attrs_list_sub_critical


if __name__ == '__main__':
    load_plot_data_only = True
    folder_name = 'sim-20201005-205252_parallel_g1000_rand_ts'
    plot_settings = {}
    plot_settings['add_save_name'] = ''
    plot_settings['attr'] = 'avg_energy'
    plot_settings['color'] = {'critical': 'darkorange', 'sub_critical': 'royalblue', 'super_critical': 'maroon'}

    plot_any_simulations_parallel(folder_name, plot_settings, load_plot_data_only)