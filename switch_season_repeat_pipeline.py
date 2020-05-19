import os
from multiprocessing import Pool
import argparse
import train
from automatic_plot_helper import detect_all_isings
processes = ('-g 5 -t 200', '-g 20 -t 200')

def run_sim_and_create_repeats():
    settings, Iterations = train.create_settings()
    sim_name = train.run(settings, Iterations)
    create_repeats(sim_name, settings)

def create_repeats(sim_name, settings):
    settings['loadfile'] = sim_name
    settings['iter'] = detect_all_isings(sim_name)[-1]
    settings['switch_off_evolution'] = True
    settings['save_data'] = False
    settings['switch_seasons_repeat_pipeline'] = True


    #  Number of repeats
    #Iterations = 200
    Iterations = 5

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
    run_sim_and_create_repeats()