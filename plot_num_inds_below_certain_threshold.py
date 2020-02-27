import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg') #For server use
from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import load_settings
from automatic_plot_helper import load_isings

def how_many_below_min_velocity(settings, isings):
    amount = 0
    for I in isings:
        if I.v



def plot(sim_name, settings, isings_list):

    folder = 'save/' + sim_name
    folder2 = folder + '/figs/' + 'individuals_below_min_velocity' + '/'


if __name__ == '__main__':
    sim_name =
    isings_list = load_isings(sim_name)
    settings = load_settings(sim_name)
    plot(sim_name, settings, isings_list)