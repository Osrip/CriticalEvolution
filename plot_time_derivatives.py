from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import load_isings_attributes_from_list
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
            plt.figure(figsize=(24, 10))
            list_attr = energies_inds[ind] # Choose energies
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
    plt.xlabel('Generation')
    plt.ylabel('Energy')
    plt.subplot(224)
    plt.scatter(x_axis_gens, velocities_list_attr, s=2, alpha=0.5)
    plt.xlabel('Generation')
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
    ax222 = plt.subplot(221)
    plt.scatter(x_axis, slided_energies)
    slided_energies_xlim = ax222.get_xlim()
    plt.xlabel('Time Steps')
    plt.ylabel('Smoothed Energy')
    plt.title('Smoothed Energy, window length: {}'.format(win_size))
    plt.subplot(223)
    plt.xlabel('Time Steps')
    plt.ylabel('Energy derivative')
    plt.title('Energy derivative of smoothed energy, point sampling difference: {}'.format(win_size))
    plt.scatter(x_axis_derivatives, derivatives_slided)
    plt.xlim(slided_energies_xlim)


def plot_derivatives_slided(derivatives, sim_name, gen, ind, win_size):
    #matplotlib.use('GTK3Cairo')
    derivatives, x_axis = slide_window(derivatives, win_size=win_size)
    #plt.figure(figsize=(12, 5))
    ax1 = plt.subplot(223)
    plt.scatter(x_axis, derivatives, s=2, alpha=0.5)
    plt.title('differences slided')
    plt.xlabel('Generations')
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
    #sim_name = "sim-20200618-112616-l_sim-20200604-235424-g_2000_-t_2000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved_-li_1999_-g_1_-t_30000_-n_last_generation_very_long_b1"
    sim_name = "sim-20200618-112742-l_sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved_-li_1999_-g_1_-t_30000_-n_last_generation_very_long_b10"
    list_attr = 'energies'
    win_size = 2000
    generations = [0]
    inds = np.arange(10)
    #inds = [0]
    main(sim_name, list_attr, generations, inds, win_size)
