from os import listdir
from os.path import isfile, join
import os
import sys
import numpy as np
import pickle
import psutil
from pathlib import Path
import time
import warnings
import operator

'''
This is a library with useful functions to load ising objects and extract information from them.
'''


def detect_all_isings(sim_name):
    '''
    Creates iter_list
    detects the ising generations in the isings folder
    '''
    curdir = os.getcwd()
    mypath = curdir + '/save/{}/isings/'.format(sim_name)
    all_isings = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('isings.pickle')]
    gen_nums = []
    for name in all_isings:
        i_begin = name.find('[') + 1
        i_end = name.find(']')
        gen_nums.append(int(name[i_begin:i_end]))
    gen_nums = np.sort(gen_nums)
    return gen_nums


def load_settings(loadfile):
    '''
    load settings from loadfile
    :param loadfile: simulation name
    '''
    curdir = os.getcwd()
    load_settings = '/save/{}/settings.pickle'.format(loadfile)
    file = open(curdir + load_settings, 'rb')
    settings = pickle.load(file)
    file.close()

    return settings


def load_isings_attr(loadfile, attr):
    '''
    Load all isings attributes from pickle files and return them as nested list
    :param loadfile : simulation name
    :param attr attriobute to load
    '''


    iter_list = detect_all_isings(loadfile)
    settings = load_settings(loadfile)
    numAgents = settings['pop_size']
    attrs_list = []
    for ii, iter in enumerate(iter_list):
        filename = 'save/' + loadfile + '/isings/gen[' + str(iter) + ']-isings.pickle'
        startstr = 'Loading simulation:' + filename
        print(startstr)

        try:
            file = open(filename, 'rb')
            attrs = attribute_from_isings(pickle.load(file), attr)
            file.close()
        except Exception:
            print("Error while loading %s. Skipped file" % filename)
            # Leads to the previous datapoint being drawn twice!!

        attrs_list.append(attrs)
    return attrs_list


def load_multiple_isings_attrs(loadfile, attr_names):
    '''
    :@param attrs List of all attribute names that should be loaded
    Load all isings attributes from pickle files and return them as nested list
    :param loadfile : simulation name
    returns list. which contains dict of attributes lists for each generation
    '''


    iter_list = detect_all_isings(loadfile)
    settings = load_settings(loadfile)
    numAgents = settings['pop_size']
    attrs_list = []
    for ii, iter in enumerate(iter_list):
        filename = 'save/' + loadfile + '/isings/gen[' + str(iter) + ']-isings.pickle'
        startstr = 'Loading simulation:' + filename
        print(startstr)

        try:
            diff_attr_names_one_gen = {}
            for attr_name in attr_names:
                file = open(filename, 'rb')
                attr_vals = attribute_from_isings(pickle.load(file), attr_name)
                diff_attr_names_one_gen[attr_name] = attr_vals
                file.close()
        except Exception:
            print("Error while loading %s. Skipped file" % filename)
            # Leads to the previous datapoint being drawn twice!!

        attrs_list.append(diff_attr_names_one_gen)
    return attrs_list


def load_isings(loadfile, wait_for_memory = True):
    '''
    Load all isings pickle files and return them as list
    :param loadfile : simulation name
    '''
    if wait_for_memory:
        wait_for_enough_memory(loadfile)
        print('Not enough memory to load in isings files. \nWaiting for memory free before loading isings files... '
              '\nIf within a randomly chosen amount of time there is not enough memory will attempt loading them '
              'anyways')

    iter_list = detect_all_isings(loadfile)
    settings = load_settings(loadfile)
    numAgents = settings['pop_size']
    isings_list = []
    for ii, iter in enumerate(iter_list):
        filename = 'save/' + loadfile + '/isings/gen[' + str(iter) + ']-isings.pickle'
        startstr = 'Loading simulation:' + filename
        print(startstr)

        try:
            file = open(filename, 'rb')
            isings = pickle.load(file)
            file.close()
        except Exception:
            print("Error while loading %s. Skipped file" % filename)
            # Leads to the previous datapoint being drawn twice!!

        isings_list.append(isings)
    return isings_list

def load_top_isings(loadfile, first_n_isings, wait_for_memory = False):
    '''
    Load all isings pickle files and return them as list
    :param loadfile : simulation name
    first_n_isings: for each generation only load the top n isings (top 20 are those that were fittest and survived from prev generation)
    '''
    if wait_for_memory:
        wait_for_enough_memory(loadfile)


    iter_list = detect_all_isings(loadfile)
    settings = load_settings(loadfile)
    numAgents = settings['pop_size']
    isings_list = []
    for ii, iter in enumerate(iter_list):
        filename = 'save/' + loadfile + '/isings/gen[' + str(iter) + ']-isings.pickle'
        startstr = 'Loading simulation:' + filename
        print(startstr)

        try:
            file = open(filename, 'rb')
            isings = pickle.load(file)
            file.close()
        except Exception:
            print("Error while loading %s. Skipped file" % filename)
            # Leads to the previous datapoint being drawn twice!!

        isings_top = isings[:first_n_isings]
        isings_list.append(isings_top)
    return isings_list

