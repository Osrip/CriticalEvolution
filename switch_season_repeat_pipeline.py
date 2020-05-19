import os
from multiprocessing import Pool
import argparse
import train

processes = ('-g 5 -t 200', '-g 20 -t 200')

def run_sim_and_create_repeats():
    settings, Iterations = train.create_settings()
    sim_name = train.run(settings)

def create_repeats(sim_name):
    pool = Pool(processes=2)
    pool.map(_run_process, processes)

def _run_process(process, settings):
    #os.system('python3 train {}'.format(process))
    settings['loadfile'] = sim_name
    settings['iter'] =
    train.run(settings)





#TODO: Wie übergebe ich settings/ argumente an die repeat simulationen und ändere dabei auch noch einige settings ( z.B. seasons)?

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='commands', help='''Commands that are passed to evolution simulation''')
    args = parser.parse_args()
    return args