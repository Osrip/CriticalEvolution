import os
import numpy as np
from automatic_plot_helper import load_isings_specific_path
from automatic_plot_helper import attribute_from_isings
import copy
import pandas as pd
import glob

def load_and_plot(runs_folder):


def plot(run_combis, runs_name, attr):
    unordered_object_df = create_df(run_combis, runs_name, attr)
    new_order_labels = ['b1 summer', 'b1 switched to summer', 'b10 summer', 'b10 switched to summer', 'b1 winter',
                        'b1 switched to winter', 'b10 winter', 'b10 switched to winter']
    ordered_df = reorder_df(unordered_object_df, new_order_labels)
    pass
    # TODO: Create plotting functions


def create_df(run_combis, runs_name, attr):
    data = []
    labels = []
    for run_combi in run_combis:
        switched_repeat_isings, same_repeat_isings = extract_isings(run_combi, runs_name)
        # TODO: Finish to make dataframe

        #Create data frame label
        if run_combi.season == 'summer':
            switched_to = 'winter'
        elif run_combi.season == 'winter':
            switched_to = 'summer'

        #switched_label = "b{} switched from {} to {}".format(run_combi.beta, run_combi.season, switched_to)
        switched_label = "b{} switched to {} {}".format(run_combi.beta, switched_to, run_combi.same_repeat)

        same_label = "b{} {} {}".format(run_combi.beta, run_combi.season, run_combi.same_repeat)

        # Make the currently 2d "repeat_isings" list 1d, which means that all ising objects from all repeated generations are in one big list
        switched_repeat_isings_1d = make_2d_list_1d(switched_repeat_isings)
        same_repeat_isings_1d = make_2d_list_1d(same_repeat_isings)
        del switched_repeat_isings
        del same_repeat_isings

        # Extract attributes from isings
        switched_repeat_isings_1d_attr = attribute_from_isings(switched_repeat_isings_1d, attr)
        same_repeat_isings_1d_attr = attribute_from_isings(same_repeat_isings_1d, attr)
        del switched_repeat_isings_1d
        del same_repeat_isings_1d


        # Append stuff to lists that will be converted to df
        data.append(same_repeat_isings_1d_attr)
        data.append(switched_repeat_isings_1d_attr)
        labels.append(same_label)
        labels.append(switched_label)



    sims_per_label = run_combi.tot_same_repeats
    unordered_df = list_to_df(data, labels, sims_per_label)
    return unordered_df


def make_2d_list_1d(in_list):
    out_list = []
    for sub_list in in_list:
        for en in sub_list:
            out_list.append(en)
    return out_list


def extract_isings(run_combi, runs_name):
    path = 'save/{}/{}/'.format(runs_name, run_combi.subfolder)
    both_repeat_isings = all_files_in(path, 'repeat_isings')
    if len(both_repeat_isings) != 2:
        raise Exception('Found more than two folders that include "repeat_isings" in {}'.format(path))
    for repeat_isings in both_repeat_isings:
        if 'switched' in repeat_isings:
            path_switched_repeat_isings = repeat_isings
        elif 'same' in repeat_isings:
            path_same_repeat_isings = repeat_isings
    switched_repeat_isings = load_isings_specific_path(path_switched_repeat_isings)
    same_repeat_isings = load_isings_specific_path(path_same_repeat_isings)

    return switched_repeat_isings, same_repeat_isings#


def all_files_in(path, sub_str):
    '''
    Returns directories of all files in folder and sub-folders of path including sub_str
    '''
    #filenames = []
    files = []
    # r=root, d=directories, f=files
    for r, d, f in os.walk(path):
        for dir in d:
            if sub_str in dir:
                files.append(os.path.join(r, dir))
    return files
    # for filename in glob.iglob(path + '**/*', recursive=True):
    #     if sub_str in filename:
    #         filenames.append(filename)
    # return filenames



def reorder_df(df, new_order_labels):
    old_cols = df.columns.tolist()
    new_cols = []
    for new_label in new_order_labels:
        for old_col in old_cols:
            if new_label in old_col:
                new_cols.append(old_col)
    df_new = copy.deepcopy(df)
    df_new = df_new[new_cols]
    return df_new

def list_to_df(all_data, labels, sims_per_label=4):
    # all_data = np.array([np.array(data) for data in all_data])
    # all_data = np.asarray(all_data)
    # all_data = np.stack(all_data, axis=0)
    df = pd.DataFrame(all_data, index=labels)
    df = df.transpose()
    return df
