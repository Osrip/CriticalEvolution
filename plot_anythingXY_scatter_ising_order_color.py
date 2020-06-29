#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg') #For server use
from matplotlib import colors
from matplotlib.lines import Line2D
from matplotlib.patches import Circle
import pickle
from os import makedirs, path
from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import load_settings
from automatic_plot_helper import load_isings
import os
import sys
'''
loadfiles = ['beta_experiment/beta-0-1/sim-20180512-105719',
             'beta_experiment/beta-1/sim-20180511-163319',
             'beta_experiment/beta-10/sim-20180512-105824']
'''


def main(loadfile, settings, isings_list, plot_var_x, plot_var_y, s=0.8, alpha=0.13, autoLoad=True, x_lim=None,
         y_lim=None, xlog=False, ylog=False, y_noise=False, name_extension=''):


    loadfiles = [loadfile]#loadfiles = ['sim-20191114-000009_server']
    iter_list = detect_all_isings(loadfile) #  iter_list = np.arange(0, 2000, 1)
    #
    energy_model = settings['energy_model']
    numAgents = settings['pop_size']
    #autoLoad = True
    saveFigBool = True
    fixGen2000 = False
    plot_first = 20

    new_order = [2, 0, 1]

    labels = [r'$\beta_i = 0.1$', r'$\beta_i = 1$', r'$\_i = 10$']


    norm = colors.Normalize(vmin=0, vmax=len(loadfiles))  # age/color mapping
    # norm = [[194, 48, 32, 255],
    #         [146, 49, 182, 255],
    #         [44, 112, 147, 255]
    #         ]
    # norm = np.divide(norm, 255)
    a = 0.15 # alpha

    color1 = 'green'
    color2 = 'red'

    isings_list_1 = []
    isings_list_2 = []
    for isings in isings_list:
        isings_list_1.append(isings[:plot_first])
        isings_list_2.append(isings[plot_first:])

    x_pars_list1, y_pars_list1 = fitness(loadfile, iter_list, isings_list_1, len(isings_list_1[0]), autoLoad, saveFigBool, plot_var_x,
                                       plot_var_y)
    x_pars_list2, y_pars_list2 = fitness(loadfile, iter_list, isings_list_2, len(isings_list_2[0]), autoLoad, saveFigBool, plot_var_x,
                                         plot_var_y)


    #fig, ax = plt.subplots()
    cmap = plt.get_cmap('plasma')
    norm = colors.Normalize(vmin=0, vmax=len(iter_list))
    font = {'family': 'normal',
            'weight': 'bold',
            'size': 10}

    plt.rc('font', **font)
    plt.figure()


    plot(x_pars_list2, y_pars_list2, iter_list, s, alpha, color2, xlog, ylog, y_noise, y_lim, x_lim, name_extension,
         saveFigBool, label='Mutated')

    plot(x_pars_list1, y_pars_list1, iter_list, s, alpha, color1, xlog, ylog, y_noise, y_lim, x_lim, name_extension,
         saveFigBool, label='Fittest from last generation ')


    plt.xlim(x_lim)
    plt.ylim(y_lim)
    plt.xlabel('{}'.format(plot_var_x.replace('_', ' ')))
    plt.ylabel('{}'.format(plot_var_y.replace('_', ' ')))
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Fittest/Selected of last generation', markerfacecolor='green',
               markersize= 5, alpha=0.75),
        Line2D([0], [0], marker='o', color='w', label='Mutated', markerfacecolor='red',
               markersize= 5, alpha=0.75)
    ]

    plt.legend(handles=legend_elements)# loc="lower right", bbox_to_anchor=(0.95, 0.05),

    folder = 'save/' + loadfile
    savefolder = folder + '/figs/' + plot_var_x + '_vs_' + plot_var_y + '_ising_order_color_line/'
    savefilename = savefolder + plot_var_x + '_vs_' + plot_var_y + '_gen' + str(iter_list[0]) + '-' + str(
        iter_list[-1]) + name_extension + '.png'
    if not path.exists(savefolder):
        makedirs(savefolder)

    if saveFigBool:
        plt.savefig(savefilename, bbox_inches='tight', dpi=300)

    plt.show()
    #  Trying to fix memory leak with this:
    plt.cla()
    plt.clf()
    plt.close('all')


