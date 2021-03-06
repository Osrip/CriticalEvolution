import numpy as np
from heat_capacity_parameter import calc_heat_cap_param_main
from automatic_plot_helper import all_sim_names_in_parallel_folder
from scipy import stats
import os
import pickle
import matplotlib.pyplot as plt
import time
import warnings
import seaborn as sns

def comparison_main(folder_name_dict, plot_settings):
    plt.rc('text', usetex=True)
    font = {'family': 'serif', 'size': 28, 'serif': ['computer modern roman']}
    plt.rc('font', **font)
    folders_delta_dict = {}
    folders_deltas_dict = {}
    for key, folder_name in folder_name_dict.items():
        if folder_name == '' or folder_name is None:
            pass
        else:
            if plot_settings['only_plot']:
                delta_dict, deltas_dict = load_plot_data(folder_name)
                folders_delta_dict[key] = delta_dict
                folders_deltas_dict[key] = deltas_dict
            else:
                if plot_settings['only_load_generation'] is None:
                    delta_dict, deltas_dict = load_dynamic_range_param(folder_name)
                else:
                    delta_dict, deltas_dict = load_dynamic_range_param(folder_name, [plot_settings['only_load_generation']])
                save_plot_data(folder_name, (delta_dict, deltas_dict))
                folders_delta_dict[key] = delta_dict
                folders_deltas_dict[key] = deltas_dict


    plot_settings['savefolder_name'] = 'dynamical_regime_comparison_plot_{}' \
        .format(time.strftime("%Y%m%d-%H%M%S"))
    os.makedirs('save/{}/figs'.format(plot_settings['savefolder_name']))
    plot_probability_density(folders_delta_dict, folders_deltas_dict, folder_name_dict, plot_settings)


def plot_probability_density(folders_delta_dict, folders_deltas_dict, folder_name_dict, plot_settings):
    plt.figure(figsize=(10, 5))
    plot_keys = ['folder_simple_last_gen_delta', 'folder_hard_last_gen_delta']
    colors = ['olive', 'maroon']
    labels = ['Easy Task', 'Hard Task']
    for plot_key, color, label in zip(plot_keys, colors, labels):
        try:
            delta_dict = folders_delta_dict[plot_key]
            if len(list(delta_dict.keys())) == 1:
                mean_delta_list_each_sim = delta_dict[list(delta_dict.keys())[0]]
            else:
                mean_delta_list_each_sim = delta_dict[str(plot_settings['compare_generation'])]
            plt.hist(mean_delta_list_each_sim, bins=15, alpha=0.2, color=color, label= label)
            sns.kdeplot(mean_delta_list_each_sim, data2=None, shade=False, vertical=False, color=color)
            plt.axvline(np.mean(mean_delta_list_each_sim), color=color, alpha=0.7, linestyle='dashed', linewidth=3)
        except KeyError:
            warnings.warn('Simulation for {} not loaded'.format(plot_key))


    save_dir = 'save/{}/figs/'.format(plot_settings['savefolder_name'])
    plt.legend()
    plt.ylabel('Density')
    plt.xlabel(r'$\langle \delta \rangle$')
    plt.title(r'$\beta_\mathrm{init}=1$, Generation 4000')
    plt.savefig(save_dir + 'probability_density.png', dpi=300, bbox_inches='tight')
    plt.show()


# def dynamic_range_extract_from_gen(folder_name, plot_settings):
#
#
#     for gen, mean_delta_list_each_sim in delta_dict.items():
#         mean_delta_per_sim = np.mean(mean_delta_list_each_sim)
#         if plot_settings['compare_generation'] == gen:


def converting_list_of_dicts_to_dict_of_lists(delta_dicts_all_sims):
    # converting to
    generations = list(delta_dicts_all_sims[0].keys())
    dict_sorted_by_generatons = {}
    for gen in generations:
        dict_sorted_by_generatons[gen] = []
    for delta_dict in delta_dicts_all_sims:
        for gen in generations:
            dict_sorted_by_generatons[gen].append(delta_dict[gen])
    return dict_sorted_by_generatons


