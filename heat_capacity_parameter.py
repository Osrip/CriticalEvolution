import numpy as np
import os
from automatic_plot_helper import load_settings
from scipy.signal import find_peaks


def calc_heat_cap_param_main(sim_name, module_settings, gen_list=None):
    '''
    @param gen_list: List of generations, to calculate heat capacity parameter for. Heat capacity has to be calculated
    for those generations. If None, automatically detects all generations, that heat capacity data has been calculated
    for.
    @return:  Returns mean dynamic range parameter over generation, dynamic range parameter dynamic range parameter, non-log dynamic range parameter, index of max beta value,
     beta value where heat cap max, heat cap max
     All as dictionaries with the generation being the key
    '''

    folder = 'save/' + sim_name
    if gen_list is None:
        gen_list = automatic_generation_generation_list(folder + '/C_recorded')

    settings = load_settings(sim_name)
    C, betas = load_heat_cap_files(sim_name, settings, gen_list)
    betas_max_gen_dict, heat_caps_max_dict, beta_index_max = calc_max(C, betas, gen_list, module_settings)

    log_beta_distance_dict, beta_distance_dict = calculate_beta_distance_parameter(betas_max_gen_dict)

    mean_log_beta_distance_dict = {k: np.mean(v) for k, v in log_beta_distance_dict.items()}

    return mean_log_beta_distance_dict, log_beta_distance_dict, beta_distance_dict, beta_index_max, betas_max_gen_dict, heat_caps_max_dict


def calc_max(C, betas, gen_list, module_settings):
    betas_max_gen_dict = {}
    heat_caps_max_dict = {}
    for i_gen in range(np.shape(C)[3]):
        gen = gen_list[i_gen]
        betas_max_one_gen = []
        heat_caps_max_one_gen = []
        for i_agent in range(np.shape(C)[1]):
            heat_caps = np.mean(C[:, i_agent, :, i_gen], axis=0)
            # Finding the peak
            # if module_settings['use_argmax_to_find_peak']:
            beta_index_max = np.argmax(heat_caps)
            heat_cap_max = np.max(heat_caps)
            # else:
            #     beta_index_max, _ = find_peaks(heat_caps, height=0) # Find all peaks
            #     beta_index_max = beta_index_max[np.argmax(_['peak_heights'])] # this is the index on the x-axis for the peak

            beta_max = betas[beta_index_max]
            betas_max_one_gen.append(beta_max)
            heat_caps_max_one_gen.append(heat_cap_max)

        betas_max_gen_dict[gen] = betas_max_one_gen
        heat_caps_max_dict[gen] = heat_caps_max_one_gen
    return betas_max_gen_dict, heat_caps_max_dict, beta_index_max

    # index,_  = find_peaks(f, height=0);
    # index = index[np.argmax(_['peak_heights'])] # this is the index on the x-axis for the peak
    # plt.plot(f); plt.plot(index, f[int(index)], '.')


def calculate_beta_distance_parameter(betas_max_gen_dict):
    '''
    This function calculates the dynamic range parameter log_beta_distance as well as its non logarithmic equivalent
    It assumes criticality at beta factor = 1
    '''
    beta_distance_dict = {}
    log_beta_distance_dict = {}
    for gen in betas_max_gen_dict:
        betas_max_one_gen = betas_max_gen_dict[gen]
        beta_distances = []
        log_beta_distances = []
        for beta_max in betas_max_one_gen:

            # Core operations of this function
            beta_distance = beta_max - 1.0
            log_beta_distance = np.log10(beta_max)  # we can just take log, as log(beta_crit = 1.0) = 0

            beta_distances.append(beta_distance)
            log_beta_distances.append(log_beta_distance)
        beta_distance_dict[gen] = beta_distances
        log_beta_distance_dict[gen] = log_beta_distances
    return log_beta_distance_dict, beta_distance_dict


def load_heat_cap_files(sim_name, settings, gen_list):
    folder = 'save/' + sim_name

    R, thermal_time, beta_low, beta_high, beta_num, y_lim_high = settings['heat_capacity_props']
    #R = 10
    Nbetas = beta_num
    betas = 10 ** np.linspace(beta_low, beta_high, Nbetas)
    numAgents = settings['pop_size']
    size = settings['size']



    # C[repeat, agent number, index of curr beta value, generation]
    C = np.zeros((R, numAgents, Nbetas, len(gen_list)))

    print('Loading data...')
    for i_gen, gen in enumerate(gen_list):
        #for bind in np.arange(0, 100):
        for bind in np.arange(1, Nbetas):
            #  Depending on whether we are dealing with recorded or dream heat capacity
            filename = folder + '/C_recorded/C_' + str(gen) + '/C-size_' + str(size) + '-Nbetas_' + \
                       str(Nbetas) + '-bind_' + str(bind) + '.npy'
            C[:, :, bind, i_gen] = np.load(filename)
    print('Done.')
    return C, betas


def automatic_generation_generation_list(C_folder):
    C_gen_folders = [f.path for f in os.scandir(C_folder) if f.is_dir()]
    generation_list = get_generations(C_gen_folders)
    return generation_list


def get_generations(C_gen_folders):
    generation_list = []
    for C_gen_folder in C_gen_folders:
        if RepresentsInt(C_gen_folder.split('_')[-1]) is True:
            generation_list.append(C_gen_folder.split('_')[-1])
    return generation_list


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    module_settings = {}
    sim_name = 'sim-20201207-145420-g_2_-b_10_-t_20_-rec_c_1_-c_props_100_10_-2_2_100_40_-c_20_-noplt_-n_heat_cap_TEST_default_setup'
    # 'sim-20201204-203157-g_2_-t_20_-rec_c_1_-c_props_100_10_-2_2_100_40_-c_20_-noplt_-n_heat_cap_test_default_setup' #
    gen_list = None

    # the findmax function seems to give the exact same results as the find max function
    # module_settings['use_argmax_to_find_peak'] = True

    calc_heat_cap_param_main(sim_name, module_settings, gen_list)