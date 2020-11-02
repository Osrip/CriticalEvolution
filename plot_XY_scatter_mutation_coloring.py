from automatic_plot_helper import load_isings
from automatic_plot_helper import load_multiple_isings_attrs
import matplotlib.pyplot as plt
import os


def mutation_coloring_main(sim_name, plot_settings):
    multiple_isings_attrs = load_multiple_isings_attrs(sim_name, [plot_settings['x_attr'], plot_settings['y_attr'], 'prev_mutation'])
    plt.figure(figsize=(10,7))
    for gen, attr_dict in enumerate(multiple_isings_attrs):
        attr_dict['mutation_colors'] = map(plot_settings['prev_mutation_colors'].get, attr_dict['prev_mutation'])
        plt.scatter(attr_dict['x_attr'], attr_dict['y_attr'], c=attr_dict['mutation_colors'])

    savefolder = 'save/{}/figs/mutations_colored/'.format(sim_name)
    savefilename = 'mutations_colored.png'
    if not os.path.exists(savefolder):
        os.makedirs(savefolder)
    plt.savefig(savefolder+savefilename)



if __name__ == '__main__':
    sim_name = 'sim-20201026-224639_parallel_b1_fixed_4000ts/sim-20201026-224642-b_1_-g_8000_-t_4000_-rec_c_2000_-c_props_10_10_-2_2_100_40_-c_1_-subfolder_sim-20201026-224639_parallel_b1_fixed_4000ts_-n_Run_1'
    plot_settings = {}
    plot_settings['x_attr'] = 'generation'
    plot_settings['y_attr'] = 'avg_energy'
    prev_mutation_colors = {'init': 'grey', 'copy': 'olive', 'point': 'slateblue', 'mate': 'maroon'}
    plot_settings['prev_mutation_colors'] = prev_mutation_colors
    mutation_coloring_main(sim_name, plot_settings)