def load_dynamic_range_param(folder_name, gen_list=None):

    sim_names = all_sim_names_in_parallel_folder(folder_name)
    delta_dicts_all_sims = []
    deltas_dicts_all_sims = []
    for sim_name in sim_names:
        module_settings = {}
        mean_log_beta_distance_dict, log_beta_distance_dict, beta_distance_dict, beta_index_max, betas_max_gen_dict, \
        heat_caps_max_dict, smoothed_heat_caps = calc_heat_cap_param_main(sim_name, module_settings, gen_list=gen_list,
                                                                          gaussian_kernel=True)
        delta_dict = mean_log_beta_distance_dict
        delta_list_dict = log_beta_distance_dict
        delta_dicts_all_sims.append(delta_dict)
        deltas_dicts_all_sims.append(delta_list_dict)


        # settings_list.append(load_settings(dir))
    # delta_dicts_all_sims --> men of each generation, deltas_dicts_all_sims --> each individual in a list
    delta_dict = converting_list_of_dicts_to_dict_of_lists(delta_dicts_all_sims)
    deltas_dict = converting_list_of_dicts_to_dict_of_lists(deltas_dicts_all_sims)
    return delta_dict, deltas_dict


def save_plot_data(folder_name, plot_data):
    save_dir = 'save/{}/dynamical_range_plot_data/'.format(folder_name)
    save_name = 'dynamical_range_data_compare_between_folders.pickle'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    pickle_out = open(save_dir + save_name, 'wb')
    pickle.dump(plot_data, pickle_out)
    pickle_out.close()


def load_plot_data(folder_name):
    save_dir = 'save/{}/dynamical_range_plot_data/'.format(folder_name)
    save_name = 'dynamical_range_data_compare_between_folders.pickle'
    print('Load plot data from: {}{}'.format(save_dir, save_name))

    file = open(save_dir+save_name, 'rb')
    attrs_lists = pickle.load(file)
    file.close()

    return attrs_lists

if __name__ == '__main__':

    plot_settings = {}
    plot_settings['only_plot'] = True
    # Only works when 'only_plot' == False, should be None by default!!!!
    plot_settings['only_load_generation'] = 4000 #None
    plot_settings['compare_generation'] = 4000 #10

    folder_name_dict = {}
    # folder_name_dict['folder_simple_continuous_delta'] = 'sim-20201210-200605_parallel_b1_dynamic_range_c_20_g4000_t2000_10_sims'
    # folder_name_dict['folder_simple_last_gen_delta'] = 'sim-20210226-023914_parallel_b1_default_task_significance_20_runs_delta_last_gen'
    # folder_name_dict['folder_hard_continuous_delta'] = ''
    # folder_name_dict['folder_hard_last_gen_delta'] = 'sim-20210226-023902_parallel_b1_break_eat_significance_20_runs_delta_last_gen'

    # folder_name_dict['folder_simple_continuous_delta'] = ''
    # folder_name_dict['folder_simple_last_gen_delta'] = 'sim-20210226-023914_parallel_b1_default_task_significance_20_runs_delta_last_gen'
    # folder_name_dict['folder_hard_continuous_delta'] = ''
    # folder_name_dict['folder_hard_last_gen_delta'] = 'sim-20210226-023902_parallel_b1_break_eat_significance_20_runs_delta_last_gen'

    folder_name_dict['folder_simple_continuous_delta'] = ''
    folder_name_dict['folder_simple_last_gen_delta'] = 'sim-20210226-023914_parallel_b1_default_task_significance_20_runs_delta_last_gen_HEL_ONLY_PLOT'
    folder_name_dict['folder_hard_continuous_delta'] = ''
    folder_name_dict['folder_hard_last_gen_delta'] = 'sim-20210226-023902_parallel_b1_break_eat_significance_20_runs_delta_last_gen_HEL_ONLY_PLOT'
    #
    # folder_name_dict['folder_simple_continuous_delta'] = ''
    # folder_name_dict['folder_simple_last_gen_delta'] = 'sim-20210302-215811_parallel_beta_linspace_rec_c20_TEST'
    # folder_name_dict['folder_hard_continuous_delta'] = ''
    # folder_name_dict['folder_hard_last_gen_delta'] = ''

    comparison_main(folder_name_dict, plot_settings)