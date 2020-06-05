from automatic_plot_helper import load_isings
from automatic_plot_helper import attribute_from_isings
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


def main(sim_name, list_attr, len_cut_off):
    isings = load_isings(sim_name)
    animate_cut_off(isings, list_attr, len_cut_off, sim_name)


def animate_cut_off(isings, list_attr, len_cut_off, sim_name, fps=30):
    fig = plt.figure()
    ani = animation.FuncAnimation(fig, update_plot,
                                  fargs=[isings, list_attr], interval=1,
                                  frames=len_cut_off)
    Writer = animation.FFMpegFileWriter
    writer = Writer(fps=fps, metadata=dict(artist='Jan Prosi'), bitrate=1800)
    writer.frame_format = 'png'

    save_path = 'save/{}/figs/cut_of_animation/'.format(sim_name)
    save_name = '{}_cut_off_{}_ts'.format(list_attr, len_cut_off)
    ani.save(save_path+save_name, writer=writer)


def update_plot(cut_num, isings, list_attr):

    # isings is a list of generations including again isings, therefore iterating through the gernerations with list
    # comprehensions, then again iterating through different individuals of one generation within that
    attrs_list = [attribute_from_isings(ising, list_attr) for ising in isings]
    attrs_list = [cut_attrs(cut_num, attrs) for attrs in attrs_list]

    # !!! Taking mean of list_attr NOT MEDIAN !!!
    mean_attrs_list = [[np.mean(list_attr) for list_attr in attrs] for attrs in attrs_list]
    # Now we have the attributes of all inidividuals of all generations in a nice list of lists availablöe for plotting

    # Taking mean over every generation, so we have one data point for each generation
    gen_mean_mean_attrs_list = [np.mean(attrs_one_gen) for attrs_one_gen in attrs_list]

    x_axis = np.arange(len(gen_mean_mean_attrs_list))
    plt.scatter(x_axis ,gen_mean_mean_attrs_list)
    plt.ylabel(list_attr)
    plt.xlabel('Generation')


def cut_attrs(cut_num, attrs):
    '''
    Cuts away first -cut_num- entries from list attribute
    '''
    new_attrs = []
    for list_attr in attrs:
        list_attr = list_attr[cut_num:]
        new_attrs.append(list_attr)
    return new_attrs


if __name__ == '__main__':
    sim_name = 'sim-20200604-235417-g_2000_-t_2000_-b_0.1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    len_cut_off = 500
    list_attrs = ['energies', 'velocities']
    for list_attr in list_attrs:
        main(sim_name, list_attr, len_cut_off)