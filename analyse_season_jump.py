import numpy as np
from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import load_isings
import matplotlib as plt

def extract_attr(isings_list, attr):
    val_list = []
    for isings in isings_list:
        for I in isings:
            exec('val_list.append(I.{})'.format(attr))
    return val_list

def load_trained_vals(trained_sim_name, attr, n_last_gens = 100):
    load_gens_trained = detect_all_isings(trained_sim_name)
    load_gens_trained = load_gens_trained[-(n_last_gens + 1):]
    trained_isings_list = load_isings_from_list(trained_sim_name, load_gens_trained)
    trained_vals = extract_attr(trained_isings_list, attr)
    # trained_avg = np.avg(trained_vals)
    # trained_std = np.std(trained_vals)
    return trained_vals

def load_switched_vals(switched_sim_name, attr):
    switched_isings_list = load_isings(switched_sim_name)
    switched_vals = extract_attr(switched_isings_list, attr)
    # switched_avg = np.avg(switched_vals)
    # switched_std = np.std(switched_vals)
    return switched_vals

def load_plot_data(trained_sim_names, switched_sim_names, attr):
    '''
    :param trained_sim_names: names of one parameter set
    :param switched_sim_names: names of one parameter set
    :return: all values of sets concatenated
    '''

    all_trained_vals = []
    for trained_sim_name in trained_sim_names:
        all_trained_vals += load_trained_vals(trained_sim_name, attr)
    # trained_avg = np.avg(all_trained_vals)
    # trained_std = np.std(all_trained_vals)

    all_switched_vals = []
    for switched_sim_name in switched_sim_names:
        all_switched_vals += load_switched_vals(switched_sim_name, attr)
    # switched_avg = np.avg(all_switched_vals)
    # switched_std = np.std(all_switched_vals)

    return all_trained_vals, all_switched_vals

# def plot(trained_sets, switched_sets):
#     trained_avgs = []
#     trained_stds = []
#     switched_avgs = []
#     switched_stds = []
#     for trained_set, switched_set in zip(trained_sets):
#         all_trained_vals, all_switched_vals = calc_plot_data(trained_set, switched_set)
#         trained_avgs.append(np.avg(all_trained_vals))
#         trained_stds.append(np.std(all_trained_vals))

def add_folder_name(sets, folder):
    new_sets = []
    for set in sets:
        new_set = []
        for sim_name in set:
            new_set.append(folder + sim_name)
        new_sets.append(new_set)
    return new_sets

def plot(trained_sets, switched_sets, attr, trained_folder = None, switched_folder = None ):
    if not trained_folder is None:
        trained_sets = add_folder_name(trained_sets, trained_folder)
        switched_sets = add_folder_name(switched_sets, switched_folder)

    data = []
    for trained_set, switched_set in zip(trained_sets, switched_sets):
        trained_vals, switched_vals = load_plot_data(trained_set, switched_set, attr)
        data.append(trained_vals)
        data.append(switched_vals)

    plt.boxplot(data)
    plt.show()

