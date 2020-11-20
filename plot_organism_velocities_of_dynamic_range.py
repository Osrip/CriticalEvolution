from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import load_isings_attributes_from_list
from automatic_plot_helper import load_settings
from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import all_folders_in_dir_with
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




def main(folder_name, plot_settings):


    isings_dict_each_sim = load_all_sims_parallel_folder(folder_name, plot_settings)
    for run_num_key in isings_dict_each_sim:
        isings = isings_dict_each_sim[run_num_key]
        for i, I in enumerate(isings):
            fig_name = '{}_Includes_{}_{}_rand_org_num{}'.format(folder_name, plot_settings['include_name'], run_num_key, i)
            fig = plt.figure(figsize=(12, 10))
            fig.suptitle(fig_name)
            plot_velocities_and_energies(I.energies, I.velocities)


            save_path = 'save/{}/figs/energies_velocities_plot/'.format(folder_name)
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            plt.savefig('{}{}'.format(save_path, fig_name), dpi=150, bbox_inches='tight')



def load_all_sims_parallel_folder(folder_name, plot_settings):
    folder_dir = 'save/{}'.format(folder_name)
    dir_list = all_folders_in_dir_with(folder_dir, 'sim')
    isings_dict_each_sim = {}
    for dir in dir_list:
        sim_name = dir[(dir.rfind('save/')+5):]
        sim_run_num_str = sim_name[(sim_name.rfind('Run_')):]
        isings = load_from_dynamic_range_data_one_sim(sim_name, plot_settings)
        if not isings is None:
            isings_dict_each_sim[sim_run_num_str] = isings
    return isings_dict_each_sim



def load_from_dynamic_range_data_one_sim(sim_name, plot_settings):
    dir = 'save/{}/repeated_generations'.format(sim_name)
    dir_list = all_folders_in_dir_with(dir, plot_settings['include_name'])
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
            isings = load_isings_specific_path_decompress(dirs_to_plot[0])[0]
        else:
            isings = load_isings_specific_path(dirs_to_plot[0])[0]
        if plot_settings['only_copied_isings']:
            isings = choose_copied_isings(isings)

        plot_ind_nums = np.random.randint(0, len(isings)-1, plot_settings['number_individuals'])
    return [isings[i] for i in plot_ind_nums]




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

    # folder_names = ['sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000', 'sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000', 'sim-20201105-202455_parallel_b1_random_ts_2000_lim_100_3900', 'sim-20201105-202517_parallel_b10_random_ts_2000_lim_100_3900']#'sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000'
    # folder_names = ['sim-20201026-224709_parallel_b10_fixed_4000ts_']
    # folder_names = ['sim-20201022-184145_parallel_TEST_repeated']
    folder_names = ['sim-20201116-182731_parallel_b10_1000ts_fixed_compressed']
    for folder_name in folder_names:
        plot_settings = {}


        plot_settings['include_name'] = 'gen1000_100foods_velocity_period_overfitting_compresseddynamic_rang' #'gen50_100foods_COMPRESSdynamic_range' '100foods_COMPRESSdynamic_range_run_' #
        # The varying number is the number of the attribute which is changed in the response plots (foods and time steps)
        # Either the largest number is plotted or a specific number is plotted
        plot_settings['plot_largest_varying_number'] = True
        plot_settings['plot_varying_number'] = 50000
        # TODO: only copied könnte Probleme, geben, da 1. Generation...
        plot_settings['only_copied_isings'] = True
        plot_settings['number_individuals'] = 3
        plot_settings['compress_save_isings'] = True
        #inds = [0]
        main(folder_name, plot_settings)
