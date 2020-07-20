import numpy as np
import matplotlib.pyplot as plt
from os import makedirs, path
from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import load_isings
from automatic_plot_helper import load_isings_from_list
from isolated_population_helper import fittest_in_isolated_populations
from isolated_population_helper import seperate_isolated_populations
from automatic_plot_helper import load_settings
from matplotlib.lines import Line2D


def main(sim_name, isings_list_dict, attr, name_extension=''):

    iter_list = detect_all_isings(sim_name)
    folder = 'save/' + sim_name
    savefolder = folder + '/figs/' + attr + '_line/'

    savefilename = savefolder + '{}_gen{}-{}-_{}.png'.format(
        attr, str(iter_list[0]), str(iter_list[-1]), name_extension)


    if not path.exists(savefolder):
        makedirs(savefolder)

    colors = ['red', 'blue', 'green']
    plt.figure(figsize=(19, 10))
    legend_elements = []
    for i, iso_pop_name in enumerate(isings_list_dict):

        y_axis = []
        for isings in isings_list_dict[iso_pop_name]:
            attr_values_onegen = []
            for I in isings:
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
    sim_name = 'sim-20200714-210215-g_6000_-rand_ts_-iso_-ref_500_-rec_c_250_-a_100_250_500_1000_-no_trace_-n_different_betas_from_scratch_isolated' #'sim-20200714-190003-g_100_-t_5_-iso_-n_test'
    isings_list = load_isings(sim_name, wait_for_memory=False)
    #isings_list = load_isings_from_list(sim_name, np.arange(100))
    isings_list_dict = seperate_isolated_populations(isings_list)
    isings_list_dict = fittest_in_isolated_populations(isings_list_dict)
    settings = load_settings(sim_name)

    main(sim_name, isings_list_dict, 'Beta')