if __name__ == '__main__':
    trained_sets = [['sim-20200121-213309-ser_-cfg_2000_100_-b_1_-nmb',
                    'sim-20200121-213313-ser_-cfg_2000_100_-b_1_-nmb',
                    'sim-20200121-213321-ser_-cfg_2000_100_-b_1_-nmb',
                    'sim-20200121-213347-ser_-cfg_2000_100_-b_1_-nmb_-a_200_1999_2190',],
                    ['sim-20200121-213356-ser_-cfg_2000_100_-b_10_-nmb',
                     'sim-20200121-213400-ser_-cfg_2000_100_-b_10_-nmb',
                     'sim-20200121-213403-ser_-cfg_2000_100_-b_10_-nmb',
                     'sim-20200121-213424-ser_-cfg_2000_100_-b_10_-nmb_-a_200_1999_2190'],
                     ['sim-20200121-213437-ser_-f_10_-cfg_2000_100_-b_1_-nmb',
                      'sim-20200121-213441-ser_-f_10_-cfg_2000_100_-b_1_-nmb',
                      'sim-20200121-213446-ser_-f_10_-cfg_2000_100_-b_1_-nmb',
                      'sim-20200121-213458-ser_-f_10_-cfg_2000_100_-b_1_-nmb_-a_200_1999_2190'],
                    ['sim-20200121-213512-ser_-f_10_-cfg_2000_100_-b_10_-nmb',
                     'sim-20200121-213520-ser_-f_10_-cfg_2000_100_-b_10_-nmb',
                     'sim-20200121-213524-ser_-f_10_-cfg_2000_100_-b_10_-nmb',
                     'sim-20200121-213537-ser_-f_10_-cfg_2000_100_-b_10_-nmb_-a_200_1999_2190'
                     ]]


    # switched_sets = [[
    #
    #                 'sim-20200129-212115-ser_-b_1_-f_10_-r_200_-li_1999_-a_5_-l_sim-20200121-213347-ser_-cfg_2000_100_-b_1_-nmb_-a_200_1999_2190',
    #                 'sim-20200129-212115-ser_-b_1_-f_10_-r_200_-li_1999_-l_sim-20200121-213309-ser_-cfg_2000_100_-b_1_-nmb',
    #                 'sim-20200129-212115-ser_-b_1_-f_10_-r_200_-li_1999_-l_sim-20200121-213313-ser_-cfg_2000_100_-b_1_-nmb',
    #                 'sim-20200129-212115-ser_-b_1_-f_10_-r_200_-li_1999_-l_sim-20200121-213321-ser_-cfg_2000_100_-b_1_-nmb'],
    #                 ['sim-20200129-212115-ser_-f_100_-b_10_-r_200_-li_1999_-a_5_-l_sim-20200121-213537-ser_-f_10_-cfg_2000_100_-b_10_-nmb_-a_200_1999_2190',
    #                 'sim-20200129-212115-ser_-f_100_-b_10_-r_200_-li_1999_-l_sim-20200121-213512-ser_-f_10_-cfg_2000_100_-b_10_-nmb',
    #                 'sim-20200129-212115-ser_-f_100_-b_10_-r_200_-li_1999_-l_sim-20200121-213520-ser_-f_10_-cfg_2000_100_-b_10_-nmb',
    #                 'sim-20200129-212115-ser_-f_100_-b_10_-r_200_-li_1999_-l_sim-20200121-213524-ser_-f_10_-cfg_2000_100_-b_10_-nmb'],
    #                 ['sim-20200129-212115-ser_-f_100_-b_1_-r_200_-li_1999_-a_5_-l_sim-20200121-213424-ser_-cfg_2000_100_-b_10_-nmb_-a_200_1999_2190',
    #                 'sim-20200129-212115-ser_-f_100_-b_1_-r_200_-li_1999_-l_sim-20200121-213403-ser_-cfg_2000_100_-b_10_-nmb',
    #                 'sim-20200129-212115-ser_-f_100_-b_1_-r_200_-li_1999_-l_sim-20200121-213437-ser_-f_10_-cfg_2000_100_-b_1_-nmb',
    #                 'sim-20200129-212115-ser_-f_100_-b_1_-r_200_-li_1999_-l_sim-20200121-213441-ser_-f_10_-cfg_2000_100_-b_1_-nmb'],
    #                 ['sim-20200129-212115-ser_-f_10_-b_10_-r_200_-li_1999_-l_sim-20200121-213356-ser_-cfg_2000_100_-b_10_-nmb',
    #                 'sim-20200129-212115-ser_-f_10_-b_10_-r_200_-li_1999_-l_sim-20200121-213400-ser_-cfg_2000_100_-b_10_-nmb',
    #                 'sim-20200129-212115-ser_-f_10_-b_10_-r_200_-li_1999_-l_sim-20200121-213403-ser_-cfg_2000_100_-b_10_-nmb',]]

    switched_sets = [['sim-20200130-205401-ser_-b_1_-f_10_-r_200_-li_1999_-a_5_-l_sim-20200121-213347-ser_-cfg_2000_100_-b_1_-nmb_-a_200_1999_2190',
                    'sim-20200130-205401-ser_-b_1_-f_10_-r_200_-li_1999_-l_sim-20200121-213309-ser_-cfg_2000_100_-b_1_-nmb',
                    'sim-20200130-205401-ser_-b_1_-f_10_-r_200_-li_1999_-l_sim-20200121-213313-ser_-cfg_2000_100_-b_1_-nmb',
                    'sim-20200130-205401-ser_-b_1_-f_10_-r_200_-li_1999_-l_sim-20200121-213321-ser_-cfg_2000_100_-b_1_-nmb'],
                    ['sim-20200130-205401-ser_-f_100_-b_10_-r_200_-li_1999_-a_5_-l_sim-20200121-213537-ser_-f_10_-cfg_2000_100_-b_10_-nmb_-a_200_1999_2190',
                    'sim-20200130-205401-ser_-f_100_-b_10_-r_200_-li_1999_-l_sim-20200121-213512-ser_-f_10_-cfg_2000_100_-b_10_-nmb',
                    'sim-20200130-205401-ser_-f_100_-b_10_-r_200_-li_1999_-l_sim-20200121-213520-ser_-f_10_-cfg_2000_100_-b_10_-nmb',
                    'sim-20200130-205401-ser_-f_100_-b_10_-r_200_-li_1999_-l_sim-20200121-213524-ser_-f_10_-cfg_2000_100_-b_10_-nmb',
                    'sim-20200130-205401-ser_-f_100_-b_1_-r_200_-li_1999_-a_5_-l_sim-20200121-213458-ser_-f_10_-cfg_2000_100_-b_1_-nmb_-a_200_1999_2190'],
                    ['sim-20200130-205401-ser_-f_100_-b_1_-r_200_-li_1999_-l_sim-20200121-213437-ser_-f_10_-cfg_2000_100_-b_1_-nmb',
                    'sim-20200130-205401-ser_-f_100_-b_1_-r_200_-li_1999_-l_sim-20200121-213441-ser_-f_10_-cfg_2000_100_-b_1_-nmb',
                    'sim-20200130-205401-ser_-f_100_-b_1_-r_200_-li_1999_-l_sim-20200121-213446-ser_-f_10_-cfg_2000_100_-b_1_-nmb',
                    'sim-20200130-205401-ser_-f_10_-b_10_-r_200_-li_1999_-a_5_-l_sim-20200121-213424-ser_-cfg_2000_100_-b_10_-nmb_-a_200_1999_2190'],
                    ['sim-20200130-205401-ser_-f_10_-b_10_-r_200_-li_1999_-l_sim-20200121-213356-ser_-cfg_2000_100_-b_10_-nmb',
                    'sim-20200130-205401-ser_-f_10_-b_10_-r_200_-li_1999_-l_sim-20200121-213400-ser_-cfg_2000_100_-b_10_-nmb',
                    'sim-20200130-205401-ser_-f_10_-b_10_-r_200_-li_1999_-l_sim-20200121-213403-ser_-cfg_2000_100_-b_10_-nmb']]
    trained_folder = 'seasons_training_one_season/'
    switched_folder = 'season_switch_repeat_scenarios/'

    attr = 'avg_energy'
    plot(trained_sets, switched_sets, attr, trained_folder, switched_folder)







# def analyse(trained_sim_name, switched_sim_name, n_last_gens = 100):
#     load_gens_trained = detect_all_isings(trained_sim_name)
#     load_gens_trained = load_gens_trained[-(n_last_gens+1)]
#     trained_isings_list = load_isings_from_list(trained_sim_name, load_gens_trained)
#     switched_isings_list = load_isings(switched_sim_name)
#     trained_vals = extract_attr(trained_isings_list, 'avg_energy')
#     switched_vals = extract_attr(switched_isings_list, 'avg_energy')
#     trained_avg = np.avg(trained_vals)
#     switched_avg = np.avg(switched_vals)


