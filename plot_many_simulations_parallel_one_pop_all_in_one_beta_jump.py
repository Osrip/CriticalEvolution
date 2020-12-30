import matplotlib
matplotlib.use('Agg')
from automatic_plot_helper import all_folders_in_dir_with
from automatic_plot_helper import load_isings_attr
from automatic_plot_helper import load_isings_specific_path
from automatic_plot_helper import attribute_from_isings
from automatic_plot_helper import load_settings
from automatic_plot_helper import choose_copied_isings
from automatic_plot_helper import calc_normalized_fitness
from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import all_sim_names_in_parallel_folder
import numpy as np

import matplotlib.pyplot as plt
import os
import pickle
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
import seaborn as sns
from matplotlib.lines import Line2D
import matplotlib.colors as colors_package
from heat_capacity_parameter import calc_heat_cap_param_main
from matplotlib.patches import Patch
import matplotlib.cm as cm


def main_plot_parallel_sims(folder_name, plot_settings):
    plt.rc('text', usetex=True)
    font = {'family': 'serif', 'size': 18, 'serif': ['computer modern roman']}
    plt.rc('font', **font)
    if plot_settings['only_copied']:
        plot_settings['only_copied_str'] = '_only_copied_orgs'
    else:
        plot_settings['only_copied_str'] = '_all_orgs'

    if plot_settings['only_plot_certain_generations']:
        plot_settings['plot_generations_str'] = 'gen_{}_to_{}' \
            .format(plot_settings['lowest_and_highest_generations_to_be_plotted'][0],
                    plot_settings['lowest_and_highest_generations_to_be_plotted'][1])
    else:
        plot_settings['plot_generations_str'] = 'gen_all'

    if not plot_settings['only_plot']:
        attrs_lists = load_attrs(folder_name, plot_settings)
        save_plot_data(folder_name, attrs_lists, plot_settings)
    else:
        attrs_lists = load_plot_data(folder_name, plot_settings)
    plot(attrs_lists, plot_settings)


def save_plot_data(folder_name, attrs_lists, plot_settings):
    save_dir = 'save/{}/one_pop_plot_data/'.format(folder_name)
    save_name = 'plot_data_{}{}_min_ts{}_min_food{}_{}.pickle' \
        .format(plot_settings['attr'], plot_settings['only_copied_str'], plot_settings['min_ts_for_plot'],
                plot_settings['min_food_for_plot'], plot_settings['plot_generations_str'])
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    pickle_out = open(save_dir + save_name, 'wb')
    pickle.dump(attrs_lists, pickle_out)
    pickle_out.close()


def load_plot_data(folder_name, plot_settings):
    save_dir = 'save/{}/one_pop_plot_data/'.format(folder_name)
    save_name = 'plot_data_{}{}_min_ts{}_min_food{}_{}.pickle'. \
        format(plot_settings['attr'], plot_settings['only_copied_str'], plot_settings['min_ts_for_plot'],
               plot_settings['min_food_for_plot'], plot_settings['plot_generations_str'])
    print('Load plot data from: {}{}'.format(save_dir, save_name))
    try:
        file = open(save_dir+save_name, 'rb')
        attrs_lists = pickle.load(file)
        file.close()
    except FileNotFoundError:
        print('Did not find original plot file where all generations are plotted...looking for older version file')
        if not plot_settings['only_plot_certain_generations']:
            save_name = 'plot_data_{}{}_min_ts{}_min_food{}.pickle'. \
                format(plot_settings['attr'], plot_settings['only_copied_str'], plot_settings['min_ts_for_plot'],
                       plot_settings['min_food_for_plot'])
            file = open(save_dir+save_name, 'rb')
            attrs_lists = pickle.load(file)
            file.close()
    return attrs_lists


def dynamic_regime_param_all_sims(plot_settings, generation):
    all_deltas = []
    for folder_name in plot_settings['all_folder_names']:
        sim_names = all_sim_names_in_parallel_folder(folder_name)
        for sim_name in sim_names:
            mean_log_beta_distance_dict, log_beta_distance_dict, beta_distance_dict, beta_index_max, betas_max_gen_dict, \
            heat_caps_max_dict, smoothed_heat_caps = calc_heat_cap_param_main(sim_name, {}, gen_list=[generation])
            all_deltas.append(mean_log_beta_distance_dict[generation])
    return all_deltas


