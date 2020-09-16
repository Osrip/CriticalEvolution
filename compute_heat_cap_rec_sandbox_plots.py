#!/usr/bin/env python

from embodied_ising import ising
import numpy as np
from sys import argv
from os import path, makedirs

import pickle
import random
import glob
from numba import jit
from automatic_plot_helper import load_settings
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import signal
import matplotlib.colors as colors
from scipy import fft, arange
from scipy import fftpack
from ising_net_fitness_landscape import all_states
from ising_net_fitness_landscape import calculate_energies

# --- COMPUTE HEAT CAPACITY -------------------------------------------------------+
def main():
    if len(argv) < 3:
        print("Usage: " + argv[0] + " <sim> + <bind> + <gen>")
        # loadfile = 'sim-20180131-145412'
        # bind = 0  POsition in BetaVec
        # iterNum = 0

    loadfile = str(argv[1])

    bind = int(argv[2]) #beta index
    iterNum = int(argv[3]) #Generation numbers

    settings = load_settings(loadfile)

    R, thermal_time, beta_low, beta_high, y_lim_high = settings['heat_capacity_props']

    #R = 100 # Number of Repetitions, each initialising with new recorded sensor value
    mode = 'MonteCarlo'

    #Is there a bug here? Nbetas = 101 originally Nbetas = 102 solves index error?
    Nbetas = 102
    betas = 10 ** np.linspace(beta_low, beta_high, Nbetas)
    loadstr = 'save/' + loadfile +  '/isings/gen[' + str(iterNum) + ']-isings.pickle'

    # print(iterNum)
    file = open(loadstr, 'rb')
    isings = pickle.load(file)
    file.close()

    size = isings[0].size # get size from first agent
    numAgents = len(isings)

    C = np.zeros((R, numAgents))
    # tqdm(range(R))
    for rep in range(R):
        # filename = 'files/mode_' + mode + '-size_' + \
        #            str(size) + '-ind_' + str(rep) + '.npz'
        # filename = 'parameters.npz'
        # data = np.load(filename)
        # I = ising(size)
        # I.h = data['h'][()][(size, rep)]
        # I.J = data['J'][()][(size, rep)]

        agentNum = 0
        all_Es = []
        all_Es_permuts = []
        all_step_Es = []
        for I in isings:

            #TimeSteps in dream simulation T = 100000

            betaVec = betas * I.Beta  # scale by org's local temperature
            # print(agentNum)
            beta_new = betaVec[bind]

            #I.randomize_state()
            #  Initialize sensors with randoms set of sensor values that have been recorded during simulation
            initialize_sensors_from_record_randomize_neurons(I)

            # Initialize lowest energy state
            if False:
                sensor_vals = I.s[0:(settings['nSensors'])]
                permutated_states, permutated_states_with_sensors = all_states(I, settings, sensor_vals)
                energies_perm = calculate_energies(I, settings, permutated_states_with_sensors)
                i_min_energy = np.argmin(energies_perm)
                min_energy_state = permutated_states_with_sensors[i_min_energy]
                I.s = np.array(min_energy_state)


            # Thermalosation to equilibrium before making energy measurements
            #TODO LEave thermalization to equilibrium away before measurement? int(thermal_time/10)
            # I.s = SequentialGlauberStepFast(1000, I.s, I.h, I.J, I.Beta, I.Ssize, I.size)

            #  Measuring energy between Glaubersteps
            I.s, Em, E2m, all_E, all_E_permuts = SequentialGlauberStepFast_calc_energy(thermal_time, I.s, I.h, I.J, beta_new, I.Ssize, I.size)
            all_Es.append(all_E)
            all_Es_permuts.append(all_E_permuts)
            #Old, slow way of clculating it:
            # for t in range(int(T / 10)):
            #     #  thermal time steps to get ANN to equilibrium
            #     I.DreamSensorGlauberStep()

            # for t in range(T):
            #     #  thermal time steps, where Ennergy is recorded
            #     I.DreamSensorGlauberStep()
            #     ### Add these 3 lines o embodied ising for natural heat capacity
            #
            #     E = -(np.dot(I.s, I.h) + np.dot(np.dot(I.s, I.J), I.s))
            #     Em += E / float(T)   # <-- mean calculation??
            #     E2m += E ** 2 / float(T)
            #     # Why is this divided by T (total amount of time steps after thermalization)? --> mean calculation

            #  Claculate heat capacity
            c = beta_new ** 2 * (E2m - Em ** 2) / size
            C[rep, agentNum] = c

            agentNum += 1


    # print(np.mean(C, 0))
    # TODO: CHANGE THIS SO THERE IS NO CONFLICT WITH OTHER DREAM HEAT CAP CALCULATION
    folder = 'save/' + loadfile + '/C_recorded' + '/C_' + str(iterNum) + '/'
    file = 'C-size_' + str(size) + '-Nbetas_' + \
           str(Nbetas) + '-bind_' + str(bind) + '.npy'
    filename = folder + file

    if not path.exists(folder):
        makedirs(folder)


    super_threshold_indices = C <= 0
    C[super_threshold_indices] = 1* 10 ** -10

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label=r'$C/N \leq 0.1$', markerfacecolor='blue',
               markersize=25, alpha=0.75),
        Line2D([0], [0], marker='o', color='w', label='$C/N > 0.1$', markerfacecolor='red',
               markersize=25, alpha=0.75)
    ]

    # I think plotting only works for 1 REPEAT!!!
    plot_c(C[0], betas[bind], loadfile, legend_elements)
    plot_all_E(all_Es, C[0], loadfile, legend_elements, betas[bind], all_permutations=False)
    plot_all_E(all_Es_permuts, C[0], loadfile, legend_elements, betas[bind], all_permutations=True)

    plot_power_spectrum(all_Es_permuts[0], loadfile, betas[bind])
    plotSpectrum(all_Es_permuts[0], loadfile, betas[bind])



