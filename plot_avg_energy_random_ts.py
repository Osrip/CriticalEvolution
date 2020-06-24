from automatic_plot_helper import load_settings
from automatic_plot_helper import load_top_isings
from automatic_plot_helper import load_top_isings_attr
from automatic_plot_helper import load_isings_from_list
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from os import makedirs, path

class SmallIsing:
    def __init__(self, avg_energy, time_steps_gen):
        self.avg_energy = avg_energy
        self.time_steps_gen = time_steps_gen
        self.norm_avg_energy = avg_energy / time_steps_gen



def main(sim_name, only_top_isings=20):
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
    plot_generational_avg(mean_attrs_generational)


def create_generational_avg(isings_list, attr_name):
    mean_attrs_generational = []
    for isings in isings_list:
        attrs = []
        for I in isings:
            exec('attrs.append(I.{})'.format(attr_name))
        mean_attrs_generational.append(np.mean(attrs))
    return mean_attrs_generational


def plot_generational_avg(y_axis):
    x_axis = np.arange(len(y_axis))
    matplotlib.use('GTK3Cairo')
    plt.figure(figsize=(19, 10))
    plt.scatter(x_axis, y_axis, alpha=0.15)
    save_folder = 'save/{}/figs/avg_energy_normalized_ANNA/'.format(sim_name)
    if not path.exists(save_folder):
        makedirs(save_folder)
    save_name = 'moin.png'
    plt.savefig(save_folder + save_name, bbox_inches='tight', dpi=300)
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
    sim_name = 'sim-20200619-173340-g_2001_-ref_0_-noplt_-b_10_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4'
    main(sim_name)
