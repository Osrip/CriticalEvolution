from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import load_isings_attributes_from_list
from automatic_plot_helper import load_settings
from automatic_plot_helper import detect_all_isings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
from numba import jit




def main(sim_name, list_attr, generations, inds, win_size):
    # attrs_list= generations, inds, attr_list
    list_attr = 'energies'
    attrs_list = [[], []]
    energies_list = load_isings_attributes_from_list(sim_name, generations, 'energies')
    velocities_list = load_isings_attributes_from_list(sim_name, generations, 'velocities')


    # loops over generations
    for energies_inds, velocities_inds, gen in zip(energies_list, velocities_list, generations):
        for ind in inds:
            fig = plt.figure(figsize=(24, 10))
            fig.suptitle('{}\ngeneration_{}_individual_{}'.format(sim_name, gen, ind))
            list_attr = energies_inds[ind]  # Choose energies
            derivatives = calculate_derivative(list_attr)
            #plot_derivatives(derivatives, sim_name, gen, ind)
            plot_velocities_and_energies(energies_inds[ind], velocities_inds[ind])
            #plot_derivatives_slided(derivatives, sim_name, gen, ind, win_size)
            plot_energies_derivatives_slided(energies_inds[ind], win_size)
            savefig(sim_name, win_size, gen, ind)


