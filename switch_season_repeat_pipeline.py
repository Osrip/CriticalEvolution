import os
from multiprocessing import Pool
import argparse
import train
import copy
from automatic_plot_helper import detect_all_isings
import time
import ray
from switch_season_repeat_plotting import plot_pipeline
import pickle
from run_combi import RunCombi
processes = ('-g 5 -t 200', '-g 20 -t 200')




def main(num_repeats, same_repeats, food_summer, food_winter, folder_add):

    folder_add = 'num_rep_{}_same_rep_{}_f_sum_{}_f_win{}_{}'.format(num_repeats, same_repeats, food_summer, food_winter
                                                                     , folder_add)

    run_combis, first_subfolder = run_all_combinations(num_repeats, same_repeats, food_summer, food_winter, folder_add)
    plot_pipeline(run_combis, first_subfolder, 'avg_energy')


def run_all_combinations(num_repeats, same_repeats, food_summer, food_winter, folder_add):
    '''
    main function for running simulations
    num_repeats: the number of times last generation is repeated
    same_repeats: Number of times the same simulation is run
    '''
    # TODO Parallelize all combinations!

    #same_repeats = 4  # Number of times the same simulation is run

    settings, Iterations = train.create_settings()
    #num_repeats = 5  # 200 # num repeats: the number of times last generation is repeated
    first_subfolder = 'switch_seasons_{}_{}'.format(time.strftime("%Y%m%d-%H%M%S"), folder_add)
    run_combis = make_combinations(settings, same_repeats, food_summer, food_winter)

    ray.init()

    ray_funcs = [run_one_combination.remote(run_combi, first_subfolder, Iterations, num_repeats, food_summer, food_winter)
                 for run_combi in run_combis]
    # ray_funcs = [run_one_combination(run_combi, first_subfolder, Iterations, num_repeats, food_summer, food_winter)
    #              for run_combi in run_combis]
    ray.get(ray_funcs)

    save_run_combis(run_combis, first_subfolder)
    return run_combis, first_subfolder

def save_run_combis(run_combis, first_subfolder):
    savefolder = 'save/{}/run_combis.pickle'.format(first_subfolder)
    pickle_out = open(savefolder, 'wb')
    pickle.dump(run_combis, pickle_out)
    pickle_out.close()



def make_combinations(settings, same_repeats, food_summer, food_winter):
    '''
    creates all combinations of runs
    same_repeats: int - Defines how many times the simulation with same parameter is "repeated"
    (for statistical significance)
    '''
    run_combis = []
    for food in [food_summer, food_winter]:
        for beta in [1, 10]:
            for repeat in range(same_repeats):
                run_combis.append(RunCombi(settings, food, beta, repeat, same_repeats, food_summer, food_winter))
    return run_combis


@ray.remote
def run_one_combination(run_combi, first_subfolder, Iterations, num_repeats, food_summer, food_winter):
    second_subfolder = run_combi.subfolder
    save_subfolder = '{}/{}'.format(first_subfolder, second_subfolder)
    settings = run_combi.settings
    settings['commands_in_folder_name'] = False
    run_sim_and_create_repeats(save_subfolder, settings, Iterations, num_repeats, food_summer, food_winter)


def run_sim_and_create_repeats(save_subfolder, settings, Iterations, num_repeats, food_summer, food_winter):
    settings['save_subfolder'] = save_subfolder

    sim_name = train.run(settings, Iterations)
    create_repeats(sim_name, save_subfolder, settings, num_repeats, food_summer, food_winter)


def create_repeats(sim_name, save_subfolder, settings, num_repeats, food_summer, food_winter):
    settings = copy.deepcopy(settings)

    complete_sim_folder = '{}/{}'.format(save_subfolder, sim_name)
    settings['loadfile'] = complete_sim_folder

    settings['iter'] = detect_all_isings(complete_sim_folder)[-1]
    settings['LoadIsings'] = True
    settings['switch_off_evolution'] = True
    settings['save_data'] = False
    settings['switch_seasons_repeat_pipeline'] = True
    # Animations:
    settings['plot_generations'] = [1]



    #  Number of repeats
    # Iterations = 200
    Iterations = num_repeats

    settings['repeat_pipeline_switched_boo'] = False
    train.run(settings, Iterations)

    #  switch seasons
    if settings['food_num'] == food_summer:
        settings['food_num'] = food_winter
    elif settings['food_num'] == food_winter:
        settings['food_num'] = food_summer


    settings['repeat_pipeline_switched_boo'] = True
    train.run(settings, Iterations)


def create_repeats_parallel(sim_name, settings):
    settings['loadfile'] = sim_name
    settings['iter'] = detect_all_isings(sim_name)[-1]
    pool = Pool(processes=2)
    pool.map(_run_process, processes)


def _run_process(process, settings):
    #os.system('python3 train {}'.format(process))

    train.run(settings)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='commands', help='''Commands that are passed to evolution simulation''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    '''
    input arguments of train.py can be passed just as usual. This way f.e. the number of time steps as well as number of
    generations in first simulation can be adjusted
    recommended:
    -g 2000 -t 2000 -dream_c 0 -nat_c 0 -ref 0 -rec_c 0
    
    The parameters below specify the pipeline specific parameters. The following parameters are recommented:
    folder_add = 'test_run'
    num_repeats = 200
    same_repeats = 4 (four times as many cores are required, so in this case 16)
    food_summer = 100
    food_winter = 10
    
    '''
    folder_add = 'test'
    num_repeats = 20
    same_repeats = 1
    food_summer = 100
    food_winter = 10

    main(num_repeats, same_repeats, food_summer, food_winter, folder_add)