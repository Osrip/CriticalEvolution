import os
from multiprocessing import Pool
import argparse
import train
import copy
from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import load_settings
import time
import ray
from switch_season_repeat_plotting import plot_pipeline
import pickle
from run_combi import RunCombi
import numpy as np

def dynamic_pipeline(sim_name, pipeline_settings):

    settings = load_settings(sim_name)
    settings = create_settings_for_repeat(settings, sim_name, pipeline_settings)
    run_all_repeats(settings, pipeline_settings)

def create_settings_for_repeat(settings, sim_name, pipeline_settings):
    # settings['TimeSteps'] = 5

    settings['random_time_steps'] = False
    # settings['random_food_seasons'] = False
    settings = copy.deepcopy(settings)

    complete_sim_folder = sim_name
    settings['loadfile'] = complete_sim_folder

    settings['iter'] = detect_all_isings(complete_sim_folder)[-1]
    settings['LoadIsings'] = True
    settings['switch_off_evolution'] = True
    settings['save_data'] = False
    settings['switch_seasons_repeat_pipeline'] = True
    settings['dynamic_range_pipeline'] = True
    # Animations:
    settings['plot_generations'] = [1]
    settings['repeat_pipeline_switched_boo'] = None
    settings['commands_in_folder_name'] = False
    settings['plot_pipeline'] = False
    # switches off animation:
    settings['plot'] = False

    return settings


def run_all_repeats(settings, pipeline_settings):
    lowest_food_num = pipeline_settings['lowest_ts']
    highest_food_num = pipeline_settings['highest_ts']
    resolution = pipeline_settings['resolution']

    ts_arr = np.linspace(lowest_food_num, highest_food_num, resolution).astype(int)

    ray.init(num_cpus=pipeline_settings['cores'])
    ray_funcs = [run_repeat.remote(time_steps, settings, pipeline_settings) for time_steps in ts_arr]
    ray.get(ray_funcs)
    # run_repeat(20, settings, pipeline_settings)

@ray.remote
def run_repeat(time_steps, settings, pipeline_settings):

    settings['TimeSteps'] = time_steps
    settings['dynamic_range_pipeline_save_name'] = 'dynamic_range_run_time_step_{}'.format(time_steps)
    Iterations = pipeline_settings['num_repeats']
    train.run(settings, Iterations)


if __name__=='__main__':
    '''
    This module explores the dynamic range of random food simulations: 
    It expects a file with with random food season parameter active
    It then takes the last generation of that simulation and puts it into different environments with fixed amount of 
    foods. There the organisms do not evolve but the experiment is repeated from scratch a given amount of times, which
    is defined by "num_repeats" to get statistically meaningful results.
    Cores should be about equal to the resolution, which should also be int
    '''
    sim_name = 'sim-20201003-000440-g_4000_-t_4000_-rec_c_1000_-c_props_100_50_-2_2_100_40_-iso_-ref_1000_-c_4_-a_1000_2000_3999_-no_trace_-n_different_betas_4000_fixed_ts_2_COMPARE'
    pipeline_settings = {}
    pipeline_settings['cores'] = 18
    pipeline_settings['num_repeats'] = 1
    pipeline_settings['lowest_ts'] = 1
    pipeline_settings['highest_ts'] = 50
    pipeline_settings['resolution'] = 3
    dynamic_pipeline(sim_name, pipeline_settings)
