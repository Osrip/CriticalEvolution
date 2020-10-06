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
    settings['TimeSteps'] = 5


    settings['random_food_seasons'] = False
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
    lowest_food_num = pipeline_settings['lowest_food_num']
    highest_food_num = pipeline_settings['highest_food_num']
    resolution = pipeline_settings['resolution']

    food_num_arr = np.linspace(lowest_food_num, highest_food_num, resolution).astype(int)

    ray.init(num_cpus=pipeline_settings['cores'])
    ray_funcs = [run_repeat.remote(food_num, settings, pipeline_settings) for food_num in food_num_arr]
    ray.get(ray_funcs)
    # run_repeat(20, settings, pipeline_settings)

@ray.remote
def run_repeat(num_foods, settings, pipeline_settings):

    settings['food_num'] = num_foods
    settings['dynamic_range_pipeline_save_name'] = 'dynamic_range_run_{}_foods'.format(num_foods)
    Iterations = pipeline_settings['num_repeats']
    train.run(settings, Iterations)


if __name__=='__main__':
    sim_name = 'sim-20201005-115245-g_4000_-t_2000_-rand_seas_-rec_c_1000_-c_props_100_50_-2_2_100_40_-iso_-ref_1000_-c_4_-a_1000_1001_10002_2000_3998_3999_-no_trace_-n_different_betas_rand_seas1_TEST_COPY'
    pipeline_settings = {}
    pipeline_settings['cores'] = 15
    pipeline_settings['num_repeats'] = 4
    pipeline_settings['lowest_food_num'] = 1
    pipeline_settings['highest_food_num'] = 500
    pipeline_settings['resolution'] = 5
    dynamic_pipeline(sim_name, pipeline_settings)
