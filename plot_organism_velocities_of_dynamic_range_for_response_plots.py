from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import load_isings_attributes_from_list
from automatic_plot_helper import load_settings
from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import all_folders_in_dir_with
import matplotlib as mpl
mpl.use('Agg') #For server use
from automatic_plot_helper import load_isings_specific_path
from automatic_plot_helper import load_isings_specific_path_decompress
from automatic_plot_helper import choose_copied_isings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
from numba import jit
import re
import scipy.signal
from scipy import fft, arange
from scipy import fftpack
from automatic_plot_helper import all_folders_in_dir_with
import math


def main(plot_settings):
    plot_settings['number_individuals'] = 1



    label_highlighted_sims = plot_settings['label_highlighted_sims']
    custom_legend_labels = plot_settings['custom_legend_labels']
    # Making a new plot for each folder and a subplot for each dict in each include_name dict
    for folder_name in label_highlighted_sims:
        plt.figure()
        include_name_dict = label_highlighted_sims[folder_name]
        num_subplots = count_total_number_of_plots_in_folder(include_name_dict)
        num_columns = plot_settings['number_columns_in_subplot']
        num_rows = math.floor(num_subplots / num_columns)
        curr_subplot_num = 0
        for include_name in include_name_dict:
            sim_num_dict = include_name_dict[include_name]
            for sim_num in sim_num_dict:
                # Creating subplot command
                subplot_input = int('{}{}{}'.format(num_subplots,
                                                    math.floor(curr_subplot_num/2)+1,
                                                    (curr_subplot_num % 2)+1))
                plt.subplot(subplot_input)
                make_one_subplot(folder_name, include_name, sim_num, plot_settings)
                curr_subplot_num += 1

        save_path = 'save/{}/figs/energies_velocities_for_response_plot/'.format(folder_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        fig_name = 'velocities.png'
        plt.savefig('{}{}'.format(save_path, fig_name), dpi=150, bbox_inches='tight')


def count_total_number_of_plots_in_folder(include_name_dict):
    count = 0
    for include_name in include_name_dict:
        sim_num_dict = include_name_dict[include_name]
        for sim_num in sim_num_dict:
            count += 1
    return count



def make_one_subplot(folder_name, include_name, sim_num, plot_settings):

    I = load_all_sims_parallel_folder(folder_name, include_name, sim_num, plot_settings)
    plot_velocities_and_energies(I.energies, I.velocities)






def load_all_sims_parallel_folder(folder_name, include_name, sim_num, plot_settings):
    folder_dir = 'save/{}'.format(folder_name)
    dir_list = all_folders_in_dir_with(folder_dir, 'sim')
    for dir in dir_list:
        sim_name = dir[(dir.rfind('save/')+5):]
        sim_num_str = sim_name[(sim_name.rfind('Run_')):]
        sim_num_str = sim_num_str[sim_num_str.rfind('Run_')+4:]
        if sim_num_str == str(sim_num):
            ising = load_from_dynamic_range_data_one_sim(sim_name, include_name, plot_settings)
            return ising



def load_from_dynamic_range_data_one_sim(sim_name, include_name, plot_settings):
    dir = 'save/{}/repeated_generations'.format(sim_name)
    dir_list = all_folders_in_dir_with(dir, include_name)
    plot_settings['plot_varying_number']
    if plot_settings['plot_largest_varying_number']:
        # find largest carying number
        plot_settings['plot_varying_number'] = np.max([get_int_end_of_str(dir) for dir in dir_list])

    # Find dirs that shall be plotted
    dirs_to_plot = []
    for dir in dir_list:
        if get_int_end_of_str(dir) == plot_settings['plot_varying_number']:
            dirs_to_plot.append(dir)

    if len(dirs_to_plot) > 1:
        print('Found more than one simulation in repeated generation folder! Choos ing first detected!')

    if len(dirs_to_plot) == 0:
        print('Did not find varying number (time step) {} in {}. Skip plotting this'
              .format(plot_settings['plot_varying_number'], sim_name))
        return None
    else:
        # TODO: Change loading all isings in this path as soon as we have more than one ising for speed
        if plot_settings['compress_save_isings']:
            # energies and velocitoes are saved in last isings, therefore [-1]
            isings = load_isings_specific_path_decompress(dirs_to_plot[0])[-1]
        else:
            isings = load_isings_specific_path(dirs_to_plot[0])[0]
        if plot_settings['only_copied_isings']:
            isings = choose_copied_isings(isings)

        plot_ind_num = np.random.randint(0, len(isings)-1)
    return isings[plot_ind_num]




def get_int_end_of_str(s):
    m = re.search(r'\d+$', s)
    return int(m.group()) if m else None


def plot_velocities_and_energies(energies_list_attr, velocities_list_attr):
    plt.subplot(211)
    x_axis_gens = np.arange(len(energies_list_attr))
    plt.scatter(x_axis_gens, energies_list_attr, s=2, alpha=0.5)
    plt.xlabel('Time Step')
    plt.ylabel('Energy')

    plt.subplot(212)
    x_axis_gens = np.arange(len(velocities_list_attr))
    plt.scatter(x_axis_gens, velocities_list_attr, s=2, alpha=0.5)
    plt.xlabel('Time Step')
    plt.ylabel('Velocity')

    # Autocorreltaion
    # plt.subplot(313)
    # y_axis = autocorr(velocities_list_attr)
    # x_axis = np.arange(len(y_axis))
    # plt.scatter(x_axis, y_axis, s=2, alpha=0.5)

    # Fourier transform try1
    # plt.subplot(313)
    # f, Pxx = scipy.signal.welch(velocities_list_attr)
    # x_axis = np.arange(len(Pxx))
    # plt.semilogy(f, Pxx, linewidth=2, alpha=1)

    # Fourier transfor try2
    # The FFT of the signal
    # plt.subplot(313)
    # sig = velocities_list_attr
    # time_step = 0.2
    # sig_fft = fftpack.fft(sig)
    # # And the power (sig_fft is of complex dtype)
    # power = np.abs(sig_fft)
    # # The corresponding frequencies
    # sample_freq = fftpack.fftfreq(np.size(sig), d=time_step)
    # # Plot the FFT power
    # plt.plot(sample_freq, power)
    # plt.xlabel('Frequency [Hz]')
    # plt.ylabel('power')
    # plt.yscale('log')
    # plt.xscale('log')


def autocorr(x):
    result = np.correlate(x, x, mode='full')
    return result
    # return result[result.size/2:]

if __name__ == '__main__':

    plot_settings = {}

    # The label highlighted sims dict is used to choose which velocities to plot
    # plot_settings['label_highlighted_sims'] = {'sim-20201119-190135_parallel_b1_normal_run_g4000_t2000_27_sims': {'ds_res_10_try_2_gen_100d': {1: '1'}, 'gen4000_100foods_res_10_try_2dy': {21: '21'}},
    #                                            'sim-20201119-190204_parallel_b10_normal_run_g4000_t2000_54_sims': {'gen4000_100foods_res_10_try_2dy': {28: '28', 19: '19', 53: '53', 7: '7', 30: '30', 39: '39'}}}

    plot_settings['label_highlighted_sims'] = {'sim-20201022-184145_parallel_TEST_repeated': {'energies_velocities_one_rep': {1: '1', 2: '2'}}}
    plot_settings['label_highlighted_sims'] = {'sim-20201022-184145_parallel_TEST_repeated': {'energies_velocitiesy_three_rep': {1: '1', 2: '2'}}}

    # The legend labels are used to label the figures
    plot_settings['custom_legend_labels'] = {'sim-20201119-190135_parallel_b1_normal_run_g4000_t2000_27_sims': {'_intermediate_run_res_40_gen_100d': 'Critical Generation 100', 'gen4000_100foods_intermediate_run_res_40d': 'Critical Generation 4000'},
                                             'sim-20201119-190204_parallel_b10_normal_run_g4000_t2000_54_sims': {'gen4000_100foods_intermediate_run_res_40d': 'Sub Critical Generation 4000'}}
    # plot_settings['include_name'] = 'gen1000_100foods_velocity_period_overfitting_compresseddynamic_rang'

    # The varying number is the number of the attribute which is changed in the response plots (foods and time steps)
    # Either the largest number is plotted or a specific number is plotted
    plot_settings['plot_largest_varying_number'] = True
    plot_settings['plot_varying_number'] = 50000
    # TODO: only copied könnte Probleme, geben, da 1. Generation...
    plot_settings['only_copied_isings'] = True

    plot_settings['compress_save_isings'] = True
    plot_settings['number_columns_in_subplot'] = 2
    #inds = [0]
    main(plot_settings)
