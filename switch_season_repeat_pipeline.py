import os
from multiprocessing import Pool
import argparse
import train
import copy
from automatic_plot_helper import detect_all_isings
import time
processes = ('-g 5 -t 200', '-g 20 -t 200')

class RunCombi:
    def __init__(self, settings, food, beta):
        '''
        This Class includes the properties of a certain simulation run
        '''
        settings = copy.deepcopy(settings)
        settings['food_num'] = food
        settings['init_beta'] = beta
        self.settings = settings

        if food == 10:
            season_name = 'winter'
        elif food == 100:
            season_name = 'summer'
        else:
            raise Exception('In the current impülementation of pipeline has to be either 10 or 100')


        subfolder = 'b{}_{}'.format(beta, season_name)
        self.subfolder = subfolder

def make_combinations(settings):
    '''
    creates all combinations of runs
    '''
    run_combis = []
    for beta in [0.1, 1]:
        for food in [100, 10]:
            run_combis.append(RunCombi(settings, food, beta))
    return run_combis

def run_all_combinations():
    '''
    main function
    '''
    settings, Iterations = train.create_settings()
    num_repeats = 5 #200 # num repeats: the number of times last generation is repeated
    first_subfolder = 'switch_seasons_{}'.format(time.strftime("%Y%m%d-%H%M%S"))
    run_combis = make_combinations(settings)
    for run_combi in run_combis:
        second_subfolder = run_combi.subfolder
        save_subfolder = '{}/{}'.format(first_subfolder, second_subfolder)
        settings = run_combi.settings
        run_sim_and_create_repeats(save_subfolder, settings, Iterations, num_repeats)

def run_sim_and_create_repeats(save_subfolder, settings, Iterations, num_repeats):
    settings['save_subfolder'] = save_subfolder

    sim_name = train.run(settings, Iterations)
    create_repeats(sim_name, save_subfolder, settings, num_repeats)


def create_repeats(sim_name, save_subfolder, settings, num_repeats):
    settings = copy.deepcopy(settings)
    settings['loadfile'] = sim_name
    complete_sim_folder = '{}/{}'.format(save_subfolder, sim_name)

    settings['iter'] = detect_all_isings(complete_sim_folder)[-1]
    settings['switch_off_evolution'] = True
    settings['save_data'] = False
    settings['switch_seasons_repeat_pipeline'] = True


    #  Number of repeats
    #Iterations = 200
    Iterations = num_repeats

    settings['repeat_pipeline_switched_boo'] = False
    train.run(settings, Iterations)

    #  switch seasons
    if settings['food_num'] == 100:
        settings['food_num'] = 10
    elif settings['food_num'] == 10:
        settings['food_num'] = 100


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





#TODO: Wie übergebe ich settings/ argumente an die repeat simulationen und ändere dabei auch noch einige settings ( z.B. seasons)?

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='commands', help='''Commands that are passed to evolution simulation''')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    run_all_combinations()