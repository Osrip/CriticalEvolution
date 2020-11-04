import os
from multiprocessing import Pool
import argparse
import train
import copy
from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import load_settings
from automatic_plot_helper import all_sim_names_in_parallel_folder
import time
import ray
from switch_season_repeat_plotting import plot_pipeline
import pickle
from run_combi import RunCombi
import numpy as np


def dynamic_pipeline_all_sims(folder_names, pipeline_settings):
    for folder_name in folder_names:
        sim_names = all_sim_names_in_parallel_folder(folder_name)
        for i, sim_name in enumerate(sim_names):
            if pipeline_settings['only_plot_certain_num_of_simulations'] is None:
                dynamic_pipeline_one_sim(sim_name, pipeline_settings)
            elif pipeline_settings['only_plot_certain_num_of_simulations'] > i:
                dynamic_pipeline_one_sim(sim_name, pipeline_settings)


def dynamic_pipeline_one_sim(sim_name, pipeline_settings):

    original_settings = load_settings(sim_name)
    settings = create_settings_for_repeat(original_settings, sim_name, pipeline_settings)
    run_all_repeats(settings, original_settings, pipeline_settings)


def create_settings_for_repeat(settings, sim_name, pipeline_settings):
    # settings['TimeSteps'] = 5

    settings['random_food_seasons'] = False
    settings = copy.deepcopy(settings)

    complete_sim_folder = sim_name
    settings['loadfile'] = complete_sim_folder

    if pipeline_settings['load_last_generation']:
        settings['iter'] = detect_all_isings(complete_sim_folder)[-1]
    else:
        settings['iter'] = pipeline_settings['load_generation']
    settings['LoadIsings'] = True
    settings['switch_off_evolution'] = True
    settings['save_data'] = False
    settings['switch_seasons_repeat_pipeline'] = True
    settings['dynamic_range_pipeline'] = True
    # Animations:
    settings['plot_generations'] = pipeline_settings['animation_for_repeats']
    settings['repeat_pipeline_switched_boo'] = None
    settings['random_time_steps_power_law'] = False
    settings['commands_in_folder_name'] = False
    settings['plot_pipeline'] = False
    # switches off animation:
    settings['plot'] = False

    return settings


def run_all_repeats(settings, original_settings, pipeline_settings):
    if not original_settings['random_food_seasons']:
        original_mean_food_num = settings['food_num']
    else:
        original_mean_food_num = (settings['rand_food_season_limits'][0] + settings['rand_food_season_limits'][1]) / 2
    lowest_food_num = original_mean_food_num * (pipeline_settings['lowest_food_percent'] / 100.0)
    if lowest_food_num == 0:
        lowest_food_num = 1
    highest_food_num = original_mean_food_num * (pipeline_settings['highest_food_percent'] / 100.0)
    resolution = pipeline_settings['resolution']

    food_num_arr = np.linspace(lowest_food_num, highest_food_num, resolution).astype(int)
    np.append(food_num_arr, original_mean_food_num)

    ray.init(num_cpus=pipeline_settings['cores'])
    ray_funcs = [run_repeat.remote(food_num, settings, pipeline_settings) for food_num in food_num_arr]
    ray.get(ray_funcs)
    ray.shutdown()
    # run_repeat(20, settings, pipeline_settings)

@ray.remote
def run_repeat(num_foods, settings, pipeline_settings):

    settings['food_num'] = num_foods
    settings['dynamic_range_pipeline_save_name'] = '{}dynamic_range_run_foods_{}'.format(pipeline_settings['add_save_file_name'], num_foods)
    Iterations = pipeline_settings['num_repeats']
    train.run(settings, Iterations)


if __name__=='__main__':
    '''
    BETTER NAME: FOOD DENSITY RESPONSE CURVE
    This module explores the dynamic range of random food simulations: 
    It expects a file with with random food season parameter active
    It then takes the last generation of that simulation and puts it into different environments with fixed amount of 
    foods. There the organisms do not evolve but the experiment is repeated from scratch a given amount of times, which
    is defined by "num_repeats" to get statistically meaningful results.
    Cores should be about equal to the resolution, which should also be int
    '''

    pipeline_settings = {}
    pipeline_settings['cores'] = 50
    pipeline_settings['num_repeats'] = 1
    pipeline_settings['lowest_food_percent'] = 1
    pipeline_settings['highest_food_percent'] = 1000
    pipeline_settings['resolution'] = 50
    pipeline_settings['add_save_file_name'] = 'first_try_'
    # list of repeats, that should be animated, keep in mind, that this Creates an animation for each REPEAT!
    # If no animations, just emtpy list, if an animation should be created f.e. [0]
    pipeline_settings['animation_for_repeats'] = []
    # This loads last / highest generation from trained simulation
    pipeline_settings['load_last_generation'] = True
    # Otherwise specify generation, that shall be loaded, make sure thsi generation exists in all loaded simulations:
    pipeline_settings['load_generation'] = 100
    # The following command allows to only plot a certain number of simulations in each parallel simulations folder
    # If all simulations in those folders shall be plotted, set to None
    pipeline_settings['only_plot_certain_num_of_simulations'] = None
    folder_names = ['sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000_COPY_load_generation_100']
    dynamic_pipeline_all_sims(folder_names, pipeline_settings)