def load_top_isings_attr(loadfile, first_n_isings, attr, wait_for_memory = False):
    '''
    Load all isings pickle files and return them as list
    :param loadfile : simulation name
    first_n_isings: for each generation only load the top n isings (top 20 are those that were fittest and survived from prev generation)
    '''
    if wait_for_memory:
        wait_for_enough_memory(loadfile)



    iter_list = detect_all_isings(loadfile)
    settings = load_settings(loadfile)
    numAgents = settings['pop_size']
    isings_attr_list = []
    for ii, iter in enumerate(iter_list):
        filename = 'save/' + loadfile + '/isings/gen[' + str(iter) + ']-isings.pickle'
        startstr = 'Loading simulation:' + filename
        print(startstr)

        try:
            file = open(filename, 'rb')
            isings = pickle.load(file)
            isings_attribute = attribute_from_isings(isings, attr)
            del isings
            file.close()
        except Exception:
            print("Error while loading %s. Skipped file" % filename)
            # Leads to the previous datapoint being drawn twice!!

        isings_attr_top = isings_attribute[:first_n_isings]
        isings_attr_list.append(isings_attr_top)
    return isings_attr_list

def load_isings_specific_path(isings_path):
    '''
    Load all isings pickle files from a specific isings folder (when they are not normally stored and return them as list
    :param isings_path : specific path to folder that ising objects are saved in
    '''

    iter_list = detect_all_isings_specific_path(isings_path)

    isings_list = []
    for ii, iter in enumerate(iter_list):
        filename = isings_path + '/gen[' + str(iter) + ']-isings.pickle'
        startstr = 'Loading simulation:' + filename
        print(startstr)

        try:
            file = open(filename, 'rb')
            isings = pickle.load(file)
            file.close()
        except Exception:
            print("Error while loading %s. Skipped file" % filename)
            # Leads to the previous datapoint being drawn twice!!

        isings_list.append(isings)
    return isings_list


def detect_all_isings_specific_path(isings_path):
    '''
    Creates iter_list
    detects the ising generations in the isings folder
    :param isings_path : specific path to folder that ising objects are saved in
    '''
    curdir = os.getcwd()
    mypath = curdir + '/{}/'.format(isings_path)
    all_isings = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('isings.pickle')]
    gen_nums = []
    for name in all_isings:
        i_begin = name.find('[') + 1
        i_end = name.find(']')
        gen_nums.append(int(name[i_begin:i_end]))
    gen_nums = np.sort(gen_nums)
    return gen_nums


def load_isings_from_list(loadfile, iter_list, wait_for_memory = False):
    '''
    Load isings pickle files specified in iter_list and return them as list
    :param loadfile : simulation name
    :param iter_list : list of ints specifying generations to load isings from
    741'''
    if wait_for_memory:
        wait_for_enough_memory(loadfile)

    settings = load_settings(loadfile)
    numAgents = settings['pop_size']
    isings_list = []
    for ii, iter in enumerate(iter_list):
        filename = 'save/' + loadfile + '/isings/gen[' + str(iter) + ']-isings.pickle'
        startstr = 'Loading simulation:' + filename
        print(startstr)

        try:
            file = open(filename, 'rb')
            isings = pickle.load(file)
            file.close()
        except Exception:
            print("Error while loading %s. Skipped file" % filename)
            # Leads to the previous datapoint being drawn twice!!

        isings_list.append(isings)
    return isings_list


def list_to_blank_seperated_str(list):
    out_str = ''
    for en in list:
        out_str += str(en) + ' '
    out_str = out_str[:-1]
    return out_str


def load_isings_attributes_from_list(loadfile, iter_list, attribute):
    # TODO: FIX MEMORY LEAK
    '''
    Load isings pickle files specified in iter_list and return them as list
    :param loadfile : simulation name
    :param iter_list : list of ints
    :param attribute


    '''
    settings = load_settings(loadfile)
    numAgents = settings['pop_size']
    isings_attribute_list = []

    # list including all differnet properties in lists

    for ii, iter in enumerate(iter_list):
        filename = 'save/' + loadfile + '/isings/gen[' + str(iter) + ']-isings.pickle'
        startstr = 'Loading simulation:' + filename
        print(startstr)

        try:
            # TODO: THIs     still has shitty open function with MEMORY LEAK!!!!!!!
            file = open(filename, 'rb')
            isings = pickle.load(file)
            file.close()
        except Exception:
            print("Error while loading %s. Skipped file" % filename)
            # Leads to the previous datapoint being drawn twice!!

        isings_attribute_list.append(attribute_from_isings(isings, attribute))

    return isings_attribute_list


def attribute_from_isings(isings, attribute):
    '''
    Returns a list of attributes (numerated by organisms) from isings list (Only one generation!!! in isings)
    '''

    #attribute_list = [exec('I.{}'.format(attribute)) for I in isings]
    #exec('attribute_list = [I.{} for I in isings]'.format(attribute))
    attribute_list = []
    for I in isings:
        # Added the if else statement afterwards, so remove this in case it throws an error at some point!
        exec('attribute_list.append(I.{})'.format(attribute))
        # if I is not None:
        #     exec('attribute_list.append(I.{})'.format(attribute))
        # else:
        #     attribute_list.append(np.nan)

    return attribute_list