def plot(attrs_lists, plot_settings):
    if plot_settings['first_plot']:
        plt.figure(figsize=(10, 7))
    # colors = sns.color_palette("dark", len(attrs_lists))


    all_deltas = dynamic_regime_param_all_sims(plot_settings, plot_settings['color_according_to_delta_in_generation'])
    cmap = plt.get_cmap('brg')
    norm = colors_package.Normalize(vmin=min(all_deltas), vmax=max(all_deltas))
    if plot_settings['last_plot']:
        cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap))
        cbar.set_label(r'$\langle \delta \rangle$ at Generation 4000', rotation=270, labelpad=23)

    sim_names = all_sim_names_in_parallel_folder(plot_settings['folder_name'])
    deltas = []
    for sim_name in sim_names:
        mean_log_beta_distance_dict, log_beta_distance_dict, beta_distance_dict, beta_index_max, betas_max_gen_dict, \
        heat_caps_max_dict, smoothed_heat_caps = calc_heat_cap_param_main(sim_name, {}, gen_list=[plot_settings['color_according_to_delta_in_generation']])
        deltas.append(mean_log_beta_distance_dict[plot_settings['color_according_to_delta_in_generation']])
    print('Deltas:')
    print(deltas)
    print('all Deltas:')
    print(all_deltas)
    for attrs_list, delta in zip(attrs_lists, deltas):
        color = cmap(norm(delta))
        generations = np.arange(len(attrs_list))
        mean_attrs_list = [np.nanmean(gen_attrs) for gen_attrs in attrs_list]
        plt.scatter(generations, mean_attrs_list, s=1, alpha=0.085, c=color)
        if plot_settings['sliding_window']:
            slided_mean_attrs_list, slided_x_axis = slide_window(mean_attrs_list, plot_settings['sliding_window_size'])
            plt.plot(slided_x_axis, slided_mean_attrs_list, alpha=0.5, linewidth=2, c=color)
        if plot_settings['smooth']:
            '''
            Trying to make some sort of regression, that smoothes and interpolates 
            Trying to find an alternative to moving average, where boundary values are cut off
            '''
            # smoothed_mean_attrs_list = gaussian_kernel_smoothing(mean_attrs_list)
            # Savitzky-Golay filter:
            smoothed_mean_attrs_list = savgol_filter(mean_attrs_list, 201, 3) # window size, polynomial order
            # plt.plot(generations, smoothed_mean_attrs_list, c=color)

            # Uncommand the following, if interpolation shall be applied to smoothed data
            f_interpolate = interp1d(generations, smoothed_mean_attrs_list, kind='cubic')
            x_interp = np.linspace(np.min(generations), np.max(generations), num=4000, endpoint=True)
            y_interp = f_interpolate(x_interp)
            plt.plot(x_interp, y_interp, c=color, alpha=0.5, linewidth=2)

        # plt.scatter(generations, mean_attrs_list, s=20, alpha=1)
    plt.xlabel('Generation')
    # plt.ylabel(plot_settings['attr'])
    plt.ylabel(r'$\langle E_\mathrm{org} \rangle$')
    plt.ylim(plot_settings['ylim'])
    # plt.title(plot_settings['title'], color=plot_settings['title_color'])
    if plot_settings['legend'] and plot_settings['last_plot']:
        create_legend()


    if plot_settings['last_plot']:

        save_dir = 'save/{}/figs/several_plots{}/'.format(folder_name, plot_settings['add_save_name'])
        save_name = 'several_sims_criticial_{}{}_{}_min_ts{}_min_food{}_{}_all_in_one.png'. \
            format(plot_settings['attr'], plot_settings['only_copied_str'], plot_settings['folder_name'],
                   plot_settings['min_ts_for_plot'], plot_settings['min_food_for_plot'],
                   plot_settings['plot_generations_str'])
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        plt.savefig(save_dir+save_name, bbox_inches='tight', dpi=300)


def create_legend():
    legend_elements = [
        # Line2D([0], [0], marker='o', color='w', markerfacecolor='w', markersize=15, alpha=0.0001, label=r'$10$ Simulations'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='grey', markersize=15, alpha=0.75, label=r'One Generation'),
        Line2D([0], [0], color='b', lw=4, c='grey', alpha=0.7, label=r'One Simulation Smoothed'),
    ]

    plt.legend(handles=legend_elements, fontsize=18)



