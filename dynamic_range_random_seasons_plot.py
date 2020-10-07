import os
import numpy as np
from automatic_plot_helper import load_isings_specific_path
from automatic_plot_helper import attribute_from_isings
import copy
import pandas as pd
import glob
import pickle
from run_combi import RunCombi
import matplotlib.pylab as plt
from matplotlib.lines import Line2D
import seaborn as sns
import re


def plot_dynamic_range(sim_name):
    attrs_list_each_food_num, food_num_list = load_data('avg_energy', sim_name)
    plot_averages(attrs_list_each_food_num, food_num_list)


def plot_averages(attrs_list_each_food_num, food_num_list):
    avg_attr_list = [np.mean(attrs) for attrs in attrs_list_each_food_num]
    plt.scatter(food_num_list, avg_attr_list)
    plt.savefig('moinsen.png')
    # TODO: Debuggen und hier weitermachen!!


def load_data(attr, sim_name):
    sim_dir = 'save/{}'.format(sim_name)
    attrs_list_each_food_num = []
    food_num_list = []
    dir_list = all_folders_in_dir_with(sim_dir)
    for dir in dir_list:
        isings_list = load_isings_specific_path(dir)
        isings = make_2d_list_1d(isings_list)
        attrs_list_each_food_num.append(attribute_from_isings(isings, attr))
        food_num_list.append(get_int_end_of_str(dir))
    return attrs_list_each_food_num, food_num_list


def get_int_end_of_str(s):
    m = re.search(r'\d+$', s)
    return int(m.group()) if m else None


def all_folders_in_dir_with(dir, including_name='foods_dynamic_range_run'):
    directory_list = list()
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in dirs:
            if including_name in name:
                directory_list.append(os.path.join(root, name))
    return directory_list


def make_2d_list_1d(in_list):
    out_list = []
    for sub_list in in_list:
        for en in sub_list:
            out_list.append(en)
    return out_list


if __name__ == '__main__':
    plot_settings = {}
    sim_name = 'sim-20201005-115242-g_4000_-t_2000_-rand_seas_-rec_c_1000_-c_props_100_50_-2_2_100_40_-iso_-ref_1000_-c_4_-a_1000_1001_10002_2000_3998_3999_-no_trace_-n_different_betas_rand_seas2_TEST_COPY_2'
    plot_dynamic_range(sim_name)