def initialize_sensors_from_record_randomize_neurons(I):
    '''
    Initialize sensors with randoms set of sensor values that have been recorded during simulation
    Randomize all other neurons
    '''
    s = np.random.randint(0, 2, I.size) * 2 - 1
    s = np.array(s, dtype=float)
    #all_recorded_inputs = from_list_of_arrs_to_arr(I.all_recorded_inputs)
    rand_index = random.randint(0, len(I.all_recorded_inputs)-1)
    chosen_sens_inputs = I.all_recorded_inputs[rand_index]
    for i in range(len(chosen_sens_inputs)):
        I.s[i] = chosen_sens_inputs[i]

    I.s = s
    if not len(chosen_sens_inputs) == I.Ssize:
        raise Exception('''For some reason the number of sensors that
        recorded values exist for is different from the sensor size saved in the settings''')

@jit(nopython=True)
def SequentialGlauberStepFast_calc_energy(thermalTime, s, h, J, Beta, Ssize, size):
    '''
    Energy calculation each thermal time step
    '''
    # TODO: After figuring the effect of thermalize sensors out delete this shit, slows everything down!
    thermalize_sensors = False

    if thermalize_sensors:
        all_neurons_except_sens = np.arange(0, size)
    else:
        all_neurons_except_sens = np.arange(Ssize, size)
    #perms_list = np.array([np.random.permutation(np.arange(Ssize, size)) for j in range(thermalTime)])
    random_vars = np.random.rand(thermalTime, len(all_neurons_except_sens)) #[np.random.rand() for i in perms]

    Em = 0
    E2m = 0
    all_E = []
    all_E_permuts = []
    for i in range(thermalTime):
        #perms = perms_list[i]
        #Prepare a matrix of random variables for later use

        # TODO: In previous dream heat cap calculation, the sensors were thermalized as well, while here they remain to have their values
        if thermalize_sensors:
            perms = np.random.permutation(np.arange(0, size))
            #np.random.permutation(size)
        else:
            perms = np.random.permutation(np.arange(Ssize, size))

        for j, perm in enumerate(perms):
            rand = random_vars[i, j]
            eDiff = 2 * s[perm] * (h[perm] + np.dot(J[perm, :] + J[:, perm], s))
            E = -(np.dot(s, h) + np.dot(np.dot(s, J), s))
            all_E_permuts.append(E)
            #deltaE = E_f - E_i = -2 E_i = -2 * - SUM{J_ij*s_i*s_j}
            #self.J[i, :] + self.J[:, i] are added because value in one of both halfs of J seperated by the diagonal is zero

            if Beta * eDiff < np.log(1.0 / rand - 1):
                #transformed  P = 1/(1+e^(deltaE* Beta)
                s[perm] = -s[perm]

        # Record/Measure energy:
        E = -(np.dot(s, h) + np.dot(np.dot(s, J), s))
        Em += E / float(thermalTime)   # <-- mean calculation??
        E2m += E ** 2 / float(thermalTime)
        all_E.append(E)

    return s, Em, E2m, all_E, all_E_permuts

