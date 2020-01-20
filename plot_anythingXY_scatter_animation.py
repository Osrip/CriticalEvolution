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
import matplotlib.animation as animation
import os
import sys
'''
loadfiles = ['beta_experiment/beta-0-1/sim-20180512-105719',
             'beta_experiment/beta-1/sim-20180511-163319',
             'beta_experiment/beta-10/sim-20180512-105824']
'''
def main(loadfile, settings, isings_list, plot_var_x, plot_var_y, plot_var_c, s=0.8, alpha=0.8, autoLoad=True, x_lim=None,
         y_lim=None, log=True, y_noise=True):


    loadfiles = [loadfile]#loadfiles = ['sim-20191114-000009_server']
    iter_list = detect_all_isings(loadfile) #  iter_list = np.arange(0, 2000, 1)
    #
    energy_model = settings['energy_model']
    numAgents = settings['pop_size']

    saveFigBool = True

    if settings['server_mode']:
        plt.rcParams['animation.ffmpeg_path'] = '/data-uwks159/home/jprosi/ffmpeg-4.2.1-linux-64/ffmpeg'
        #'/usr/local/bin/ffmpeg'
    else:
        plt.rcParams['animation.ffmpeg_path'] = "D:/Program Files/ffmpeg-20191217-bd83191-win64-static/bin/ffmpeg.exe"


    new_order = [2, 0, 1]

    labels = [r'$\beta_i = 0.1$', r'$\beta_i = 1$', r'$\_i = 10$']

    cmap = plt.get_cmap('seismic')
    norm = colors.Normalize(vmin=0, vmax=len(loadfiles))  # age/color mapping
    # norm = [[194, 48, 32, 255],
    #         [146, 49, 182, 255],
    #         [44, 112, 147, 255]
    #         ]
    # norm = np.divide(norm, 255)
    a = 0.15 # alpha

    x_pars_list, y_pars_list, c_pars_list = fitness(loadfile, iter_list, isings_list, numAgents, autoLoad, saveFigBool, plot_var_x,
                                       plot_var_y, plot_var_c)
    #fig, ax = plt.subplots()

    fig = plt.figure()
    ani = animation.FuncAnimation(fig, update_plot,
                                  fargs=[x_pars_list, y_pars_list, c_pars_list], interval=1,
                                  frames=len(x_pars_list))
    Writer = animation.FFMpegFileWriter
    writer = Writer(fps=settings['animation_fps'], metadata=dict(artist='Sina Abdollahi, Jan Prosi'), bitrate=1800)
    writer.frame_format = 'png'


    folder = 'save/' + loadfile
    savefolder = folder + '/figs/' + plot_var_x + '_vs_' + plot_var_y + '_line/'
    savefilename = 'ani' + savefolder + plot_var_x + '_vs_' + plot_var_y + '_gen' + str(iter_list[0]) + '-' + str(
        iter_list[-1]) + '.mpg'

    if not path.exists(savefolder):
        makedirs(savefolder)

    if saveFigBool:
        ani.save(savefilename, writer=writer)

    plt.show()

def update_plot(f, x_pars_list, y_pars_list, c_pars_list):

    # cmap = plt.get_cmap('plasma')
    # norm = colors.Normalize(vmin=np.min(c_pars_list), vmax=np.max(c_pars_list)
    # font = {'family': 'normal',
    #         'weight': 'bold',
    #         'size': 10}
    #
    # plt.rc('font', **font)
    # c = cmap(norm(gen))
    x_pars, y_pars, c_pars = x_pars_list[f], y_pars_list[f], c_pars_list[f]
    if y_noise:
        y_pars = y_pars.astype(float)
        y_pars = y_pars + np.random.rand(np.shape(y_pars)[0]) - 0.5
    ax = plt.scatter(x_pars, y_pars, c=c_pars, s = s, alpha = alpha)
    if y_noise:
        plt.ylim(1,1000)
    if log:
        plt.xscale('log')
        plt.yscale('log')

    plt.xlim(x_lim)
    plt.ylim(y_lim)
    plt.xlabel('{}'.format(plot_var_x.replace('_', ' ')))
    plt.ylabel('{}'.format(plot_var_y.replace('_', ' ')))
def upper_tri_masking(A):
    m = A.shape[0]
    r = np.arange(m)
    mask = r[:, None] < r
    return A[mask]

def fitness(loadfile, iter_list, isings_list, numAgents, autoLoad, saveFigBool, plot_var_x, plot_var_y, plot_var_c):

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

    #Loading directly from isings_list in case it has been passed
    x_pars_list = np.zeros((len(iter_list), numAgents))
    y_pars_list = np.zeros((len(iter_list), numAgents))
    c_pars_list = np.zeros((len(iter_list), numAgents))
    for ii, isings in enumerate(isings_list):
        x_pars = []
        y_pars = []
        c_pars = []
        for i, I in enumerate(isings):
            exec('x_pars.append(I.%s)' % plot_var_x)
            exec('y_pars.append(I.%s)' % plot_var_y)
            exec('c_pars.append(I.%s)' % plot_var_c)
        x_pars_list[ii, :] = x_pars
        y_pars_list[ii, :] = y_pars
        c_pars_list[ii, :] = c_pars
    if not path.exists(folder2):
        makedirs(folder2)
    #np.savez(fname2, x_pars_list=x_pars_list)
    return x_pars_list, y_pars_list, c_pars_list
    # else:
    #     #Otherwise load file directly
    #     FOOD = np.zeros((len(iter_list), numAgents))
    #     for ii, iter in enumerate(iter_list):
    #         filename = 'save/' + loadfile + '/isings/gen[' + str(iter) + ']-isings.pickle'
    #         startstr = 'Loading simulation:' + filename
    #         print(startstr)
    #
    #         try:
    #             isings = pickle.load(open(filename, 'rb'))
    #         except Exception:
    #             print("Error while loading %s. Skipped file" % filename)
    #             #Leads to the previous datapoint being drawn twice!!
    #
    #
    #         food = []


        #     for i, I in enumerate(isings):
        #         exec('food.append(I.%s)' % plot_var)
        #
        #     # food = np.divide(food, 6)
        # x_pars_list[ii, :] = x_pars
        #
        # if not path.exists(folder2):
        #     makedirs(folder2)

        #np.savez(fname2, FOOD=x_pars_list)


if __name__ == '__main__':

    #loadfile = sys.argv[1]
    #plot_var = sys.argv[2] #plot_var = 'v'
    loadfile = 'sim-20200103-170556-ser_-s_-b_1_-ie_2_-a_0_500_1000_1500_1999'
    plot_var_x = 'avg_velocity'
    plot_var_y = 'food'#'food'
    plot_var_c = 'avg_energy'
    isings_list = load_isings(loadfile)
    settings = load_settings(loadfile)
    #TODO: add something that detetcts .npz file and skips loading isings in that case

    main(loadfile, settings, isings_list, plot_var_x, plot_var_y, plot_var_c, autoLoad=False, x_lim=(-1,20), y_lim=(-0.1, 0.8), alpha = 0.05)
    #TODO: Evt. PCA oder decision trees um herauszufinden welche eigenschaften wichtig sind für hohe avg energy?

