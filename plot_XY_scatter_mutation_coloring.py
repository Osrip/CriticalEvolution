from automatic_plot_helper import load_isings
from automatic_plot_helper import load_multiple_isings_attrs
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import pickle


def mutation_coloring_main(sim_name, plot_settings):
    if not plot_settings['only_plot']:
        multiple_isings_attrs = load_multiple_isings_attrs(sim_name, [plot_settings['x_attr'], plot_settings['y_attr'], 'prev_mutation'])
        save_plot_data(sim_name, multiple_isings_attrs, plot_settings)
    else:
        multiple_isings_attrs = load_plot_data(sim_name, plot_settings)
    plot(multiple_isings_attrs, sim_name, plot_settings)


def save_plot_data(sim_name, multiple_isings_attrs, plot_settings):
    save_dir = 'save/{}/figs/mutations_colored/'.format(sim_name)
    save_name = 'multiple_isings_attrs.pickle'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    pickle_out = open(save_dir + save_name, 'wb')
    pickle.dump(multiple_isings_attrs, pickle_out)
    pickle_out.close()


def load_plot_data(sim_name, plot_settings):
    save_dir = 'save/{}/figs/mutations_colored/'.format(sim_name)
    save_name = 'multiple_isings_attrs.pickle'
    print('Load plot data from: {}{}'.format(save_dir, save_name))
    file = open(save_dir+save_name, 'rb')
    multiple_isings_attrs = pickle.load(file)
    file.close()
    return multiple_isings_attrs


def plot(multiple_isings_attrs, sim_name, plot_settings):
    plt.figure(figsize=(10,7))
    for gen, attr_dict in enumerate(multiple_isings_attrs):
        attr_dict['mutation_colors'] = list(map(plot_settings['prev_mutation_colors'].get, attr_dict['prev_mutation']))
        plt.scatter(attr_dict[plot_settings['x_attr']], attr_dict[plot_settings['y_attr']], c=attr_dict['mutation_colors'], s=0.5, alpha=0.3)
    plt.ylabel(plot_settings['y_attr'])
    plt.xlabel(plot_settings['x_attr'])
    savefolder = 'save/{}/figs/mutations_colored/'.format(sim_name)
    savefilename = 'mutations_colored.png'
    if not os.path.exists(savefolder):
        os.makedirs(savefolder)
    plt.savefig(savefolder+savefilename, dpi=150, bbox_inches='tight')



if __name__ == '__main__':
    # sim_name = 'sim-20201026-224639_parallel_b1_fixed_4000ts/sim-20201026-224642-b_1_-g_8000_-t_4000_-rec_c_2000_-c_props_10_10_-2_2_100_40_-c_1_-subfolder_sim-20201026-224639_parallel_b1_fixed_4000ts_-n_Run_1' #
    # sim_name = 'sim-20201026-224709_parallel_b10_fixed_4000ts/sim-20201026-224711-b_10_-g_8000_-t_4000_-rec_c_2000_-c_props_10_10_-2_2_100_40_-c_1_-subfolder_sim-20201026-224709_parallel_b10_fixed_4000ts_-n_Run_1'
    # sim_names = ['sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000/sim-20201022-190555-b_1_-g_4000_-t_2000_-noplt_-subfolder_sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000_-n_Run_1', 'sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000/sim-20201022-190618-b_10_-g_4000_-t_2000_-noplt_-subfolder_sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000_-n_Run_1']
    sim_names = ['sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000_HEL_ONLY_PLOT_MUTATION/sim-20201022-190555-b_1_-g_4000_-t_2000_-noplt_-subfolder_sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000_-n_Run_1', 'sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000_HEL_ONLY_PLOT_MUTATION/sim-20201022-190618-b_10_-g_4000_-t_2000_-noplt_-subfolder_sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000_-n_Run_1']

    for sim_name in sim_names :
        plot_settings = {}
        plot_settings['only_plot'] = True

        plot_settings['x_attr'] = 'generation'
        plot_settings['y_attr'] = 'avg_energy'
        prev_mutation_colors = {'init': 'grey', 'copy': 'olive', 'point': 'slateblue', 'mate': 'maroon'}
        plot_settings['prev_mutation_colors'] = prev_mutation_colors
        mutation_coloring_main(sim_name, plot_settings)