def load_attrs(folder_name, plot_settings):
    folder_dir = 'save/{}'.format(folder_name)
    dir_list = all_folders_in_dir_with(folder_dir, 'sim')
    attrs_list_all_sims = []
    settings_list = []
    for dir in dir_list:
        sim_name = dir[(dir.rfind('save/')+5):]
        settings = load_settings(sim_name)

        if plot_settings['only_plot_certain_generations']:
            load_generations = np.arange(plot_settings['lowest_and_highest_generations_to_be_plotted'][0],
                                         plot_settings['lowest_and_highest_generations_to_be_plotted'][1]+1)
            isings_list = load_isings_from_list(sim_name, load_generations, decompress=plot_settings['decompress'])
        else:
            isings_list = load_isings_specific_path('{}/isings'.format(dir), decompress=plot_settings['decompress'])

        if plot_settings['only_copied']:
            isings_list = [choose_copied_isings(isings) for isings in isings_list]
        if plot_settings['attr'] == 'norm_avg_energy' or plot_settings['attr'] == 'norm_food_and_ts_avg_energy':

            calc_normalized_fitness(isings_list, plot_settings, settings)

        isings_list = below_threshold_nan(isings_list, settings)
        attrs_list = [attribute_from_isings(isings, plot_settings['attr']) if isings is not None else np.nan
                      for isings in isings_list]
        attrs_list_all_sims.append(attrs_list)
        del isings_list
        # settings_list.append(load_settings(dir))
    return attrs_list_all_sims


def below_threshold_nan(isings_list, sim_settings):
    for i, isings in enumerate(isings_list):
        if isings[0].time_steps < plot_settings['min_ts_for_plot']:
            isings_list[i] = None
        if sim_settings['random_food_seasons']:
            if isings[0].food_in_env < plot_settings['min_food_for_plot']:
                isings_list[i] = None
    return isings_list

def slide_window(iterable, win_size):
    slided = []
    x_axis_gens = []
    n = 0
    while n+win_size < len(iterable)-1:
        mean = np.nanmean(iterable[n:n+win_size])
        slided.append(mean)
        x_axis_gens.append(n+int(win_size/2))
        n += 1
    return slided, x_axis_gens