@jit(nopython=True)
def SequentialGlauberStepFast(thermalTime, s, h, J, Beta, Ssize, size):
    thermalize_sensors = False
    if thermalize_sensors:
        all_neurons_except_sens = np.arange(0, size)
    else:
        all_neurons_except_sens = np.arange(Ssize, size)

    #perms_list = np.array([np.random.permutation(np.arange(Ssize, size)) for j in range(thermalTime)])
    random_vars = np.random.rand(thermalTime, len(all_neurons_except_sens)) #[np.random.rand() for i in perms]
    for i in range(thermalTime):
        #perms = perms_list[i]
        #Prepare a matrix of random variables for later use

        # TODO: In previous dream heat cap calculation, the sensors were thermalized as well, while here they remain to have their values
        if thermalize_sensors:
            perms = np.random.permutation(np.arange(0, size))
            #perms = np.random.permutation(size)
        else:
            perms = np.random.permutation(np.arange(Ssize, size))

        for j, perm in enumerate(perms):
            rand = random_vars[i, j]
            eDiff = 2 * s[perm] * (h[perm] + np.dot(J[perm, :] + J[:, perm], s))
            #deltaE = E_f - E_i = -2 E_i = -2 * - SUM{J_ij*s_i*s_j}
            #self.J[i, :] + self.J[:, i] are added because value in one of both halfs of J seperated by the diagonal is zero

            if Beta * eDiff < np.log(1.0 / rand - 1):
            # if rand < 1/(1+np.exp(eDiff * Beta)):
                #transformed  P = 1/(1+e^(deltaE* Beta)
                s[perm] = -s[perm]

    return s

def plotSpectrum(sig, sim_name, beta_fac):
    # The FFT of the signal
    time_step = 0.02
    sig_fft = fftpack.fft(sig)

    # And the power (sig_fft is of complex dtype)
    power = np.abs(sig_fft)

    # The corresponding frequencies
    sample_freq = fftpack.fftfreq(np.size(sig), d=time_step)

    # Plot the FFT power
    plt.figure(figsize=(6, 5))
    plt.plot(sample_freq, power)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('plower')
    plt.yscale('log')
    plt.xscale('log')

    # Find the peak frequency: we can focus on only the positive frequencies
    pos_mask = np.where(sample_freq > 0)
    freqs = sample_freq[pos_mask]
    peak_freq = freqs[power[pos_mask].argmax()]



    # An inner plot to show the peak frequency

    # axes = plt.axes([0.55, 0.3, 0.3, 0.5])
    # plt.title('Peak frequency')
    # plt.plot(freqs[:8], power[:8])
    # plt.setp(axes, yticks=[])

    save_folder = 'save/{}/figs/C_recorded_anaylze/'.format(sim_name)
    save_name = 'beta_{}_spectrum.png'.format(np.round(beta_fac, decimals=2))

    if not path.exists(save_folder):
        makedirs(save_folder)

    plt.savefig(save_folder+save_name, bbox_inches='tight', dpi=300)

