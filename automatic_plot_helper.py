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
    settings = pickle.load(open(curdir + load_settings, 'rb'))
    return settings

def load_isings(loadfile, wait_for_memory = True):
    '''
    Load all isings pickle files and return them as list
    :param loadfile : simulation name
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

        isings_list.append(isings)
    return isings_list

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

def load_isings_from_list(loadfile, iter_list, wait_for_memory = True):
    '''
    Load isings pickle files specified in iter_list and return them as list
    :param loadfile : simulation name
    :param iter_list : list of ints
    '''
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
            isings = pickle.load(open(filename, 'rb'))
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
        exec('attribute_list.append(I.{})'.format(attribute))

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
        warnings.warn("Your system's total memory is not sufficient to load in isings file. Attempting it anyways hoping for enough swap")
    else:
        waited_seconds = 0
        while available_memory < size_isings_folder:
            time.sleep(10)
            waited_seconds += 10
            if waited_seconds > 1200:
                warnings.warn('''After 20 minutes there is still not enough memory available for plotting,
                 trying to plot now anyways hoping for enough swap space.''')
                break






