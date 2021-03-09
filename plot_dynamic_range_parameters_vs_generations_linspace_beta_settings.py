import matplotlib
matplotlib.use('Agg')
from automatic_plot_helper import all_sim_names_in_parallel_folder
from heat_capacity_parameter import calc_heat_cap_param_main
from scipy.interpolate import interp1d
import numpy as np
# from statsmodels.nonparametric.kernel_regression import KernelReg
from scipy.signal import savgol_filter

import matplotlib.pyplot as plt
import os
import pickle
import seaborn as sns
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.colors as colors_package
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.cm as cm

def main_plot_parallel_sims(folder_name, plot_settings):
    plt.rc('text', usetex=True)
    font = {'family': 'serif', 'size': 18, 'serif': ['computer modern roman']}
    plt.rc('font', **font)

    if not plot_settings['only_plot']:
        attrs_lists = load_dynamic_range_param(folder_name, plot_settings)
        save_plot_data(folder_name, attrs_lists, plot_settings)
    else:
        attrs_lists = load_plot_data(folder_name, plot_settings)
    delta_dicts_all_sims, deltas_dicts_all_sims = attrs_lists
    plot(delta_dicts_all_sims, deltas_dicts_all_sims, plot_settings)


def save_plot_data(folder_name, attrs_lists, plot_settings):
    save_dir = 'save/{}/one_pop_plot_data/'.format(folder_name)
    save_name = 'plot_dynamic_range_param_data.pickle'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    pickle_out = open(save_dir + save_name, 'wb')
    pickle.dump(attrs_lists, pickle_out)
    pickle_out.close()


def load_plot_data(folder_name, plot_settings):
    save_dir = 'save/{}/one_pop_plot_data/'.format(folder_name)
    save_name = 'plot_dynamic_range_param_data.pickle'
    print('Load plot data from: {}{}'.format(save_dir, save_name))

    file = open(save_dir+save_name, 'rb')
    attrs_lists = pickle.load(file)
    file.close()

    return attrs_lists


def create_legend():
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='grey', markersize=15, alpha=0.75, label=r'One Generation'),

    ]
    if plot_settings['smooth']:
        legend_elements.append(Line2D([0], [0], color='b', lw=4, c='grey', alpha=0.7, label='One Simulation\nSmoothed'))
    elif plot_settings['interpolate']:
        legend_elements.append(Line2D([0], [0], color='b', lw=4, c='grey', alpha=0.7, label='One Simulation\nInterpolated'))
    elif plot_settings['plot_line']:
        legend_elements.append(Line2D([0], [0], color='b', lw=4, c='grey', alpha=0.7, label='One Simulation'))

    plt.legend(handles=legend_elements, fontsize=17)


def colormap_according_to_delta(delta_dicts_all_sims, generation, plot_settings):
    delta_list_one_gen = []
    for delta_dict in delta_dicts_all_sims:
        # delta dict: mean delta of each generation

        delta_one_gen = delta_dict[str(generation)]
        delta_list_one_gen.append(delta_one_gen)

    colors = [plot_settings['colors']['b10'], plot_settings['colors']['b1'], plot_settings['colors']['b01']]
    cmap_name = 'custom_cmap'
    # cmap = plt.get_cmap('brg')
    cmap = LinearSegmentedColormap.from_list(
        cmap_name, colors)
    norm = colors_package.Normalize(vmin=min(delta_list_one_gen), vmax=max(delta_list_one_gen))
    return cmap, norm