def plot_power_spectrum(energies, sim_name, beta_fac):

    freqs, psd = signal.welch(energies)

    plt.figure(figsize=(5, 4))
    plt.loglog(freqs, psd)
    #plt.semilogx(freqs, psd)
    plt.title('PSD: power spectral density')
    plt.xlabel('Frequency')
    plt.ylabel('Power')
    plt.tight_layout()

    save_folder = 'save/{}/figs/C_recorded_anaylze/'.format(sim_name)
    save_name = 'beta_{}_power_spectrum.png'.format(np.round(beta_fac, decimals=2))

    if not path.exists(save_folder):
        makedirs(save_folder)

    plt.savefig(save_folder+save_name, bbox_inches='tight', dpi=300)



def plot_all_E(all_Es, C, sim_name, legend_elements, beta_fac, all_permutations = False):
    plt.figure(figsize=(10, 12))
    plt.rcParams.update({'font.size': 22})
    plt.rc('text', usetex=True)
    plt.xscale('log')

    # norm=colors.LogNorm(vmin=min(C), vmax=max(C))
    # cmap = plt.get_cmap('plasma')
    # colors = []
    for c, all_E in zip(C, all_Es):
        # color = cmap(norm(c))
        if c > 0.1:
            color = 'red'
        else:
            color = 'blue'
        plt.plot(all_E, c=color)
        if all_permutations:
            # plt.xlim((0, 5000))
            pass
        else:
            # plt.xlim((0, 500))
            pass
        # break
    save_folder = 'save/{}/figs/C_recorded_anaylze/'.format(sim_name)
    if all_permutations:
        save_name = 'beta_{}_for_each_thermal_time_step_all_energies.png'.format(np.round(beta_fac, decimals=2))
    else:
        save_name = 'beta_{}_for_each_permutaion_all_energies.png'.format(np.round(beta_fac, decimals=2))
    plt.title(r'$E_{{net}}$ during thermalization of population with $\beta_\mathrm{{fac}}={}$'.format(np.round(beta_fac, decimals=4)))

    if all_permutations:
        plt.xlabel('Permutation')
    else:
        plt.xlabel('Thermal Time Step')
    plt.ylabel(r'$E_{net}$')
    plt.legend(handles=legend_elements)
    if not path.exists(save_folder):
        makedirs(save_folder)

    plt.savefig(save_folder+save_name, bbox_inches='tight', dpi=300)




def plot_c(C, beta_fac, sim_name, legend_elements):
    plt.figure(figsize=(10, 12))
    plt.rcParams.update({'font.size': 22})
    plt.rc('text', usetex=True)
    #plt.rc('font', family='serif')
    x_axis = np.arange(len(C))
    plt.title(r'$C/N$ for $\beta_\mathrm{{fac}}={}$'.format(np.round(beta_fac, decimals=2)))
    for x, y in zip(x_axis, C):
        if y > 0.1:
            color = 'red'
        else:
            color = 'blue'
        plt.scatter(x, y, c=color)
    plt.yscale('log')
    plt.ylabel(r'$C/N$')
    plt.xlabel(r'Organism number')
    plt.legend(handles=legend_elements)

    save_folder = 'save/{}/figs/C_recorded_anaylze/'.format(sim_name)
    if not path.exists(save_folder):
        makedirs(save_folder)
    save_name = 'C_vec_beta_fac{}.png'.format(beta_fac)
    plt.savefig(save_folder+save_name, bbox_inches='tight', dpi=300)
    plt.show()
    pass


# def from_list_of_arrs_to_arr(arr_list):
#     return np.concatenate(arr_list, axis=0)

if __name__ == '__main__':
    main()
    # sim-20200724-201710-g_2_-rec_c_1_-c_props_1_10000_-2_2_100_-c_11_-n_rec_c_recorded_sonsors_no_pre_thermalize 99 0