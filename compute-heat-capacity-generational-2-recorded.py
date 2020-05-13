#!/usr/bin/env python

from embodied_ising import ising
import numpy as np
from sys import argv
from os import path, makedirs

import pickle
import glob

# --- COMPUTE HEAT CAPACITY -------------------------------------------------------+

if len(argv) < 3:
    print("Usage: " + argv[0] + " <sim> + <bind> + <gen>")
    # loadfile = 'sim-20180131-145412'
    # bind = 0
    # iterNum = 0

loadfile = str(argv[1]) #

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
        I.randomize_state()
        for t in range(int(T / 10)):
            #  thermal time steps to get ANN to equilibrium
            I.DreamSensorGlauberStep()

        for t in range(T):
            #  thermal time steps, where Ennergy is recorded
            I.DreamSensorGlauberStep()
            ### Add these 3 lines o embodied ising for natural heat capacity

            E = -(np.dot(I.s, I.h) + np.dot(np.dot(I.s, I.J), I.s))
            Em += E / float(T)   # <-- mean calculation??
            E2m += E ** 2 / float(T)
            # Why is this divided by T (total amount of time steps after thermalization)?
        C[rep, agentNum] = I.Beta ** 2 * (E2m - Em ** 2) / size
        agentNum += 1

# print(np.mean(C, 0))
folder = 'save/' + loadfile + '/C' + '/C_' + str(iterNum) + '/'
file = 'C-size_' + str(size) + '-Nbetas_' + \
       str(Nbetas) + '-bind_' + str(bind) + '.npy'
filename = folder + file

if not path.exists(folder):
    makedirs(folder)


np.save(filename, C)
# savestr = 'Saving: ./.../' + file
# print(savestr)