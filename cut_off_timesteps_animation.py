from automatic_plot_helper import load_isings
from automatic_plot_helper import attribute_from_isings
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


def main(sim_name, list_attr, len_cut_off):
    isings = load_isings(sim_name)


def animate_cut_off(isings, list_attr, len_cut_off, sim_name, fps=30):
    fig = plt.figure()
    ani = animation.FuncAnimation(fig, update_plot,
                                  fargs=[isings, list_attr], interval=1,
                                  frames=len_cut_off)
    Writer = animation.FFMpegFileWriter
    writer = Writer(fps=fps, metadata=dict(artist='Jan Prosi'), bitrate=1800)
    writer.frame_format = 'png'

    save_path = 'save/{}/figs/cut_of_animation/'.format(sim_name)
    save_name =
    ani.save(savefilename, writer=writer)


def update_plot(cut_num, isings, list_attr):
    attrs = attribute_from_isings(isings, list_attr)
    attrs = cut_attrs(cut_num, attrs)

    # !!! Taking mean of list_attr NOT MEDIAN !!!
    mean_attrs = [np.mean(list_attr) for list_attr in attrs]

    plt.scatter(mean_attrs)
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