def plot(delta_dicts_all_sims, deltas_dicts_all_sims, plot_settings):
    if plot_settings['new_fig']:
        plt.figure(figsize=(10, 7))
        ax = plt.subplot()
        plt.grid()
    # plt.rcParams.update({
    #     'ytick.right': True,
    #     "ytick.labelright": True
    # })

    cmap, norm = colormap_according_to_delta(delta_dicts_all_sims, plot_settings['color_according_to_delta_in_generation'],
                                             plot_settings)


    for delta_dict, deltas_dict in zip(delta_dicts_all_sims, deltas_dicts_all_sims):
        # delta dict: mean delta of each generation
        # deltas_dict: delta of every individual


        # Handle delta dict, which includes mean delta of each generation
        generations = list(delta_dict.keys())
        generations = np.array([int(gen) for gen in generations])
        sorted_gen_indecies = np.argsort(generations)
        generations = np.sort(generations)
        mean_attrs_list = np.array(list(delta_dict.values()))
        mean_attrs_list = mean_attrs_list[sorted_gen_indecies]

        # Handle deltas dict, which includes list of delta of each individual in a generation
        generations_ind = list(deltas_dict.keys())
        generations_ind = np.array([int(gen) for gen in generations_ind])
        sorted_gen_indecies_ind = np.argsort(generations_ind)
        generations_ind = np.sort(generations_ind)
        mean_attrs_list_ind = np.array(list(deltas_dict.values()))
        mean_attrs_list_ind = mean_attrs_list_ind[sorted_gen_indecies_ind]
        # We have a list of delta values for each generation. Unnest the lists and repeat the generations for each
        # individual, such that lists have same dimensions for plotting
        generations_unnested_ind = []
        mean_attr_list_ind_unnested = []
        for gen_ind, mean_attr_list_ind in zip(generations_ind, mean_attrs_list_ind):
            for mean_attr_ind in mean_attr_list_ind:
                generations_unnested_ind.append(gen_ind)
                mean_attr_list_ind_unnested.append(mean_attr_ind)



        curr_color_delta= delta_dict[str(plot_settings['color_according_to_delta_in_generation'])]
        color = cmap(norm(curr_color_delta))




        if plot_settings['plot_line']:
            '''
            Trying to make some sort of regression, that smoothes and interpolates 
            Trying to find an alternative to moving average, where boundary values are cut off
            '''
            # smoothed_mean_attrs_list = gaussian_kernel_smoothing(mean_attrs_list)
            # Savitzky-Golay filter:
            if plot_settings['smooth']:
                smoothed_mean_attrs_list = savgol_filter(mean_attrs_list, plot_settings['smooth_window'], 3) # window size, polynomial order
            else:
                smoothed_mean_attrs_list = mean_attrs_list
            # plt.plot(generations, smoothed_mean_attrs_list, c=color)


            if plot_settings['interpolate']:
                f_interpolate = interp1d(generations, smoothed_mean_attrs_list, kind='cubic')
                x_interp = np.linspace(np.min(generations), np.max(generations), num=4000, endpoint=True)
                y_interp = f_interpolate(x_interp)
                plt.plot(x_interp, y_interp, c=color, alpha=plot_settings['line_alpha'])
            else:
                plt.plot(generations, smoothed_mean_attrs_list, c=color, alpha=plot_settings['line_alpha'])






        if plot_settings['plot_deltas_of_individuals']:
            plt.scatter(generations_unnested_ind,  mean_attr_list_ind_unnested, s=2, alpha=0.2, c=color)

        plt.scatter(generations, mean_attrs_list, s=5, alpha=0.4, c=color, marker='.')

        if plot_settings['sliding_window']:
            slided_mean_attrs_list = moving_average(mean_attrs_list, plot_settings['sliding_window_size'])
            plt.plot(generations, slided_mean_attrs_list, alpha=0.8, linewidth=2, c=color)


    plt.xlabel('Generation')
    plt.ylabel(r'$\langle \delta \rangle$')
    plt.ylim(plot_settings['ylim'])

    cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap))
    cbar.set_label(r'$\langle \delta \rangle$ at Generation 0', rotation=270, labelpad=23)


    # plt.text(-200, 1, 'hallo', fontsize=14)
    # plt.subplots_adjust(left=0.9)



    # plt.title(r'$\beta_\mathrm{init}=%s$' % plot_settings['beta_init_for_title'])

    if plot_settings['plot_legend']:
        create_legend()

    if plot_settings['new_fig']:
        pad = -20
        color = 'dimgray'
        ax.annotate('Super-\nCritical', xy=(0, 1.5), xytext=(-ax.yaxis.labelpad - pad, 155),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    size=15, ha='right', va='center', rotation=0, color=color)
        ax.annotate('Critical', xy=(0, 1.5), xytext=(-ax.yaxis.labelpad - pad, 5),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    size=15, ha='right', va='center', rotation=0, color=color)
        ax.annotate('Sub-\nCritical', xy=(0, 1.5), xytext=(-ax.yaxis.labelpad - pad, -145),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    size=15, ha='right', va='center', rotation=0, color=color)

    if plot_settings['save_fig']:


        save_dir = 'save/{}/figs/several_plots{}/'.format(folder_name, plot_settings['add_save_name'])
        save_name = 'delta_vs_generations_all_in_one.png'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        plt.savefig(save_dir+save_name, bbox_inches='tight', dpi=300)


def load_dynamic_range_param(folder_name, plot_settings):
    folder_dir = 'save/{}'.format(folder_name)
    sim_names = all_sim_names_in_parallel_folder(folder_name)
    delta_dicts_all_sims = []
    deltas_dicts_all_sims = []
    for sim_name in sim_names:
        module_settings = {}
        mean_log_beta_distance_dict, log_beta_distance_dict, beta_distance_dict, beta_index_max, betas_max_gen_dict, \
        heat_caps_max_dict, smoothed_heat_caps = calc_heat_cap_param_main(sim_name, module_settings, gaussian_kernel=plot_settings['gaussian_kernel'])
        delta_dict = mean_log_beta_distance_dict
        delta_list_dict = log_beta_distance_dict
        delta_dicts_all_sims.append(delta_dict)
        deltas_dicts_all_sims.append(delta_list_dict)


        # settings_list.append(load_settings(dir))
    # delta_dicts_all_sims --> men of each generation, deltas_dicts_all_sims --> each individual in a list
    return (delta_dicts_all_sims, deltas_dicts_all_sims)


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