def plot(x_pars_list, y_pars_list, iter_list, s, alpha, color, xlog, ylog, y_noise, y_lim, x_lim, name_extension,
         saveFigBool, label):

    for gen, (x_pars, y_pars) in enumerate(zip(x_pars_list, y_pars_list)):
        #c = cmap(norm(gen))

        if y_noise:
            y_pars = y_pars.astype(float)
            y_pars = y_pars + np.random.rand(np.shape(y_pars)[0]) - 0.5
        ax = plt.scatter(x_pars, y_pars, s=s, alpha=alpha, c=color, label=label)
        if y_noise:
            plt.ylim(1, 1000)
        if xlog:
            plt.xscale('log')
        if ylog:
            plt.yscale('log')
        #TODO:colour acc to generation!!


def upper_tri_masking(A):
    m = A.shape[0]
    r = np.arange(m)
    mask = r[:, None] < r
    return A[mask]

def fitness(loadfile, iter_list, isings_list, numAgents, autoLoad, saveFigBool, plot_var_x, plot_var_y):

    folder = 'save/' + loadfile

    folder2 = folder + '/figs/' + plot_var_x + '_vs_'+ plot_var_y + '/'
    fname2 = folder2 + plot_var_x + '_vs_'+ plot_var_y + \
             str(iter_list[0]) + '-' + str(iter_list[1] - iter_list[0]) + '-' + str(iter_list[-1]) + \
             '.npz'

    # if path.isfile(fname2) and autoLoad:
    #     txt = 'Loading: ' + fname2
    #     print(txt)
    #     data = np.load(fname2)
    #     FOOD = data['FOOD']
    if path.isfile(fname2) and autoLoad:
        #Loading previously saved files
        txt = 'Loading: ' + fname2
        print(txt)
        data = np.load(fname2)
        x_pars_list = data['x_pars_list']
        y_pars_list = data['y_pars_list']
    else:
        #Loading directly from isings_list in case it has been passed
        x_pars_list = np.zeros((len(iter_list), numAgents))
        y_pars_list = np.zeros((len(iter_list), numAgents))
        for ii, isings in enumerate(isings_list):
            x_pars = []
            y_pars = []
            for i, I in enumerate(isings):
                exec('x_pars.append(I.%s)' % plot_var_x)
                exec('y_pars.append(I.%s)' % plot_var_y)
            x_pars_list[ii, :] = x_pars
            y_pars_list[ii, :] = y_pars
        if not path.exists(folder2):
            makedirs(folder2)
        np.savez(fname2, x_pars_list=x_pars_list)
    return x_pars_list, y_pars_list


if __name__ == '__main__':
    loadfile = 'Energies_Velocities_saved_during_2d_sim_random_time_steps_cut_off_animations/sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved' #sim-20200604-235424-g_2000_-t_2000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved
    loadfile = 'Energies_Velocities_saved_during_2d_sim_random_time_steps_cut_off_animations/sim-20200604-235424-g_2000_-t_2000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    #loadfile = 'Energies_Velocities_saved_during_2d_sim_random_time_steps_cut_off_animations/test_dataset_random_ts'
    plot_var_x = 'generation'
    plot_var_y = 'avg_energy'#'food'
    isings_list = load_isings(loadfile)
    settings = load_settings(loadfile)
    #TODO: add something that detetcts .npz file and skips loading isings in that case

    main(loadfile, settings, isings_list, plot_var_x, plot_var_y, autoLoad=False, alpha=0.05)
    #TODO: Evt. PCA oder decision trees um herauszufinden welche eigenschaften wichtig sind fuer hohe avg energy?

