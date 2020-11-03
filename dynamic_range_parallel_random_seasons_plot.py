import os
import numpy as np
from automatic_plot_helper import load_isings_specific_path
from automatic_plot_helper import attribute_from_isings
from automatic_plot_helper import all_folders_in_dir_with
from automatic_plot_helper import load_settings
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
from automatic_plot_helper import all_sim_names_in_parallel_folder
from automatic_plot_helper import choose_copied_isings
from automatic_plot_helper import calc_normalized_fitness
import time


class ResponseCurveSimData:
    def __init__(self, sim_name, folder_name, key, folder_num_in_key,  attrs_list_each_food_num, food_num_list):
        self.sim_name = sim_name
        self.folder_name = folder_name
        self.folder_num_in_key = folder_num_in_key
        self.key = key
        self.attrs_list_each_food_num = attrs_list_each_food_num
        self.food_num_list = food_num_list
        # calculate averages
        self.avg_attr_list = [np.mean(attrs) for attrs in attrs_list_each_food_num]


def dynamic_range_main(folder_name_dict, plot_settings):

    if not plot_settings['only_plot']:
        plot_settings['savefolder_name'] = 'response_plot_{}'.format(time.strftime("%Y%m%d-%H%M%S"))
        os.makedirs('save/{}'.format(plot_settings['savefolder_name']))
        sim_data_list_each_folder = prepare_data(folder_name_dict, plot_settings)
        save_plot_data(sim_data_list_each_folder, plot_settings)
    else:
        sim_data_list_each_folder = load_plot_data(plot_settings['only_plot_folder_name'])
    plot(sim_data_list_each_folder, plot_settings)


def prepare_data(folder_name_dict, plot_settings):


    sim_data_list_each_folder = []
    for key in folder_name_dict:
        folder_name_list = folder_name_dict[key]
        for folder_num_in_key, folder_name in enumerate(folder_name_list):
            sim_names = all_sim_names_in_parallel_folder(folder_name)
            attrs_food_num_lists_each_sim = []
            for sim_name in sim_names:
                attrs_list_each_food_num_all, food_num_list = load_data(sim_name, folder_name, plot_settings)
                sim_data = ResponseCurveSimData(sim_name, folder_name, key, folder_num_in_key,  attrs_list_each_food_num_all, food_num_list)
                attrs_food_num_lists_each_sim.append(sim_data)
            sim_data_list_each_folder.append(attrs_food_num_lists_each_sim)
    return sim_data_list_each_folder



def save_plot_data(plot_data, plot_settings):
    save_dir = 'save/{}/plot_data/'.format(plot_settings['savefolder_name'])
    save_name = 'plot_data.pickle'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    pickle_out = open(save_dir + save_name, 'wb')
    pickle.dump(plot_data, pickle_out)
    pickle_out.close()


def load_plot_data(folder_name):
    save_dir = 'save/{}/plot_data/'.format(folder_name)
    save_name = 'plot_data.pickle'
    print('Load plot data from: {}{}'.format(save_dir, save_name))
    file = open(save_dir+save_name, 'rb')
    plot_data = pickle.load(file)
    file.close()
    return plot_data


def plot(sim_data_list_each_folder, plot_settings):
    for sim_data_list in sim_data_list_each_folder:
        list_of_avg_attr_list = []
        list_of_food_num_list = []
        for sim_data in sim_data_list:
            list_of_avg_attr_list.append(sim_data.avg_attr_list)
            list_of_food_num_list.append(sim_data.food_num_list)

        for food_num_list in list_of_food_num_list:
            if not food_num_list == list_of_food_num_list[0]:
                raise Exception('There seem to be files for different food numbers within the simulations of folder {}'
                                .format(sim_data.folder_name))

        avg_of_avg_attr_list = []
        # This goes through all lists and takes averages of the inner nesting, such that instead of a list of lists
        # we have one list with average value of each entriy of the previous lists,
        # in future do this with np. array and define axis to take average over
        for i in range(len(list_of_avg_attr_list[0])):
            avg_of_avg_attr_list.append(np.mean([list_of_avg_attr_list[j][i] for j in range(len(list_of_avg_attr_list))]))

        marker = plot_settings['marker'][sim_data.folder_num_in_key]
        color = plot_settings['color'][sim_data.key]
        plt.figure(figsize=(10, 7))
        # Plot each simulation
        plt.scatter(list_of_food_num_list, list_of_avg_attr_list, marker=marker, c=color, s=1, alpha=0.2)
        # Plot averages of each folder
        plt.scatter(list_of_food_num_list[0], avg_of_avg_attr_list, marker=marker, c=color, s=5, alpha=0.4, label=sim_data.folder_name)

        plt.ylabel(plot_settings['attr'])
        plt.xlabel('Percentage of food that population was originally trained on')
        save_name = 'response_plot.png'
        save_folder = 'save/{}/figs/'.format(plot_settings['savefolder_name'])
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        plt.savefig(save_folder+save_name, bbox_inches='tight', dpi=150)


def load_data(sim_name, folder_name, plot_settings):
    sim_dir = 'save/{}'.format(sim_name)

    attrs_list_each_food_num_all = []
    attrs_list_each_food_num_critical = []
    attrs_list_each_food_num_sub_critical = []
    food_num_list = []
    dir_list = all_folders_in_dir_with(sim_dir, plot_settings['dynamic_range_folder_name_includes'])
    for dir in dir_list:
        isings_list = load_isings_specific_path(dir)
        if plot_settings['only_copied']:
            isings_list = [choose_copied_isings(isings) for isings in isings_list]
        if plot_settings['attr'] == 'norm_avg_energy' or plot_settings['attr'] == 'norm_food_and_ts_avg_energy':
            settings = load_settings(sim_name)
            calc_normalized_fitness(isings_list, plot_settings, settings)
        isings = make_2d_list_1d(isings_list)
        # isings_populations_seperated = seperate_isolated_populations([isings])
        # isings_critical = isings_populations_seperated[0][0]
        # isings_sub_critical = isings_populations_seperated[1][0]
        attrs_list_each_food_num_all.append(attribute_from_isings(isings, plot_settings['attr']))
        # attrs_list_each_food_num_critical.append(attribute_from_isings(isings_critical, attr))
        # attrs_list_each_food_num_sub_critical.append(attribute_from_isings(isings_sub_critical, attr))
        food_num_list.append(get_int_end_of_str(dir))
    return attrs_list_each_food_num_all, food_num_list


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
    critical_folder_name_list = ['sim-20201022-184145_parallel_TEST']
    sub_critical_folder_name_list =[]
    plot_settings = {}
    plot_settings['only_plot'] = False
    plot_settings['only_plot_folder_name'] = ''
    plot_settings['add_save_name'] = ''
    plot_settings['only_copied'] = True
    plot_settings['attr'] = 'avg_energy'
    plot_settings['color'] = {'critical': 'darkorange', 'sub_critical': 'royalblue', 'super_critical': 'maroon'}
    # This setting defines the markers, which are used in the order that the folder names are listed
    plot_settings['marker'] = ['.', '*', '+']

    plot_settings['dynamic_range_folder_name_includes'] = 'foods_dynamic_range_run'
    folder_name_dict = {'critical': critical_folder_name_list, 'sub_critical': sub_critical_folder_name_list}
    dynamic_range_main(folder_name_dict, plot_settings)