if __name__ == '__main__':
    # folder_name = 'sim-20201020-181300_parallel_TEST'
    plot_settings = {}
    # Only plot loads previously saved plotting file instead of loading all simulations to save time
    plot_settings['only_plot'] = True
    plot_settings['decompress'] = True

    plot_settings['add_save_name'] = ''
    plot_settings['attr'] = 'avg_energy' #'norm_food_and_ts_avg_energy' #'norm_avg_energy'
    # plot_settings['only_plot_fittest']
    if plot_settings['attr'] == 'norm_food_and_ts_avg_energy':
        plot_settings['ylim'] = (-0.0001, 0.00025)
    else:
        plot_settings['ylim'] = (-0.001, 0.015)
    plot_settings['ylim'] = (-1, 40)
    # plot_settings['ylim'] = (-0.000001, 0.00007)

    # This only plots individuals that have not been mutated in previous generation (thus were fittest in previous generation)
    plot_settings['only_copied'] = True
    plot_settings['sliding_window'] = False
    plot_settings['smooth'] = True
    plot_settings['sliding_window_size'] = 100

    # ONLY PLOT HAS TO BE FALSE FOR FOLLOWING SETTINGS to work:
    plot_settings['min_ts_for_plot'] = 0
    plot_settings['min_food_for_plot'] = 0

    plot_settings['only_plot_certain_generations'] = False
    plot_settings['lowest_and_highest_generations_to_be_plotted'] = [0, 1000]
    plot_settings['title'] = ''
    plot_settings['legend'] = True

    # folder_names = ['sim-20201022-190625_parallel_b1_rand_seas_g4000_t2000', 'sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000', 'sim-20201022-190605_parallel_b1_rand_seas_g4000_t2000', 'sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000'] #
    # folder_names = ['sim-20201019-154142_parallel_parallel_mean_4000_ts_b1_rand_ts', 'sim-20201019-154106_parallel_parallel_mean_4000_ts_b1_fixed_ts', 'sim-20201019-153950_parallel_parallel_mean_4000_ts_b10_fixed_ts', 'sim-20201019-153921_parallel_parallel_mean_4000_ts_b10_rand_ts']
    # folder_names = ['sim-20201022-190625_parallel_b1_rand_seas_g4000_t2000', 'sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000', 'sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000']
    # folder_names = ['sim-20201026-224639_parallel_b1_fixed_4000ts_', 'sim-20201026-224655_parallel_b1_random_100-7900ts_', 'sim-20201026-224709_parallel_b10_fixed_4000ts_', 'sim-20201026-224722_parallel_b10_random_100-7900ts_', 'sim-20201026-224748_parallel_b1_fixed_POWER_ts', 'sim-20201026-224817_parallel_b10_fixed_POWER_ts', 'sim-20201028-185409_parallel_b1_rand_seas_g4000_t2000_lim_1_499', 'sim-20201028-185436_parallel_b10_rand_seas_g4000_t2000_lim_1_499', 'sim-20201102-220107_parallel_b1_rand_seas_g4000_t2000_fixed_250_foods', 'sim-20201102-220135_parallel_b10_rand_seas_g4000_t2000_fixed_250_foods', 'sim-20201105-202455_parallel_b1_random_ts_2000_lim_100_3900', 'sim-20201022-190553_parallel_b1_normal_seas_g4000_t2000', 'sim-20201022-190625_parallel_b1_rand_seas_g4000_t2000', 'sim-20201023-191408_parallel_b10_rand_seas_g4000_t2000']
    # folder_names = ['sim-20201105-202517_parallel_b10_random_ts_2000_lim_100_3900', 'sim-20201022-190615_parallel_b10_normal_seas_g4000_t2000']
    # folder_names = ['sim-20201210-200605_parallel_b1_dynamic_range_c_20_g4000_t2000_10_sims_HEL_ONLY_PLOT', 'sim-20201210-200613_parallel_b10_dynamic_range_c_20_g4000_t2000_10_sims_HEL_ONLY_PLOT', 'sim-20201211-211021_parallel_b0_1_dynamic_range_c_20_g4000_t2000_10_sims_HEL_ONLY_PLOT'] # sim-20201202-021347_parallel_b1_break_eat_v_eat_max_05_g4000_t2000_20_sims
    # folder_names = ['sim-20201210-200605_parallel_b1_dynamic_range_c_20_g4000_t2000_10_sims', 'sim-20201210-200613_parallel_b10_dynamic_range_c_20_g4000_t2000_10_sims', 'sim-20201211-211021_parallel_b0_1_dynamic_range_c_20_g4000_t2000_10_sims']
    # folder_names = ['sim-20201215-201024_parallel_b1_dynamic_range_c_20_g4000_t2000_10_sims_beta_jump_HEL_ONLY_PLOT', 'sim-20201215-201043_parallel_b10_dynamic_range_c_20_g4000_t2000_10_sims_beta_jump_HEL_ONLY_PLOT', 'sim-20201215-201011_parallel_b0_1_dynamic_range_c_20_g4000_t2000_10_sims_beta_jump_HEL_ONLY_PLOT']
    folder_names = ['sim-20201215-201024_parallel_b1_dynamic_range_c_20_g4000_t2000_10_sims_beta_jump', 'sim-20201215-201043_parallel_b10_dynamic_range_c_20_g4000_t2000_10_sims_beta_jump', 'sim-20201215-201011_parallel_b0_1_dynamic_range_c_20_g4000_t2000_10_sims_beta_jump']

    plot_settings['color_according_to_delta_in_generation'] = 4000
    init_betas = [1, 10, 0.1]
    title_colors = ['olive', 'royalblue', 'maroon']
    titles = [r'$\beta_\mathrm{init} = 1$', r'$\beta_\mathrm{init} = 10$', r'$\beta_\mathrm{init} = 0.1$']
    for i, (folder_name, title, title_color, init_beta) in enumerate(zip(folder_names, titles, title_colors, init_betas)):
        plot_settings['folder_name'] = folder_name
        plot_settings['title'] = title
        plot_settings['all_folder_names'] = folder_names
        plot_settings['init_beta'] = init_beta
        if i == 0:
            plot_settings['first_plot'] = True
        else:
            plot_settings['first_plot'] = False

        if i == len(folder_names) - 1:
            plot_settings['last_plot'] = True
        else:
            plot_settings['last_plot'] = False

        plot_settings['title_color'] = title_color
        main_plot_parallel_sims(folder_name, plot_settings)