def savefig(sim_name, win_size, gen, ind):
    save_name = 'derivatives_slided_winsize_{}_gen_{}_ind_{}.png'.format(win_size, gen, ind)
    save_path = 'save/{}/figs/derivative_time_steps/new_derivative/'.format(sim_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    plt.savefig('{}{}'.format(save_path, save_name), dpi=300)


def plot_velocities_and_energies(energies_list_attr, velocities_list_attr):
    plt.subplot(222)
    x_axis_gens = np.arange(len(energies_list_attr))
    plt.scatter(x_axis_gens, energies_list_attr, s=2, alpha=0.5)
    plt.xlabel('Time Step')
    plt.ylabel('Energy')
    plt.subplot(224)
    x_axis_gens = np.arange(len(velocities_list_attr))
    plt.scatter(x_axis_gens, velocities_list_attr, s=2, alpha=0.5)
    plt.xlabel('Time Step')
    plt.ylabel('Velocity')



def calculate_derivative(list_attr):
    derivatives = []
    for i in range(len(list_attr)-1):
        deriv = list_attr[i+1] - list_attr[i]
        derivatives.append(deriv)
    return derivatives


def plot_derivatives(derivatives, sim_name, gen, ind):
    #matplotlib.use('GTK3Cairo')
    x_axis = np.arange(len(derivatives))
    plt.figure(figsize=(24, 10))
    ax1 = plt.subplot(221)
    plt.title('differences')
    plt.scatter(x_axis, derivatives, s=2, alpha=0.5)
    save_name = 'derivatives_gen_{}_ind_{}.png'.format(gen, ind)
    save_path = 'save/{}/figs/derivative_time_steps/all_in_one/'.format(sim_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)


def derivatives_low_pass(slided_energies, win_size):
    derivatives = []
    x_axis = []
    n = 0
    while n + win_size < len(slided_energies):
        derivatives.append(slided_energies[n + win_size] - slided_energies[n])
        x_axis.append(n+int(win_size))
        # Adding win size here. Usually would add win_size/2 But as this has already been done with slided energies
        # it is 2x win_size/2 this time
        n += 1
    return derivatives, x_axis


def plot_energies_derivatives_slided(energies, win_size):
    slided_energies, x_axis = slide_window(energies, win_size)
    derivatives_slided, x_axis_derivatives = derivatives_low_pass(slided_energies, win_size)
    # Normalizing derivatibes for win size,s o we have difference per time step
    derivatives_slided = list(map(lambda x: x / win_size, derivatives_slided))
    ax222 = plt.subplot(221)
    plt.scatter(x_axis, slided_energies)
    slided_energies_xlim = ax222.get_xlim()
    plt.xlabel('Time Step')
    plt.ylabel('Smoothed Energy')
    plt.title('Smoothed Energy, window length: {}'.format(win_size))
    plt.subplot(223)
    plt.xlabel('Time Step')
    plt.ylabel('Energy difference per Time Step')
    plt.title('Energy difference of smoothed energy, sampling distance: {}'.format(win_size))
    plt.scatter(x_axis_derivatives, derivatives_slided)
    plt.xlim(slided_energies_xlim)


def plot_derivatives_slided(derivatives, sim_name, gen, ind, win_size):
    #matplotlib.use('GTK3Cairo')
    derivatives, x_axis = slide_window(derivatives, win_size=win_size)
    #plt.figure(figsize=(12, 5))
    ax1 = plt.subplot(223)
    plt.scatter(x_axis, derivatives, s=2, alpha=0.5)
    plt.title('differences slided')
    plt.xlabel('Time Step')
    plt.ylabel('difference slided, window size = {}'.format(win_size))

    plt.show()


def slide_window(iterable, win_size):
    slided = []
    x_axis_gens = []
    n = 0
    while n+win_size < len(iterable)-1:
        mean = np.mean(iterable[n:n+win_size])
        slided.append(mean)
        x_axis_gens.append(n+int(win_size/2))
        n += 1
    return slided, x_axis_gens


if __name__ == '__main__':
    #sim_name = 'sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    #sim_name = 'sim-20200604-235424-g_2000_-t_2000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    sim_name = "sim-20200618-112616-l_sim-20200604-235424-g_2000_-t_2000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved_-li_1999_-g_1_-t_30000_-n_last_generation_very_long_b1"
    #sim_name = "sim-20200618-112742-l_sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved_-li_1999_-g_1_-t_30000_-n_last_generation_very_long_b10"
    list_attr = 'energies'
    #sim_name = 'sim-20200619-173349-g_2001_-ref_0_-noplt_-b_1_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4'
    #sim_name = 'sim-20200619-173340-g_2001_-ref_0_-noplt_-b_10_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4'
    #sim_name = 'sim-20200619-173345-g_2001_-ref_0_-noplt_-b_0.1_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4'
    #sim_name = 'sim-20200606-014815-g_2000_-t_4000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps'
    #sim_name = 'sim-20200606-014837-g_2000_-t_4000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps'
    #sim_name = 'sim-20200606-014846-g_2000_-t_4000_-b_0.1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps'
    # sim_name = 'sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    # sim_name = 'sim-20200604-235424-g_2000_-t_2000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    # sim_name = 'sim-20200604-235417-g_2000_-t_2000_-b_0.1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    # sim_name = 'sim-20200621-100451-g_1_-t_30000_-l_sim-20200619-173349-g_2001_-ref_0_-noplt_-b_1_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4_-li_2000_-a_0_-n_random_timesteps_last_gen_very_long'
    # sim_name = 'sim-20200621-123120-g_1_-t_30000_-l_sim-20200619-173349-g_2001_-ref_0_-noplt_-b_1_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4_-li_2000_-n_random_time_steps_last_gen_very_long_ENERGIES_saved_this_time'
    # sim_name = 'sim-20200621-123007-g_1_-t_30000_-l_sim-20200619-173340-g_2001_-ref_0_-noplt_-b_10_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4_-li_2000_-n_random_time_steps_last_gen_very_long_ENERGIES_saved_this_time'
    # sim_name = 'sim-20200621-123354-g_1_-t_30000_-l_sim-20200606-014837-g_2000_-t_4000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps_-li_1999_-n_long_last_generation_from_4000_ts_sim_ENERGIES_this_time'
    # sim_name = 'sim-20200621-123448-g_1_-t_30000_-l_sim-20200606-014815-g_2000_-t_4000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps_-li_1999_-n_long_last_generation_from_4000_ts_sim_ENERGIES_this_time'
    #sim_name = 'sim-20200604-235417-g_2000_-t_2000_-b_0.1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    #sim_name = 'sim-20200604-235424-g_2000_-t_2000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    #sim_name = 'sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    #win_size = 2000
    #win_size = 1000
    #sim_name = 'sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    #sim_name = 'sim-20200618-112616-l_sim-20200604-235424-g_2000_-t_2000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved_-li_1999_-g_1_-t_30000_-n_last_generation_very_long_b1'
    #sim_name = 'sim-20200618-112742-l_sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved_-li_1999_-g_1_-t_30000_-n_last_generation_very_long_b10'
    #sim_name = 'sim-20200621-123448-g_1_-t_30000_-l_sim-20200606-014815-g_2000_-t_4000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps_-li_1999_-n_long_last_generation_from_4000_ts_sim_ENERGIES_this_time'
    #sim_name = 'sim-20200621-123354-g_1_-t_30000_-l_sim-20200606-014837-g_2000_-t_4000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps_-li_1999_-n_long_last_generation_from_4000_ts_sim_ENERGIES_this_time'
    sim_name = 'sim-20200621-123120-g_1_-t_30000_-l_sim-20200619-173349-g_2001_-ref_0_-noplt_-b_1_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4_-li_2000_-n_random_time_steps_last_gen_very_long_ENERGIES_saved_this_time'
    sim_name = 'sim-20200621-123007-g_1_-t_30000_-l_sim-20200619-173340-g_2001_-ref_0_-noplt_-b_10_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4_-li_2000_-n_random_time_steps_last_gen_very_long_ENERGIES_saved_this_time'
    sim_name = 'sim-20200622-004643-g_1_-t_500000_-noplt_-l_sim-20200619-173349-g_2001_-ref_0_-noplt_-b_1_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4_-li_1999_-n_random_time_steps_super_long_last_gen'
    #sim_name = 'sim-20200622-004717-g_1_-t_500000_-noplt_-l_sim-20200619-173340-g_2001_-ref_0_-noplt_-b_10_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4_-li_1999_-n_random_time_steps_super_long_last_gen'
    sim_name = 'sim-20200621-224919-g_1_-t_120000_-noplt_-li_1999_-l_sim-20200619-174456-g_2001_-t_6000_-b_10_-dream_c_1000_-ref_0_-noplt_-c_4_-a_2000_-n_long_run_save_energies_-n_long_last_gen_for_6000ts_sim'
    sim_name = 'sim-20200621-205137-g_1_-t_120000_-li_1999_-l_sim-20200606-014837-g_2000_-t_4000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps_-noplt_-n_very_long_last_gen_from_4000'
    sim_name = 'sim-20200621-205137-g_1_-t_120000_-li_1999_-l_sim-20200606-014837-g_2000_-t_4000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps_-noplt_-n_very_long_last_gen_from_4000'
    sim_name = 'sim-20200621-205056-g_1_-t_120000_-li_1999_-l_sim-20200606-014815-g_2000_-t_4000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps_-noplt_-n_very_long_last_gen_from_4000'
    sim_name = 'sim-20200622-142753-g_1_-t_3000_-noplt_-l_sim-20200619-173349-g_2001_-ref_0_-noplt_-b_1_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4_-li_2000_-n_last_gen_random_time_steps_3000ts'
    #sim_name = 'sim-20200622-142821-g_1_-t_3000_-noplt_-l_sim-20200619-173340-g_2001_-ref_0_-noplt_-b_10_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4_-li_2000_-n_last_gen_random_time_steps_3000ts'
    sim_name = 'sim-20200621-205137-g_1_-t_120000_-li_1999_-l_sim-20200606-014837-g_2000_-t_4000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps_-noplt_-n_very_long_last_gen_from_4000'
    sim_name = 'sim-20200621-205056-g_1_-t_120000_-li_1999_-l_sim-20200606-014815-g_2000_-t_4000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-noplt_-n_energies_velocities_saved_more_time_steps_-noplt_-n_very_long_last_gen_from_4000'
    sim_name = 'sim-20200619-174456-g_2001_-t_6000_-b_10_-dream_c_1000_-ref_0_-noplt_-c_4_-a_2000_-n_long_run_save_energies'
    #sim_name = 'sim-20200619-174503-g_2001_-t_6000_-b_1_-dream_c_1000_-ref_0_-noplt_-c_4_-a_2000_-n_long_run_save_energies'
    sim_name = 'sim-20201003-000428-g_4000_-t_2000_-rec_c_1000_-c_props_100_50_-2_2_100_40_-iso_-ref_1000_-c_4_-a_1000_2000_3999_-no_trace_-n_different_betas_2000_fixed_ts_3_COMPARE_and_DYNAMIC_RANGE_FOOD_TS'
    sim_name = 'sim-20201022-175746-g_1_-energies_0_-t_120000_-li_1999_-l_sim-20201019-153950_parallel_parallel_mean_4000_ts_b10_fixed_ts/sim-20201019-153952-b_10_-g_2000_-t_4000_-noplt_-subfolder_sim-20201019-153950_parallel_parallel_mean_4000_ts_b10_fixed_ts_-n_Run_3_-n_life_time_analysis'
    sim_name = 'sim-20201026-224709_parallel_b10_fixed_4000ts_/sim-20201026-224711-b_10_-g_8000_-t_4000_-rec_c_2000_-c_props_10_10_-2_2_100_40_-c_1_-subfolder_sim-20201026-224709_parallel_b10_fixed_4000ts_-n_Run_1'
    sim_name = 'sim-20201026-224709_parallel_b10_fixed_4000ts_/sim-20201026-224711-b_10_-g_8000_-t_4000_-rec_c_2000_-c_props_10_10_-2_2_100_40_-c_1_-subfolder_sim-20201026-224709_parallel_b10_fixed_4000ts_-n_Run_1'
    win_size = 2000#500#2000#500
    settings = load_settings(sim_name)
    generations = settings['save_energies_velocities_gens'] #np.arange(1990, 2000)
    last_gen = detect_all_isings(sim_name)[-1]
    # For last generation velocties are always saved
    if type(generations) is list:
        generations.append(last_gen)
    else:
        generations = [last_gen]
    inds = np.arange(10)
    #inds = [0]
    main(sim_name, list_attr, generations, inds, win_size)