def wait_for_enough_memory(sim_name):
    '''
    Stops program until enough memory is available to load in all ising files
    '''

    root_directory = Path('save/{}/isings'.format(sim_name))
    size_isings_folder = sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())

    memory_data = psutil.virtual_memory()
    available_memory = memory_data.available
    total_system_memory = memory_data.active

    if total_system_memory < size_isings_folder:
        warnings.warn("Your system's total (not currently free) memory is not sufficient to load in isings file. Attempting it anyways hoping for enough swap")
    else:
        waited_seconds = 0
        # Randomize max waited seconds, to make it unlikely for two parallely waiting processes writing onto swap at the same time
        max_waited_seconds = np.random.randint(1200, 3600)
        while available_memory < size_isings_folder:
            print('Not enough memory to load in isings files. \nWaiting for memory to be free before loading isings files... '
                  '\nIf within {} seconds chosen amount of time there is not enough memory will attempt loading them '
                  'anyways'.format(max_waited_seconds-waited_seconds))
            time.sleep(10)
            waited_seconds += 10
            if waited_seconds > max_waited_seconds:
                warnings.warn('''After {} seconds there is still not enough memory available for plotting,
                 trying to plot now anyways hoping for enough swap space.'''.format(max_waited_seconds))
                break

# OLD FUNCTION:
# def all_folders_in_dir_with(dir, including_name):
#     directory_list = list()
#     for root, dirs, files in os.walk(dir, topdown=False):
#         for name in dirs:
#             if including_name in name:
#                 directory_list.append(os.path.join(root, name))
#     return directory_list

def all_folders_in_dir_with(dir, including_name):
    '''
    Lists all subfolders (also subsubfolders, subsubsubfolders, ...)
    including name can either be list of str or list
    Returns directory of all folders with including_name in the folder name
    or if including name is a list with all strings specified in the list in the folder name
    '''
    if type(including_name) == str:
        directory_list = list()
        for root, dirs, files in os.walk(dir, topdown=False):
            for name in dirs:
                if including_name in name:
                    directory_list.append(os.path.join(root, name))
    elif type(including_name) == list:
        including_names = including_name
        directory_list = list()
        for root, dirs, files in os.walk(dir, topdown=False):
            for name in dirs:
                boo_list = []
                for including_name in including_names:
                    boo_list.append(including_name in name)
                if all(boo_list):
                    directory_list.append(os.path.join(root, name))

    return directory_list


def subfolders_in_folder(dir, inluding_strs):
    '''
    Lists all immediate subfolders (not subsubfolders) in dir, that include all strings specified in list including strs
    @return: directories of these subfolders
    '''
    # next(os.walk('.'))[1]
    # subdirs = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]

    sub_folder_dirs = []
    sub_folder_names = []
    for folder_name in os.listdir(dir):
        folder_dir = os.path.join(dir, folder_name)
        boo_list = []
        for including_str in inluding_strs:
            boo_list.append(including_str in folder_name)
        if all(boo_list) and os.path.isdir(folder_dir):
            sub_folder_dirs.append(folder_dir)
            # sub_folder_names.append(folder_name)

    return sub_folder_dirs


def choose_copied_isings(isings):
    '''
    This function chooses only those ising objects, which have been copied by the Evolutionary Algorithm in the previous generation

    '''

    isings_new = [I for I in isings if I.prev_mutation == 'copy']
    # For the initial population just choose 20 "random" organims instead
    if isings_new == [] and all([I.prev_mutation == 'init' for I in isings]):
        isings_new = isings[0:20]
        # isings_new = sorted(isings, key=operator.attrgetter('avg_energy'), reverse=True)[0:19]
    return isings_new


def calc_normalized_fitness(isings_list, plot_settings, sim_settings):
    '''
    This function calculates two normalized fitness / avg_energy values, that are not in the ising object by default

    '''
    for isings in isings_list:
        for I in isings:
            I.norm_avg_energy = I.avg_energy / I.time_steps


    if plot_settings['attr'] == 'norm_food_and_ts_avg_energy':
        if sim_settings['random_food_seasons']:
            for isings in isings_list:
                for I in isings:
                    I.norm_food_and_ts_avg_energy = I.norm_avg_energy / I.food_in_env
        else:
            food_num = sim_settings['food_num']
            for isings in isings_list:
                for I in isings:
                    I.norm_food_and_ts_avg_energy = I.norm_avg_energy / food_num


def all_sim_names_in_parallel_folder(folder_name):
    '''
    This function returns all simulation names within a given folder
    @param folder_name: Folder name of folder with all simulations, whose names should be returned
    '''

    folder_dir = 'save/{}'.format(folder_name)
    dir_list = all_folders_in_dir_with(folder_dir, 'sim')
    sim_name_list = []
    for dir in dir_list:
        sim_name = dir[(dir.rfind('save/')+5):]
        sim_name_list.append(sim_name)
    return sim_name_list
