from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import load_isings_attributes_from_list
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
from numba import jit




def main(sim_name, list_attr, generations, inds, win_size):
    # attrs_list= generations, inds, attr_list
    attrs_list = load_isings_attributes_from_list(sim_name, generations, list_attr)

    # loops over generations
    for attrs, gen in zip(attrs_list, generations):
        for ind in inds:
            list_attr = attrs[ind]
            derivatives = calculate_derivative(list_attr)
            plot_derivatives(derivatives, sim_name, gen, ind)
            plot_derivatives_slided(derivatives, sim_name, gen, ind, win_size)


def calculate_derivative(list_attr):
    derivatives = []
    for i in range(len(list_attr)-1):
        deriv = list_attr[i+1] - list_attr[i]
        derivatives.append(deriv)
    return derivatives


def plot_derivatives(derivatives, sim_name, gen, ind):
    matplotlib.use('GTK3Cairo')
    x_axis = np.arange(len(derivatives))
    plt.figure(figsize=(12, 10))
    ax1 = plt.subplot(211)
    plt.scatter(x_axis, derivatives, s=2, alpha=0.5)
    save_name = 'derivatives_gen_{}_ind_{}.png'.format(gen, ind)
    save_path = 'save/{}/figs/derivative_time_steps/'.format(sim_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    #plt.savefig('{}{}'.format(save_path, save_name), dpi=300)
    #plt.show()


def plot_derivatives_slided(derivatives, sim_name, gen, ind, win_size):
    matplotlib.use('GTK3Cairo')
    derivatives, x_axis = slide_window(derivatives, win_size=win_size)
    #plt.figure(figsize=(12, 5))
    ax1 = plt.subplot(212)
    plt.scatter(x_axis, derivatives, s=2, alpha=0.5)
    save_name = 'derivatives_slided_winsize_{}_gen_{}_ind_{}.png'.format(win_size, gen, ind)
    save_path = 'save/{}/figs/derivative_time_steps/'.format(sim_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    plt.savefig('{}{}'.format(save_path, save_name), dpi=300)
    plt.show()

#@jit(nopython=True)
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
    sim_name = 'sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    #'sim-20200604-235424-g_2000_-t_2000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    list_attr = 'energies'
    win_size = 1000
    generations = [1999]
    inds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    main(sim_name, list_attr, generations, inds, win_size)