from automatic_plot_helper import load_settings
from automatic_plot_helper import load_top_isings
from automatic_plot_helper import load_top_isings_attr
from automatic_plot_helper import load_isings_from_list
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from os import makedirs, path
import pickle

class SmallIsing:
    def __init__(self, avg_energy, time_steps_gen):
        self.avg_energy = avg_energy
        self.time_steps_gen = time_steps_gen
        self.norm_avg_energy = avg_energy / time_steps_gen


def all_plots(sim_name_b1_fix, sim_name_b10_fix, sim_name_b1_rand, sim_name_rand, only_top_isings=20,
              load_previous=True):


    save_folder = 'save/plots_for_anna/'
    matplotlib.rcParams.update({'font.size': 22})

    if not load_previous:
        attrs_gen_b10_fix = load_ising_stuff(sim_name_b10_fix, only_top_isings)
        attrs_gen_b1_fix = load_ising_stuff(sim_name_b1_fix, only_top_isings)
        attrs_gen_b10_rand = load_ising_stuff(sim_name_b10_rand, only_top_isings)
        attrs_gen_b1_rand = load_ising_stuff(sim_name_b1_rand, only_top_isings)

        loaded_plot_attrs = {
            'attrs_gen_b1_fix': attrs_gen_b1_fix,
            'attrs_gen_b10_fix': attrs_gen_b10_fix,
            'attrs_gen_b10_rand': attrs_gen_b10_rand,
            'attrs_gen_b1_rand': attrs_gen_b1_rand
        }

        pickle_out = open('{}loaded_plot_attrs.pickle'.format(save_folder), 'wb')
        pickle.dump(loaded_plot_attrs, pickle_out)
        pickle_out.close()

    else:

        colour_b1 = 'darkorange'
        colour_b10 = 'blue'

        file = open('{}/loaded_plot_attrs.pickle'.format(save_folder), 'rb')
        loaded_plot_attrs = pickle.load(file)
        file.close()

        attrs_gen_b10_fix = loaded_plot_attrs['attrs_gen_b10_fix']
        attrs_gen_b1_fix = loaded_plot_attrs['attrs_gen_b1_fix']
        attrs_gen_b10_rand = loaded_plot_attrs['attrs_gen_b10_rand']
        attrs_gen_b1_rand = loaded_plot_attrs['attrs_gen_b1_rand']

        ylim = plot_generational_avg(attrs_gen_b10_fix, colour_b10, save_folder, 'fixed_time_steps_b10', get_axis=True)
        plot_generational_avg(attrs_gen_b1_fix, colour_b1, save_folder, 'fixed_time_steps_b1', get_axis=False, ylim=ylim)
        plot_generational_avg(attrs_gen_b10_rand, colour_b10, save_folder, 'random_time_steps_b10', get_axis=False, ylim=ylim)
        plot_generational_avg(attrs_gen_b1_rand, colour_b1, save_folder, 'random_time_steps_b1', get_axis=False, ylim=ylim)

        plot_overlap(attrs_gen_b1_fix, attrs_gen_b10_fix, colour_b1, colour_b10, save_folder,
                     'Overlap_fixed_time_steps', ylim)
        plot_overlap(attrs_gen_b1_rand, attrs_gen_b10_rand, colour_b1, colour_b10, save_folder,
                     'Overlap_random_time_steps', ylim)



def load_ising_stuff(sim_name, only_top_isings):
    isings_avg_energy_list = load_top_isings_attr(sim_name, only_top_isings, 'avg_energy')
    # Load this in order to have something to compute the number of time steps of current generation with
    energies_first_ind = load_top_isings_attr(sim_name, 1, 'energies')
    # Get rid of double list (usually several individuals are in there but now only one is in there, which is why we can remove one nesting)
    energies_first_ind = [energies[0] for energies in energies_first_ind]
    time_steps_each_gen = list(map(lambda x: len(x), energies_first_ind))
    settings = load_settings(sim_name)
    settings['pop_size'] = only_top_isings
    small_isings_list = create_small_isings(isings_avg_energy_list, time_steps_each_gen)
    mean_attrs_generational = create_generational_avg(small_isings_list, 'norm_avg_energy')
    return mean_attrs_generational



def create_generational_avg(isings_list, attr_name):
    mean_attrs_generational = []
    for isings in isings_list:
        attrs = []
        for I in isings:
            exec('attrs.append(I.{})'.format(attr_name))
        mean_attrs_generational.append(np.mean(attrs))
    return mean_attrs_generational


def plot_generational_avg(y_axis, colour, save_folder, add_save_name, get_axis=True, ylim=None):
    x_axis = np.arange(len(y_axis))
    #matplotlib.use('GTK3Cairo')
    plt.figure(figsize=(19, 10))
    ax = plt.scatter(x_axis, y_axis, alpha=0.15, c=colour)
    if get_axis:
        ylim = plt.ylim()
    else:
        plt.ylim(ylim)

    if not path.exists(save_folder):
        makedirs(save_folder)
    save_name = '{}.png'.format(add_save_name)

    plt.savefig(save_folder + save_name, dpi=300) #bbox_inches='tight'
    plt.show()
    if get_axis:
        return ylim

def plot_overlap(y_axis_b1, y_axis_b10, colour_b1, colour_b10, save_folder, add_save_name, ylim=None):
    x_axis_b1 = np.arange(len(y_axis_b1))
    x_axis_b10 = np.arange(len(y_axis_b10))
    plt.figure(figsize=(19, 10))
    plt.scatter(x_axis_b1, y_axis_b1, alpha=0.15, c=colour_b1)
    plt.scatter(x_axis_b10, y_axis_b10, alpha=0.15, c=colour_b10)
    plt.ylim(ylim)
    plt.savefig(save_folder+add_save_name, dpi=300)
    plt.show()


def create_small_isings(isings_avg_energy_list, time_steps_each_gen):
    small_isings_list = []
    for avg_energies, time_steps_gen in zip(isings_avg_energy_list, time_steps_each_gen):
        small_isings = []
        for avg_energy in avg_energies:
            I_small = SmallIsing(avg_energy, time_steps_gen)
            small_isings.append(I_small)
        small_isings_list.append(small_isings)
    return small_isings_list


if __name__ == '__main__':
    sim_name_b10_fix = 'sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    sim_name_b1_fix = 'sim-20200604-235424-g_2000_-t_2000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    sim_name_b10_rand = 'sim-20200619-173340-g_2001_-ref_0_-noplt_-b_10_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4'
    sim_name_b1_rand = 'sim-20200619-173349-g_2001_-ref_0_-noplt_-b_1_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4'
    all_plots(sim_name_b1_fix, sim_name_b10_fix, sim_name_b1_rand, sim_name_b10_rand)