def gaussian(x, mu, sigma):

    C = 1 / (sigma * np.sqrt(2*np.pi))

    return C * np.exp(-1/2 * (x - mu)**2 / sigma**2)

def gaussian_kernel_smoothing(x):
    '''
    Convolving with gaussian kernel in order to smoothen noisy heat cap data (before eventually looking for maximum)
    '''

    # gaussian kernel with sigma=2.25. mu=0 means, that kernel is centered on the data
    # kernel = gaussian(np.linspace(-3, 3, 15), 0, 2.25)
    kernel = gaussian(np.linspace(-3, 3, 15), 0, 6)
    smoothed_x = np.convolve(x, kernel, mode='same')
    return smoothed_x


def moving_average(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')

if __name__ == '__main__':
    # folder_name = 'sim-20201020-181300_parallel_TEST'
    plot_settings = {}
    # Only plot loads previously saved plotting file instead of loading all simulations to save time
    plot_settings['only_plot'] = True

    plot_settings['add_save_name'] = ''
    # plot_settings['only_plot_fittest']

    plot_settings['ylim'] = (-1.8, 1.1) #(-1.5, 1.1)
    # This only plots individuals that have not been mutated in previous generation (thus were fittest in previous generation)
    plot_settings['sliding_window'] = False
    plot_settings['sliding_window_size'] = 10

    # smooth works only if plot_settings['interpolate'] = True
    plot_settings['plot_line'] = True
    plot_settings['smooth'] = True
    plot_settings['interpolate'] = True
    plot_settings['smooth_window'] = 7  # 21
    plot_settings['line_alpha'] = 0.6  # beta jump 0.4 # normal 0.6

    plot_settings['plot_deltas_of_individuals'] = False

    plot_settings['gaussian_kernel'] = True

    plot_settings['kernel_regression'] = False
    plot_settings['color_according_to_delta_in_generation'] = 0

    plot_settings['colors'] = {'b1': 'olive', 'b01': 'maroon', 'b10': 'royalblue'}

    beta_inits = [1, 10, 0.1]
    # folder_names = ['sim-20201210-200605_parallel_b1_dynamic_range_c_20_g4000_t2000_10_sims_HEL_ONLY_PLOT', 'sim-20201210-200613_parallel_b10_dynamic_range_c_20_g4000_t2000_10_sims_HEL_ONLY_PLOT', 'sim-20201211-211021_parallel_b0_1_dynamic_range_c_20_g4000_t2000_10_sims_HEL_ONLY_PLOT']
    # folder_names = ['sim-20201210-200605_parallel_b1_dynamic_range_c_20_g4000_t2000_10_sims', 'sim-20201210-200613_parallel_b10_dynamic_range_c_20_g4000_t2000_10_sims', 'sim-20201211-211021_parallel_b0_1_dynamic_range_c_20_g4000_t2000_10_sims']
    # folder_names = ['sim-20201215-201024_parallel_b1_dynamic_range_c_20_g4000_t2000_10_sims_beta_jump_HEL_ONLY_PLOT', 'sim-20201215-201043_parallel_b10_dynamic_range_c_20_g4000_t2000_10_sims_beta_jump_HEL_ONLY_PLOT', 'sim-20201215-201011_parallel_b0_1_dynamic_range_c_20_g4000_t2000_10_sims_beta_jump_HEL_ONLY_PLOT']
    # folder_names = ['sim-20201226-002401_parallel_beta_linspace_rec_c40_30_sims_HEL_ONLY_PLOT']
    folder_names = ['sim-20201226-002401_parallel_beta_linspace_rec_c40_30_sims']
    # folder_names = ['sim-20210216-210708_parallel_beta_linspace_rec_c100_10_sims_no_mut_beta']
    regimes = ['b1']
    plot_settings['last_sim'] = False
    for i, (folder_name, beta_init, regime) in enumerate(zip(folder_names, beta_inits, regimes)):
        plot_settings['regime'] = regime
        plot_settings['folder_name'] = folder_name
        plot_settings['beta_init_for_title'] = beta_init

        plot_settings['new_fig'] = True

        plot_settings['plot_legend'] = True
        plot_settings['save_fig'] = True


        main_plot_parallel_sims(folder_name, plot_settings)