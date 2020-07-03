#!/usr/bin/env python

from embodied_ising import ising
import numpy as np
from sys import argv
from os import path, makedirs

import pickle
import random
import glob
from numba import jit

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


    R = 1 # Number of Repetitions
    mode = 'MonteCarlo'

    #Is there a bug here? Nbetas = 101 originally Nbetas = 102 solves index error?
    Nbetas = 102
    betas = 10 ** np.linspace(-1, 1, Nbetas)
    loadstr = 'save/' + loadfile +  '/isings/gen[' + str(iterNum) + ']-isings.pickle'

    # print(iterNum)

    isings = pickle.load(open(loadstr, 'rb'))
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

        for I in isings:
            Em = 0
            E2m = 0
            T = 10000 #TimeSteps in dream simulation T = 100000

            betaVec = betas * I.Beta  # scale by org's local temperature
            # print(agentNum)
            I.Beta = betaVec[bind]
            #I.randomize_state()
            #  Initialize sensors with randoms set of sensor values that have been recorded during simulation
            initialize_sensors_from_record_randomize_neurons(I)

            # Thermalosation to equilibrium before making energy measurements
            #TODO LEave thermalization to equilibrium away before measurement?
            #I.s = SequentialGlauberStepFast(int(T/10), I.s, I.h, I.J, I.Beta, I.Ssize, I.size)

            #  Measuring energy between Glaubersteps
            I.s, E, E2m = SequentialGlauberStepFast_calc_energy(T, I.s, I.h, I.J, I.Beta, I.Ssize, I.size)

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
            C[rep, agentNum] = I.Beta ** 2 * (E2m - Em ** 2) / size
            agentNum += 1

    # print(np.mean(C, 0))
    # TODO: CHANGE THIS SO THERE IS NO CONFLICT WITH OTHER DREAM HEAT CAP CALCULATION
    folder = 'save/' + loadfile + '/C_recorded' + '/C_' + str(iterNum) + '/'
    file = 'C-size_' + str(size) + '-Nbetas_' + \
           str(Nbetas) + '-bind_' + str(bind) + '.npy'
    filename = folder + file

    if not path.exists(folder):
        makedirs(folder)


    np.save(filename, C)

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
            #deltaE = E_f - E_i = -2 E_i = -2 * - SUM{J_ij*s_i*s_j}
            #self.J[i, :] + self.J[:, i] are added because value in one of both halfs of J seperated by the diagonal is zero

            if Beta * eDiff < np.log(1.0 / rand - 1):
                #transformed  P = 1/(1+e^(deltaE* Beta)
                s[perm] = -s[perm]

        E = -(np.dot(s, h) + np.dot(np.dot(s, J), s))
        Em += E / float(thermalTime)   # <-- mean calculation??
        E2m += E ** 2 / float(thermalTime)

    return s, E, E2m

@jit(nopython=True)
def SequentialGlauberStepFast(thermalTime, s, h, J, Beta, Ssize, size):
    thermalize_sensors = True
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
                #transformed  P = 1/(1+e^(deltaE* Beta)
                s[perm] = -s[perm]

    return s

# def from_list_of_arrs_to_arr(arr_list):
#     return np.concatenate(arr_list, axis=0)

if __name__ == '__main__':
    main()
