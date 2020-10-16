import os
import numpy as np
from automatic_plot_helper import load_isings_specific_path
from automatic_plot_helper import attribute_from_isings
from automatic_plot_helper import all_folders_in_dir_with
import copy
import pandas as pd
import glob
import pickle
from run_combi import RunCombi
import matplotlib.pylab as plt
from matplotlib.lines import Line2D
import seaborn as sns
import re
from isolated_population_helper import seperate_isolated_populations


def plot_dynamic_range(sim_name, plot_settings):
    attrs_list_each_food_num_all, attrs_list_each_food_num_critical, attrs_list_each_food_num_sub_critcal, food_num_list = load_data('avg_energy', sim_name)
    # plot_averages(attrs_list_each_food_num_all, food_num_list, sim_name, plot_settings)
    plot_seperated_averages(attrs_list_each_food_num_critical, attrs_list_each_food_num_sub_critcal, food_num_list,
                            sim_name, plot_settings)


def plot_averages(attrs_list_each_food_num, food_num_list, sim_name, plot_settings):
    avg_attr_list = [np.mean(attrs) for attrs in attrs_list_each_food_num]
    plt.scatter(food_num_list, avg_attr_list)
    # plt.savefig('moinsen.png')
    save_dir = 'save/{}/figs/dynamic_range_plots{}/'.format(sim_name, plot_settings['add_save_name'])
    save_name = 'plot_averages.png'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    plt.savefig(save_dir+save_name, bbox_inches='tight')
    plt.show()


def plot_seperated_averages(attrs_list_each_food_num_critical, attrs_list_each_food_num_sub_critical, food_num_list,
                            sim_name, plot_settings):
    avg_attr_list_critical = [np.mean(attrs) for attrs in attrs_list_each_food_num_critical]
    avg_attr_list_sub_critical = [np.mean(attrs) for attrs in attrs_list_each_food_num_sub_critical]
    plt.figure(figsize=(12, 8))

    # make list of list with similar food_num entries for plotting
    food_num_list_extended_critical = [[food_num for i in range(len(attrs))]
                              for food_num, attrs in zip(food_num_list, attrs_list_each_food_num_critical)]
    food_num_list_extended_sub_critical = [[food_num for i in range(len(attrs))]
                                       for food_num, attrs in zip(food_num_list, attrs_list_each_food_num_sub_critical)]
    # food_num_list_extended = np.array(food_num_list_extended)
    # attrs_list_each_food_num_critical = np.array(attrs_list_each_food_num_critical)
    # attrs_list_each_food_num_sub_critical = np.array(attrs_list_each_food_num_sub_critical)
    # for food_num_critical, food_num_sub_critical, attr_critical, attr_sub_critical in
    #     zip(food_num_list_extended_critical, food_num_list_extended_critical,
    #         attrs_list_each_food_num_critical, attrs_list_each_food_num_sub_critical)

    plt.scatter(food_num_list_extended_critical, attrs_list_each_food_num_critical,
                c=plot_settings['color']['critical'], s=2, alpha=0.4)
    plt.scatter(food_num_list_extended_sub_critical, attrs_list_each_food_num_sub_critical, c=plot_settings['color']['sub_critical'],
                s=2, alpha=0.4)

    plt.scatter(food_num_list, avg_attr_list_critical, c=plot_settings['color']['critical'], label='critical')
    plt.scatter(food_num_list, avg_attr_list_sub_critical, c=plot_settings['color']['sub_critical'],
                label='sub-critical')

    plt.ylabel('avg_energy (normalized for time steps)')
    plt.xlabel('number food particles in simulation')

    plt.legend()
    save_dir = 'save/{}/figs/dynamic_range_plots_foods{}/'.format(sim_name, plot_settings['add_save_name'])
    save_name = 'plot_averages_seperated.png'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    plt.savefig(save_dir+save_name, bbox_inches='tight')
    plt.show()



    # TODO: Debuggen und hier weitermachen!!


def load_data(attr, sim_name):
    sim_dir = 'save/{}'.format(sim_name)
    attrs_list_each_food_num_all = []
    attrs_list_each_food_num_critical = []
    attrs_list_each_food_num_sub_critical = []
    food_num_list = []
    dir_list = all_folders_in_dir_with(sim_dir, 'foods_dynamic_range_run')
    for dir in dir_list:
        isings_list = load_isings_specific_path(dir)
        isings = make_2d_list_1d(isings_list)
        isings_populations_seperated = seperate_isolated_populations([isings])
        isings_critical = isings_populations_seperated[0][0]
        isings_sub_critical = isings_populations_seperated[1][0]
        attrs_list_each_food_num_all.append(attribute_from_isings(isings, attr))
        attrs_list_each_food_num_critical.append(attribute_from_isings(isings_critical, attr))
        attrs_list_each_food_num_sub_critical.append(attribute_from_isings(isings_sub_critical, attr))
        food_num_list.append(get_int_end_of_str(dir))
    return attrs_list_each_food_num_all, attrs_list_each_food_num_critical, attrs_list_each_food_num_sub_critical, food_num_list


def get_int_end_of_str(s):
    m = re.search(r'\d+$', s)
    return int(m.group()) if m else None




def make_2d_list_1d(in_list):
    out_list = []
    for sub_list in in_list:
        for en in sub_list:
            out_list.append(en)
    return out_list


if __name__ == '__main__':
    plot_settings = {}
    plot_settings['add_save_name'] = ''
    plot_settings['color'] = {'critical': 'darkorange', 'sub_critical': 'royalblue', 'super_critical': 'maroon'}
    sim_name = 'sim-20201012-220717-g_2000_-f_1000_-t_2000_-iso_-ref_1000_-rec_c_1000_-a_500_1000_1999_-no_trace_-c_3_-n_different_betas_EVOLVE_MANY_FOODS_DYNAMIC_RANGE_1000'
    plot_dynamic_range(sim_name, plot_settings)
