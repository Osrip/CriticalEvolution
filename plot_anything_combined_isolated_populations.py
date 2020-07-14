import numpy as np
import matplotlib.pyplot as plt
from os import makedirs, path
from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import load_isings
from automatic_plotting_isolated_populations import seperate_isolated_populations
from automatic_plot_helper import load_settings
from matplotlib.lines import Line2D


def main(sim_name, isings_list_dict, settings, attr):

    iter_list = detect_all_isings(sim_name)
    folder = 'save/' + sim_name
    savefolder = folder + '/figs/' + attr + '_line/'


    savefilename = savefolder + attr + '_gen' + str(iter_list[0]) + '-' + str(iter_list[-1]) + '.png'

    if not path.exists(savefolder):
        makedirs(savefolder)

    colors = ['red', 'blue', 'green']
    plt.figure(figsize=(19, 10))
    legend_elements = []
    for i, iso_pop_name in enumerate(isings_list_dict):

        y_axis = []
        for isings in isings_list_dict[iso_pop_name]:
            y_axis = []
            for I in isings:
                attr_values_onegen = []
                exec('attr_values_onegen.append(I.{})'.format(attr))
                gen_avg = np.mean(attr_values_onegen)
                y_axis.append(gen_avg)

        x_axis = np.arange(len(y_axis))


        legend_elements.append(Line2D([0], [0], marker='o', color='w', label='population {}'.format(iso_pop_name), markerfacecolor=colors[i],
                                      markersize=5, alpha=0.75))
        plt.scatter(x_axis, y_axis, c=colors[i], alpha=0.15)


    # plt.legend(loc="lower right", bbox_to_anchor=(0.95, 0.05), handles=legend_elements)
    plt.legend(handles=legend_elements)
    plt.xlabel('Generation')
    plt.ylabel(attr)
    plt.savefig(savefilename, dpi=300, bbox_inches='tight')


if __name__ == '__main__':
    sim_name = 'sim-20200714-190003-g_100_-t_5_-iso_-n_test'
    isings_list = load_isings(sim_name, wait_for_memory=False)
    isings_list_dict = seperate_isolated_populations(isings_list)
    settings = load_settings(sim_name)

    main(sim_name, isings_list_dict, settings, 'Beta')