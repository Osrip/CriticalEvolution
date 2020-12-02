import numpy as np
import os
from automatic_plot_helper import load_settings
from scipy.signal import find_peaks

def calc_heat_cap_param_main(sim_name, gen_list=None):
    settings = load_settings(sim_name)
    C = load_heat_cap_files(sim_name, settings, gen_list)


def calc_max():

    f = C[agent_index] ## this is the specific heat curve (shape = [1, 101]) for one agent

    index,_  = find_peaks(f, height=0);
    index = index[np.argmax(_['peak_heights'])] # this is the index on the x-axis for the peak
    plt.plot(f); plt.plot(index, f[int(index)], '.')

def load_heat_cap_files(sim_name, settings, gen_list):
    folder = 'save/' + sim_name

    R, thermal_time, beta_low, beta_high, beta_num, y_lim_high = settings['heat_capacity_props']
    #R = 10
    Nbetas = beta_num
    betas = 10 ** np.linspace(beta_low, beta_high, Nbetas)
    numAgents = settings['pop_size']
    size = settings['size']

    if gen_list is None:
        gen_list = automatic_generation_generation_list(folder + '/C_recorded')

    # TODO: Repeat averaging seems to work
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
    return C

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