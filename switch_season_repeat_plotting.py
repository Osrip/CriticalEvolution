import os
import numpy as np
from automatic_plot_helper import load_isings_specific_path


def plot(run_combis):
    df = create_df(run_combis)
    # TODO: Create plotting functions

def create_df(run_combis):
    for run_combi in run_combis:
        switched_repeat_isings, same_repeat_isings = extract_isings(run_combi)
        # TODO: Finish to make dataframe


def extract_isings(run_combi):
    path = '{}/'.format(run_combi.subfolder())
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
    files = []
    # r=root, d=directories, f=files
    for r, d, f in os.walk(path):
        for file in f:
            if sub_str in file:
                files.append(os.path.join(r, file))
    return files
