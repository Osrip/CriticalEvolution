import compute_and_plot_heat_capacity_automatic
import plotting
import numpy as np
import operator
from itertools import combinations, product
import matplotlib as mpl

mpl.use('Agg')
import matplotlib.pyplot as plt
import copy

from math import atan2
from math import cos
from math import degrees
from math import floor
from math import radians
from random import random
from random import sample
from random import randint
from math import sin
from math import sqrt
from random import uniform
from copy import deepcopy
import multiprocessing as mp
import sys
import os
import pickle
import time
from shutil import copyfile
import automatic_plotting
from numba import jit
from numba import njit

import math
from os import listdir
from os.path import isfile, join
import subprocess
#import random
#from tqdm import tqdm
#from pympler import tracker



# ------------------------------------------------------------------------------+
# ------------------------------------------------------------------------------+
# --- CLASSES ------------------------------------------------------------------+
# ------------------------------------------------------------------------------+
# ------------------------------------------------------------------------------+
settings = {}

class ising:
    # Initialize the network
    def __init__(self, settings, netsize, Nsensors=2, Nmotors=2, name=None):
        # Create ising model
        self.size = netsize
        self.Ssize = Nsensors  # Number of sensors
        self.Msize = Nmotors  # Number of sensors
        self.radius = settings['org_radius']

        self.h = np.zeros(netsize) # TODO: is this bias, does this ever go over [0 0 0 0 0]???????

        # self.J = np.zeros((self.size, self.size))

        self.J = np.random.random((self.size, self.size))*2 - 1
        self.J = (self.J + self.J.T) / 2 #Connectivity Matrix
        np.fill_diagonal(self.J, 0)

        self.max_weights = 2

        self.maxRange = sqrt((settings['x_max'] - settings['x_min']) ** 2 +
                             (settings['y_max'] - settings['y_min']) ** 2)
        self.v_max = settings['v_max']
        self.food_num_env = settings['food_num']

        self.randomize_state()
        self.xpos = 0.0 #Position
        self.ypos = 0.0
        self.randomize_position(settings) #randomize position

        # self.r = uniform(0, 360)  # orientation   [0, 360]
        # self.v = uniform(0, settings['v_max']/3)  # velocity      [0, v_max]
        # self.dv = uniform(-settings['dv_max'], settings['dv_max'])  # dv


        self.dx = 0
        self.dy = 0

        self.name = name
        '''
        initial beta
        '''
        if settings['diff_init_betas'] is None:
            self.Beta = settings['init_beta']
        else:
            self.Beta = np.random.choice(settings['diff_init_betas'], 1)
        #self.Beta = 1.0
        # self.defaultT = max(100, netsize * 20)

        self.Ssize1 = 1 # FOOD ROTATIONAL SENSOR: sigmoid(theta)
        self.Ssize2 = 1 # FOOD DISTANCE SENSOR: sigmoid(distance)
        self.Ssize3 = 1 # DIRECTIONAL NEIGHBOUR SENSOR: dot-product distance normalized, see self.org_sens

        self.Msize1 = int(self.Msize/2)  # dv motor neuron


        # MASK USED FOR SETTINGS J/h TO 0
        self.maskJ = np.ones((self.size, self.size), dtype=bool)
        self.maskJ[0:self.Ssize, 0:self.Ssize] = False
        self.maskJ[-self.Msize: -self.Msize] = False
        self.maskJ[0:self.Ssize, -self.Msize:] = False
        np.fill_diagonal(self.maskJ, 0)
        self.maskJ = np.triu(self.maskJ)

        self.J[~self.maskJ] = 0

        # self.maskJtriu = np.triu(self.maskJ)

        self.disconnect_hidden_neurons(settings)

        self.maskh = np.ones(self.size, dtype=bool)
        self.maskh[0:self.Ssize] = False

        self.d_food = self.maxRange  # distance to nearest food
        self.r_food = 0  # orientation to nearest food
        #self.org_sens = 0 # directional, 1/distance ** 2 weighted organism sensor
        self.fitness = 0
        self.energy = 0.0
        self.food = 0
        self.energies = [] #Allows for using median as well... Replace with adding parameter up for average in future to save memory? This array is deleted before saving to reduce file size
        self.avg_energy = 0 #currently median implemented
        self.all_velocity = 0
        self.avg_velocity = 0
        self.v = 0.0
        self.generation = 0

        #self.assign_critical_values(settings) (attribute ising.C1)


        if not settings['BoidOn']:
            self.Update(settings, 0)

    def get_state(self, mode='all'):
        if mode == 'all':
            return self.s
        elif mode == 'motors':
            return self.s[-self.Msize:]
        elif mode == 'sensors':
            return self.s[0:self.Ssize]
        elif mode == 'non-sensors':
            return self.s[self.Ssize:]
        elif mode == 'hidden':
            return self.s[self.Ssize:-self.Msize]

    def get_state_index(self, mode='all'):
        return bool2int(0.5 * (self.get_state(mode) + 1))

    # Randomize the state of the network
    def randomize_state(self):
        self.s = np.random.randint(0, 2, self.size) * 2 - 1
        self.s = np.array(self.s, dtype=float)

        # SEE SENSOR UPDATE
        # random sensor states are generated by considering the sensor limitations

        random_rfood = (np.random.rand() * 360) - 180
        self.s[0] = random_rfood / 180

        random_dfood = np.random.rand() * self.maxRange
        self.s[1] = np.tanh(self.radius / (random_dfood ** 2 + 1e-6)) * 2 - 1

        random_v = np.random.rand() * self.v_max
        self.s[2] = np.tanh(random_v)

        random_energy = np.random.rand() * self.food_num_env
        self.s[3] = np.tanh(random_energy)

    def randomize_position(self, settings):

        self.xpos = uniform(settings['x_min'], settings['x_max'])  # position (x)
        self.ypos = uniform(settings['y_min'], settings['y_max'])  # position (y)

        if settings['BoidOn']:
            self.v = (np.random.randn(2) * 2 - 1) * settings['v_max']
            self.dv = (np.random.randn(2) * 2 - 1) * settings['dv_max']
            self.dx = self.v[0] * settings['dt']
            self.dy = self.v[1] * settings['dt']
            # self.r = np.abs(np.arctan(self.ypos / self.xpos))
            self.r = np.arctan2(self.v[1], self.v[0]) * 180 / np.pi
            
        else:
            self.r = np.random.rand() * 360 
            self.v = np.random.rand() * settings['v_max'] #TODO: This cannot work with huge v_max
            self.dv = np.random.rand() * settings['dv_max']
            self.dx = self.v * cos(radians(self.r)) * settings['dt']
            self.dy = self.v * sin(radians(self.r)) * settings['dt']



    # NOT USED
    # # Set random bias to sets of units of the system
    # def random_fields(self, max_weights=None):
    #     if max_weights is None:
    #         max_weights = self.max_weights
    #     self.h[self.Ssize:] = max_weights * (np.random.rand(self.size - self.Ssize) * 2 - 1)

    # Set random connections to sets of units of the system
    def random_wiring(self, max_weights=None):  # Set random values for h and J
        if max_weights is None:
            max_weights = self.max_weights
        for i in range(self.size):
            for j in np.arange(i + 1, self.size):
                if i < j and (i >= self.Ssize or j >= self.Ssize):
                    self.J[i, j] = (np.random.rand(1) * 2 - 1) * self.max_weights

    def Move(self, settings):
        # print(self.s[-2:])
        # TODO: velocity coeffecient that can be mutated?
        # UPDATE HEADING - Motor neuron s.[-self.Msize:self.Msize1]
        self.r += (np.sum(self.s[-self.Msize:-self.Msize1]) / 2) * settings['dr_max'] * settings['dt']
        self.r = self.r % 360

        # UPDATE VELOCITY - Motor neuron s.[-self.Msize1:]
        if settings['motor_neuron_acceleration']:
            self.v += (np.sum(self.s[-self.Msize1:]) / 2) * settings['dv_max'] * settings['dt']
        else:
            v_new = (np.sum(self.s[-self.Msize1:]) / 2) * settings['v_max']
            v_new_largest = v_new + settings['dv_max'] * settings['dt']
            v_new_lowest = v_new - settings['dv_max'] * settings['dt']
            if v_new > v_new_largest:
                v_new = v_new_largest
            if v_new < v_new_lowest:
                v_new = v_new_lowest

            self.v = v_new


        if self.v < 0:
            self.v = 0

        if self.v > settings['v_max']:
            self.v = settings['v_max']

        if self.r > settings['r_max']:
            self.r = settings['r_max']

        if settings['energy_model']:


            if self.energy >= (self.v * settings['cost_speed']) and self.v > settings['v_min']:
                #if agend has enough energy and wants to go faster than min speed
                self.energy -= self.v * settings['cost_speed']
            elif self.v > settings['v_min']:
                #if agned wants to go faster than min speed but does not have energy
                self.v = settings['v_min']
            self.all_velocity += self.v

        # print('Velocity: ' + str(self.v) +  str(self.s[-1]))

        # UPDATE POSITION
        self.dx = self.v * cos(radians(self.r)) * settings['dt']
        self.dy = self.v * sin(radians(self.r)) * settings['dt']
        self.xpos += self.dx
        self.ypos += self.dy

        # torus boundary conditions
        # if abs(self.xpos) > settings['x_max']:
        #     self.xpos = -self.xpos
        #
        # if abs(self.ypos) > settings['y_max']:
        #     self.ypos = -self.ypos

        self.xpos = (self.xpos + settings['x_max']) % settings['x_max']
        self.ypos = (self.ypos + settings['y_max']) % settings['y_max']

    def UpdateSensors(self, settings):
        # self.s refers to the neuron state, which for sensor neurons is sensor input

        # self.s[0] = sigmoid(self.r_food / 180)
        # self.s[1] = sigmoid(self.d_food)

        # normalize these values to be between -1 and 1
        # TODO: make the numberators (gravitational constants part of the connectivity matrix so it can be mutated)
        self.s[0] = self.r_food / 180 # self.r_food can only be -180:180
        # self.s[1] = np.tanh(np.log10(self.radius / (self.d_food ** 2 + 1e-6)))  # self.d_food goes from 0 to ~
        # self.s[2] = np.tanh(np.log10(self.org_sens + 1e-10))
        self.s[1] = np.tanh(self.radius / (self.d_food ** 2 + 1e-6))*2 - 1  # self.d_food goes from 0 to ~
        #self.s[2] = np.tanh((self.org_sens))*2 - 1
        self.s[2] = np.tanh(self.v)
        self.s[3] = np.tanh(self.energy)
        # print(self.s[0:3])
    
    # Execute step of the Glauber algorithm to update the state of one unit

    def GlauberStep(self, i=None):
        '''
        Utilizes: self.s, self.h, self.J
        Modifies: self.s
        '''
        if i is None:
            i = np.random.randint(self.size)
        eDiff = 2 * self.s[i] * (self.h[i] + np.dot(self.J[i, :] + self.J[:, i], self.s))
        #deltaE = E_f - E_i = -2 E_i = -2 * - SUM{J_ij*s_i*s_j}
        #self.J[i, :] + self.J[:, i] are added because value in one of both halfs of J seperated by the diagonal is zero

        if self.Beta * eDiff < np.log(1.0 / np.random.rand() - 1):
            #transformed  P = 1/(1+e^(deltaE* Beta)
            self.s[i] = -self.s[i]
    '''
    # Execute step of the Glauber algorithm to update the state of one unit
    # Faster version??
    def GlauberStep(self, i=None):
        #if i is None:
        #    i = np.random.randint(self.size) <-- commented out as not used
        eDiff = np.multiply(np.multiply(2, self.s[i]), np.add(self.h[i], np.dot(np.add(self.J[i, :], self.J[:, i]), self.s)))
        if np.multiply(self.Beta, eDiff) < np.log(1.0 / np.random.rand() - 1):  # Glauber
            self.s[i] = -self.s[i]
    '''

    # Execute time-step using an ANN algorithm to update the state of all units
    def ANNStep(self):

        # SIMPLE MLP
        af = lambda x: np.tanh(x)  # activation function
        Jhm = self.J + np.transpose(self.J)  # connectivity for hidden/motor layers

        Jh = Jhm[:, self.Ssize:-self.Msize]  # inputs to hidden neurons
        Jm = Jhm[:, -self.Msize:]  # inputs to motor neurons

        # activate and update
        new_h = af(np.dot(self.s, Jh))
        self.s[self.Ssize:-self.Msize] = new_h

        new_m = af(np.dot(self.s, Jm))
        self.s[-self.Msize:] = new_m

        #  TODO: non-symmetric Jhm, need to change through to GA



    # Compute energy difference between two states with a flip of spin i
    def deltaE(self, i):
        return 2 * (self.s[i] * self.h[i] + np.sum(
            self.s[i] * (self.J[i, :] * self.s) + self.s[i] * (self.J[:, i] * self.s)))

    # Update states of the agent from its sensors
    def Update(self, settings, i=None):
        if i is None:
            i = np.random.randint(self.size)
        if i == 0:
            self.Move(settings)
            self.UpdateSensors(settings)
        elif i >= self.Ssize:
            self.GlauberStep(i)

    def SequentialUpdate(self, settings):
        for i in np.random.permutation(self.size):
            self.Update(settings, i)


    # Update all states of the system without restricted influences

    def SequentialGlauberStepFastHelper(self, settings):
        thermalTime = int(settings['thermalTime'])
        self.UpdateSensors(settings)

        self.s = SequentialGlauberStepFast(thermalTime, self.s, self.h, self.J, self.Beta, self.Ssize, self.size)
        self.Move(settings)





    def SequentialGlauberStep(self, settings, thermal_time):
        thermalTime = int(thermal_time)

        self.UpdateSensors(settings)  # update sensors at beginning

        # update all other neurons a bunch of times
        for j in range(thermalTime):
            perms = np.random.permutation(range(self.Ssize, self.size))
            #going through all neuron exceot sensors in random permutations
            for i in perms:
                #self.GlauberStep(i)
                rand = np.random.rand()
                GlauberStepFast(i, rand, self.s, self.h, self.J, self.Beta)

        self.Move(settings)  # move organism at end


    # Update all states of the system without restricted influences
    def ANNUpdate(self, settings):
        thermalTime = int(settings['thermalTime'])

        self.UpdateSensors(settings)  # update sensors at beginning

        # update all other neurons a bunch of times
        for j in range(thermalTime):
            self.ANNStep()

        self.Move(settings)  # move organism at end

    # update everything except sensors
    def NoSensorGlauberStep(self):
        perms = np.random.permutation(range(self.Ssize, self.size))
        for i in perms:
            self.GlauberStep(i)

    # update sensors using glauber steps (dream)
    def DreamSensorGlauberStep(self):
        perms = np.random.permutation(self.size)
        for i in perms:
            self.GlauberStep(i)

    # ensure that not all of the hidden neurons are connected to each other
    def disconnect_hidden_neurons(self, settings):
        numHNeurons = self.size - self.Ssize - self.Msize
        perms = list(combinations(range(self.Ssize, self.Ssize + numHNeurons), 2))
        numDisconnectedEdges = len(list(combinations(range(settings['numDisconnectedNeurons']), 2)))
        # settings['numDisconnectedNeurons'] how many hidden neurons are disconnenced fromeach other

        for i in range(0, numDisconnectedEdges):
            nrand = np.random.randint(len(perms))
            iIndex = perms[nrand][0]
            jIndex = perms[nrand][1]

            self.J[iIndex,jIndex] = 0
            # self.J[jIndex, iIndex] = 0

            self.maskJ[iIndex, jIndex] = False
            # self.maskJ[jIndex, iIndex] = False

        # self.maskJtriu = np.triu(self.maskJ)


    # mutate the connectivity matrix of an organism by stochastically adding/removing an edge
    def mutate(self, settings):
        '''
         3 Mutations happening at once:
        CONNECTIVITY Mutations:
        One of these things happen
        - A new edge is removed (according to sparsity settings more or less likely)
        - or added (if no adding is possible some random edge gets new edge weight)

        EDGE MUTATIONS
        currently in an edge mutation means, that the whole edge weight is replaced by a randomly generated weight
        

        BETA Mutations
        Beta is mutated
        '''

        # ADDS/REMOVES RANDOM EDGE DEPENDING ON SPARSITY SETTING, RANDOMLY MUTATES ANOTHER RANDOM EDGE

        # expected number of disconnected edges
        numDisconnectedEdges = len(list(combinations(range(settings['numDisconnectedNeurons']), 2)))
        totalPossibleEdges = len(list(combinations(range(self.size - self.Ssize - self.Msize), 2)))

        # number of (dis)connected edges
        connected = copy.deepcopy(self.maskJ)

        disconnected = ~connected #disconnected not connected
        np.fill_diagonal(disconnected, 0)
        disconnected = np.triu(disconnected)

        # things that need to be connected and not flagged to change
        connected[0:self.Ssize, :] = 0
        connected[:, -self.Msize:] = 0
        # things that need to be disconnected and not flagged to change
        disconnected[0:self.Ssize, -self.Msize:] = 0
        disconnected[0:self.Ssize, 0:self.Ssize] = 0

        numEdges = np.sum(connected) #number of edges, that can actuall be disconnected (in beginning of simulatpn curr settings 3)
        # positive value means too many edges, negative value means too little
        edgeDiff = numEdges - (totalPossibleEdges - numDisconnectedEdges)
        # edgeDiff = numEdges - numDisconnectedEdges

        # TODO: investigate the empty connectivity matrix here
        prob = sigmoid(edgeDiff)  #for numDisconnectedNeurons=0 this means 0.5 --> equal probability of adding edge and removing edge # probability near 1 means random edge will be removed, near 0 means random edge added
        rand = np.random.rand()

        if prob >= rand:
            # remove random edge
            i, j = np.nonzero(connected) #Indecies of neurons connected by edges that can be disconnected
            if len(i) > 0:
                randindex = np.random.randint(0, len(i))
                ii = i[randindex]
                jj = j[randindex]

                self.maskJ[ii, jj] = False
                self.J[ii, jj] = 0

                # TODO: is this a good way of making the code multi-purpose?
                # try:
                #     self.C1[ii, jj] = 0
                # except NameError:
                #     pass'

            else:
                print('Connectivity Matrix Empty! Mutation Blocked.')

        else:
            #looking for disconnected neurons that can be connected
            # add random edge
            i, j = np.nonzero(disconnected)
            if len(i) > 0:
                randindex = np.random.randint(0, len(i))
                ii = i[randindex]
                jj = j[randindex]

                self.maskJ[ii, jj] = True
                self.J[ii, jj] = np.random.uniform(-1, 1) * self.max_weights
                # I.J[ii, jj] = np.random.uniform(np.min(I.J[I.Ssize:-I.Msize, I.Ssize:-I.Msize]) / 2,
                #                                 np.max(I.J[I.Ssize:-I.Msize, I.Ssize:-I.Msize]) * 2)
                # try:
                #     self.C1[ii, jj] = settings['Cdist'][np.random.randint(0, len(settings['Cdist']))]
                # except NameError:
                #     pass

            else:  # if connectivity matrix is full, just change an already existing edge
                #This only happens, when alogorithm tries to add edge, but everything is connected
                i, j = np.nonzero(connected)

                randindex = np.random.randint(0, len(i))
                ii = i[randindex]
                jj = j[randindex]

                self.J[ii, jj] = np.random.uniform(-1, 1) * self.max_weights


        # MUTATE RANDOM EDGE
        i, j = np.nonzero(self.maskJ)

        randindex = np.random.randint(0, len(i))
        ii = i[randindex]
        jj = j[randindex]

        self.J[ii, jj] = np.random.uniform(-1, 1) * self.max_weights
        #Mutation of weights--> mutated weight is generated randomly from scratch

        # MUTATE LOCAL TEMPERATURE
        if settings['mutateB']:
            deltaB = np.abs(np.random.normal(1, settings['sigB']))
            self.Beta = self.Beta * deltaB  #TODO mutate beta not by multiplying? How was Beta modified originally?
            #biases GA pushing towards lower betas (artifical pressure to small betas)

    def reset_state(self, settings):

        # randomize internal state (not using self.random_state since it also randomizes sensors)
        self.s = np.random.random(size=self.size) * 2 - 1
        # randomize position (not using self.randomize_position function since it also randomizes velocity)
        self.xpos = uniform(settings['x_min'], settings['x_max'])  # position (x)
        self.ypos = uniform(settings['y_min'], settings['y_max'])  # position (y)

        self.dv = 0
        self.v = 0

        self.ddr = 0
        self.dr = 0

        self.food = 0
        self.fitness = 0

        if settings['energy_model']:
            self.energies = []  # Clear .energies, that .avg_energy is calculated from with each iteration
            self.energy = settings['initial_energy']  # Setting initial energy

            self.avg_energy = 0
            self.all_velocity = 0
            self.avg_velocity = 0


#
# @jit(nopython=True)
# def SequentialGlauberStepFast(thermalTime, perms, random_vars, s, h, J, Beta):
#     for j in range(thermalTime):
#         for ind, i in enumerate(perms):
#             rand = random_vars[ind]
#             GlauberStepFast(i, rand, s, h, J, Beta)
#
# @jit(nopython=True)
# def GlauberStepFast(i, rand, s, h, J, Beta ):
#     '''
#     Utilizes: self.s, self.h, self.J
#     Modifies: self.s
#     '''
#
#     eDiff = 2 * s[i] * (h[i] + np.dot(J[i, :] + J[:, i], s))
#     #deltaE = E_f - E_i = -2 E_i = -2 * - SUM{J_ij*s_i*s_j}
#     #self.J[i, :] + self.J[:, i] are added because value in one of both halfs of J seperated by the diagonal is zero
#
#     if Beta * eDiff < np.log(1.0 / rand - 1):
#         #transformed  P = 1/(1+e^(deltaE* Beta)
#         s[i] = -s[i] # TODO return s!!!!!!!

# @jit(nopython=True)
# def SequentialGlauberStepFast(thermalTime, perms_list, random_vars_list, s, h, J, Beta):
#     for j in range(thermalTime):
#         perms = perms_list[j]
#         random_vars = random_vars_list[j]
#         for ind, i in enumerate(perms):
#             rand = random_vars[ind]
#             eDiff = 2 * s[i] * (h[i] + np.dot(J[i, :] + J[:, i], s))
#             #deltaE = E_f - E_i = -2 E_i = -2 * - SUM{J_ij*s_i*s_j}
#             #self.J[i, :] + self.J[:, i] are added because value in one of both halfs of J seperated by the diagonal is zero
#
#             if Beta * eDiff < np.log(1.0 / rand - 1):
#                 #transformed  P = 1/(1+e^(deltaE* Beta)
#                 s[i] = -s[i]
#     return s

@jit(nopython=True)
def SequentialGlauberStepFast(thermalTime, s, h, J, Beta, Ssize, size):
    all_neurons_except_sens = np.arange(Ssize, size)
    #perms_list = np.array([np.random.permutation(np.arange(Ssize, size)) for j in range(thermalTime)])
    random_vars = np.random.rand(thermalTime, len(all_neurons_except_sens)) #[np.random.rand() for i in perms]
    for i in range(thermalTime):
        #perms = perms_list[i]
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



class food():
    def __init__(self, settings):
        self.xpos = uniform(settings['x_min'], settings['x_max'])
        self.ypos = uniform(settings['y_min'], settings['y_max'])
        self.energy = settings['food_energy']

    def respawn(self, settings):
        self.xpos = uniform(settings['x_min'], settings['x_max'])
        self.ypos = uniform(settings['y_min'], settings['y_max'])
        self.energy = settings['food_energy']

# ------------------------------------------------------------------------------+
# ------------------------------------------------------------------------------+
# --- FUNCTIONS ----------------------------------------------------------------+
# ------------------------------------------------------------------------------+
# ------------------------------------------------------------------------------+

def save_whole_project(folder):
    cwd = os.getcwd()
    onlyfiles = [f for f in listdir(cwd) if isfile(join(cwd, f))]
    save_folder = folder + 'code/'
    for file in onlyfiles:
        save_code(save_folder, file)



def save_code(folder, filename):
    src = filename
    dst = folder + src
    copyfile(src, dst)


def dist(x1, y1, x2, y2):
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

#@jit(nopython=True)

def pdistance_pairwise(x0, x1, dimensions, food=False):
    '''
    Parameters
    ----------
    x0, x1:
        (vectorized) list of coordinates. Can be N-dimensional. e.g. x0 = [[0.5, 2.], [1.1, 3.8]].

    dimensions:
        size of the bounding box, array of length N. e.g. [8., 8.], [xmax - xmin, ymax - ymin].

    food:
        boolean signifying if the distance calculations are between organisms or between organisms and food. In the
        latter case we don't need to compare it both ways around, in the former, theta_mat is a non-symmetric matrix.

    Returns
    -------

    dist_mat:
        upper triangle matrix of pairwise distances accounting for periodic boundaries

    theta_mat:
        full matrix of angles between each position accounting for periodic boundaries
    '''


    # get all unique pairs combinations
    N1 = len(x0)
    N2 = len(x1)

    if food:
        combo_index = list(product(np.arange(N1), np.arange(N2)))
    else:
        if not len(x0) == len(x1):
            raise Exception('x0.shape[0] not equal to x1.shape[0] when comparing organisms.')
        combo_index = list(combinations(np.arange(N1), 2))


    Ii = np.array([x0[i[0]] for i in combo_index])
    Ij = np.array([x1[i[1]] for i in combo_index])

    # calculate distances accounting for periodic boundaries
    # delta = np.abs(Ipostiled_seq - Ipostiled)
    delta = Ij - Ii
    delta = np.where(np.abs(delta) > 0.5 * dimensions, delta - np.sign(delta)*dimensions, delta)

    dist_vec = np.sqrt((delta ** 2).sum(axis=-1))
    theta_vec_ij = np.degrees(np.arctan2(delta[:, 1], delta[:, 0]))  # from org i to org j
    if not food:
        theta_vec_ji = np.degrees(np.arctan2(-delta[:, 1], -delta[:, 0])) # from org j to org i

    if food:
        dist_mat = dist_vec.reshape(N1, N2)
    else:
        dist_mat = np.zeros((N1, N2))
    theta_mat = np.zeros((N1, N2))

    for ii, ind in enumerate(combo_index):
        i = ind[0]
        j = ind[1]
        # can leave this as upper triangle since it's symmetric
        if not food:
            dist_mat[i, j] = dist_vec[ii]
        # need to get a full matrix since eventually these angles are not symmetric
        theta_mat[i, j] = theta_vec_ij[ii]
        # if comparing org-to-org angles, need the other direction as well
        if not food:
            theta_mat[j, i] = theta_vec_ji[ii]


    return dist_mat, theta_mat


def calc_heading(I, food):
    d_x = food.xpos - I.xpos
    d_y = food.ypos - I.ypos
    theta_d = degrees(atan2(d_y, d_x)) - I.r
    theta_d %= 360

    # keep the angles between -180:180
    if theta_d > 180:
        theta_d -= 360
    return theta_d


# Transform bool array into positive integer
def bool2int(x):
    y = 0
    for i, j in enumerate(np.array(x)[::-1]):
        y += j * 2 ** i
    return int(y)


# Transform positive integer into bit array
def bitfield(n, size):
    x = [int(x) for x in bin(int(n))[2:]]
    x = [0] * (size - len(x)) + x
    return np.array(x)

def extract_plot_information(isings, foods, settings):
    isings_info = []
    foods_info = []
    for I in isings:
        if settings['energy_model']:
            isings_info.append([I.xpos, I.ypos, I.r, I.energy])
        else:
            isings_info.append([I.xpos, I.ypos, I.r, I.fitness])
    for f in foods:
        foods_info.append([f.xpos, f.ypos])
    return isings_info, foods_info




def TimeEvolve(isings, foods, settings, folder, rep, total_timesteps = 0):
    [ising.reset_state(settings) for ising in isings]

    T = settings['TimeSteps']
    for I in isings:
        I.position = np.zeros((2, T))

    # Main simulation loop:
    if settings['plot'] == True:

        fig, ax = plt.subplots()
        #fig.set_size_inches(15, 10)
        isings_all_timesteps = []
        foods_all_timesteps = []


    '''
    !!! iterating through timesteps
    '''
    #for t in tqdm(range(T)):
    for t in range(T):
        #print(len(foods))

        # print('\r', 'Iteration {0} of {1}'.format(t, T), end='') #, end='\r'
        # print('\r', 'Tstep {0}/{1}'.format(t, T), end='')  # , end='\r'
        if not (settings['chg_food_gen'] is None):
            if t == settings['chg_food_gen'][0]:
                settings['num_food'] = settings['chg_food_gen'][1]
        if settings['seasons'] == True:
            foods = seasons(settings, foods, t, T, total_timesteps)

        # PLOT SIMULATION FRAME
        if settings['plot'] == True and (t % settings['frameRate']) == 0:
            #plot_frame(settings, folder, fig, ax, isings, foods, t, rep)
            isings_info, foods_info = extract_plot_information(isings, foods, settings)
            isings_all_timesteps.append(isings_info)
            foods_all_timesteps.append(foods_info)

        interact(settings, isings, foods)

            
        
        if settings['BoidOn']:
            boid_update(isings, settings)
            for I in isings:
                I.position[:, t] = [I.xpos, I.ypos]
        else:

            #parallelization here

            if settings['ANN']:
                I.ANNUpdate(settings)

            else:
                if settings['parallel_computing']:
                    parallelizedSequGlauberSteps(isings, settings)
                else:
                    [I.SequentialGlauberStepFastHelper(settings) for I in isings]

            
            
    if settings['plot']:
        #plotting.animate_plot(artist_list, settings, ax, fig)
        # try:
        plotting.animate_plot_Func(isings_all_timesteps, foods_all_timesteps, settings, ax, fig, rep, t, folder)

        # except Exception:
        #     print('There occurred an error during animation...the simulation keeps going')

        '''
        for I in isings:
            if settings['ANN']:
                I.ANNUpdate(settings)
            else:
                I.SequentialGlauberStep(settings)
            I.position[:, t] = [I.xpos, I.ypos]
        '''
'''
#Helper functions parallelization
def parallelSequGlauberStep(I, settings):
    # I = copy.deepcopy(I)
    I.SequentialGlauberStep()
    return I
'''
def parallelizedSequGlauberSteps(isings, settings, asynchronous = False):

    if not asynchronous:

        if settings['cores'] == 0:
            pool = mp.Pool(mp.cpu_count() - 1)
        else:
            pool = mp.Pool(settings['cores'])

        if not asynchronous:
            for I in isings:
                I.UpdateSensors(settings) # update sensors at beginning
                # pass_vars = (settings, I.Ssize, I.size, I.s, I.h, I.J, I.Beta)
                # pool.apply_async(parallelizedSequGlauberStep, args=(pass_vars), callback=collect_result)
            vars_list = [(settings, I.Ssize, I.size, I.s, I.h, I.J, I.Beta) for I in isings]
            s_list = pool.map(parallelizedSequGlauberStep, vars_list)
            pool.close()
            #pool.join()

            # = results

            for i, I in enumerate(isings):
                I.s = s_list[i]
                I.Move(settings)  # move organism at end
        else:
            for I in isings:
                I.UpdateSensors(settings)  # update sensors at beginning
            # pass_vars = (settings, I.Ssize, I.size, I.s, I.h, I.J, I.Beta)
            # pool.apply_async(parallelizedSequGlauberStep, args=(pass_vars), callback=collect_result)
            vars_list = [(settings, I.Ssize, I.size, I.s, I.h, I.J, I.Beta) for I in isings]
            s_list = pool.map_async(parallelizedSequGlauberStep, vars_list)
            pool.close()
            pool.join()


def parallelizedSequGlauberStep(pass_vars):
    settings, Ssize, size, s, h, J, Beta = pass_vars
    thermalTime = int(settings['thermalTime'])

    # update all other neurons a bunch of times
    for j in range(thermalTime):
        perms = np.random.permutation(range(Ssize, size))
        for i in perms:
            s_fac = GlauberStepParallel(i, s, h, J, Beta, size)
            s[i] = s[i] * s_fac
    return s


def GlauberStepParallel(i, s, h, J, Beta, size):
    eDiff = 2 * s[i] * (h[i] + np.dot(J[i, :] + J[:, i], s))
    if Beta * eDiff < np.log(1.0 / np.random.rand() - 1):  # Glauber
        return -1
    else:
        return 1




def EvolutionLearning(isings, foods, settings, Iterations = 1):
    '''
    Called by "train"
    '''
    #Add command line input to folder name
    s = sys.argv[1:]
    command_input = '_'.join([str(elem) for elem in s])
    sim_name = 'sim-' + time.strftime("%Y%m%d-%H%M%S") + command_input
    folder = 'save/' + sim_name  + '/'
    if settings['save_data'] == True:#

        if not os.path.exists(folder):
            os.makedirs(folder)
            os.makedirs(folder + 'isings')
            os.makedirs(folder + 'stats')
            os.makedirs(folder + 'figs')
            os.makedirs(folder + 'code')

            #save settings dicitionary
        save_settings(folder, settings)
        try:
            save_whole_project(folder)
        except Exception:
            print('Could not create backup copy of code')

    total_timesteps = 0 #  Total amount of time steps, needed for bacterial seasons
    if settings['seasons']:
        handle_total_timesteps(folder, settings, 0)

    if (settings['seasons'] and (settings['years_per_iteration'] < 1)) and not (settings['loadfile'] is ''):
        time_steps = handle_total_timesteps(folder, settings)

    #tr = tracker.SummaryTracker()
    count = 0
    for rep in range(Iterations):
        ''' 
        !!! jede Iteration
        '''
        for I in isings:
            I.generation = rep
        if rep in settings['plot_generations']:
            settings['plot'] = True
        else:
            settings['plot'] = False

        TimeEvolve(isings, foods, settings, folder, rep, total_timesteps)
        if settings['energy_model']:

            for I in isings:
                I.avg_energy = np.mean(I.energies)  # Average or median better?
                I.avg_velocity = I.all_velocity / settings['TimeSteps']
            eat_rate = np.average([I.avg_energy for I in isings])

        if settings['plot'] == True:
            plt.clf()

        # mutationrate[0], mutationrate[1] = mutation_rate(isings)

        if rep % settings['evolution_rate'] == 0:

            fitness, fitness_stat = food_fitness(isings)

            if settings['energy_model'] == False:
                eat_rate = np.sum(fitness_stat)/settings['TimeSteps'] #avg fitnes, normalized by timestep

            if settings['mutateB']:
                Beta = []
                for I in isings:
                    Beta.append(I.Beta)

                mBeta = np.mean(Beta)
                stdBeta = np.std(Beta)
                maxBeta = np.max(Beta)
                minBeta = np.min(Beta)

        # save rate equal to evolutation rate
        # TODO: Add eatrate; make this useful
            mutationrate = None
            fitm = None
            fitC = None

            if settings['energy_model']:
                fit_func_param_name = 'avg_energy'
            else:
                fit_func_param_name = 'eat_rate'

            if settings['mutateB']:
                print('\n', count, '|', fit_func_param_name, eat_rate, 'mean_Beta', mBeta,
                      'std_Beta', stdBeta, 'min_Beta', minBeta, 'max_Beta', maxBeta)
            else:
                print('\n', count, '|', 'Avg_fitness', eat_rate)

            if settings['seasons'] and (settings['years_per_iteration'] < 1):
                total_timesteps = handle_total_timesteps(folder, settings)


            if settings['save_data']:
                if settings['energy_model']:
                    # Clear I.energies in isings_copy before saving
                    isings_copy = deepcopy(isings)
                    for I in isings_copy:
                        I.energies = []

                    save_sim(folder, isings_copy, fitness_stat, mutationrate, fitC, fitm, rep)
                    del isings_copy
                else:
                    save_sim(folder, isings, fitness_stat, mutationrate, fitC, fitm, rep)


        count += 1

        if rep % settings['evolution_rate'] == 0:
            '''
            Irrelevant without critical learning!!
            Evolution via GA! According to evolution rate done every nth iteration
            Does every evolution event represent one generation?
            '''

            isings = evolve(settings, isings, rep)

        #Refreshing of plots
        if not settings['refresh_plot'] is 0:
            if rep % settings['refresh_plot'] == 0 and rep != 0:
                try:
                    if settings['refresh_plot'] - rep == 0:
                        # During first refresh plot, compute heat capacity of gen 0
                        compute_and_plot_heat_capacity_automatic.main(sim_name, settings, generations=[0])

                    #automatic_plotting.main(sim_name)
                    #  WRONGLY ALSO ACTIVATED final_true on purpose
                    os.system('python3 automatic_plotting.py {} final_true'.format(sim_name))
                    #subprocess.Popen(['python3', 'automatic_plotting.py', sim_name])
                except Exception:
                    print('Something went wrong when refreshing plot at generation{}'.format(rep))

        #tr.print_diff()
    # Plot simulation at end even is refresh is inactive, but only if refresh has not already done that
    if settings['plot_pipeline']:
        if settings['refresh_plot'] == 0:
            #automatic_plotting.main(sim_name)
            os.system('python3 automatic_plotting.py {} final_true'.format(sim_name))

            #subprocess.Popen(['python3', 'automatic_plotting.py', sim_name])
        elif (not rep % settings['refresh_plot'] == 0):
            #automatic_plotting.main(sim_name)
            os.system('python3 automatic_plotting.py {} final_true'.format(sim_name))
            #subprocess.Popen(['python3', 'automatic_plotting.py', sim_name])
    return sim_name

def handle_total_timesteps(folder, settings, save_value = None):
    #if count > 0 or (settings['loadfile'] is ''):
    if save_value is None:
        #  total_timesteps = pickle.load(open('{}total_timesteps.pickle'.format(folder)), 'rb')
        total_timesteps = pickle.load(open('{}total_timesteps.pickle'.format(folder), 'rb'))
    else:
        total_timesteps = save_value
    total_timesteps += settings['TimeSteps']
    pickle_out = open('{}total_timesteps.pickle'.format(folder), 'wb')
    pickle.dump(total_timesteps, pickle_out)
    pickle_out.close()
    return total_timesteps


def food_fitness(isings):
    fitness = []
    for I in isings:

        fitness.append(I.fitness)

    fitness = np.array(fitness, dtype='float')
    mask = fitness != 0

    fitnessN = copy.deepcopy(fitness)
    fitnessN[mask] /= float(np.max(fitnessN))
    # fitness[mask] /= float(np.max(fitness))

    return fitnessN, fitness

def evolve(settings, I_old, gen):

    size = settings['size']
    nSensors = settings['nSensors']
    nMotors = settings['nMotors']
    
    '''
    !!!fitness function!!!
    '''
    if settings['energy_model']:
        I_sorted = sorted(I_old, key=operator.attrgetter('avg_energy'), reverse=True)
    else:
        I_sorted = sorted(I_old, key=operator.attrgetter('fitness'), reverse=True)
    I_new = []

    alive_num = int(settings['pop_size'] - settings['numKill'])
    elitism_num = int(alive_num/2) # only the top half of the living orgs can duplicate

    numMate = int(settings['numKill'] * settings['mateDupRatio'])
    numDup = settings['numKill'] - numMate

    for i in range(0, alive_num):
        I_new.append(I_sorted[i])

    # --- GENERATE NEW ORGANISMS ---------------------------+
    orgCount = settings['pop_size'] + gen * settings['numKill']

    # DUPLICATION OF ELITE POPULATION
    for dup in range(0, numDup):
        candidateDup = range(0, elitism_num)
        random_index = sample(candidateDup, 1)[0]

        name = copy.deepcopy(I_sorted[random_index].name) + 'm'
        I_new.append(ising(settings, size, nSensors, nMotors, name))

        #  TODO: need to seriously check if mutations are occuring uniquely
        # probably misusing deepcopy here, figure this shit out
        I_new[-1].Beta = copy.deepcopy(I_sorted[random_index].Beta)
        I_new[-1].J = copy.deepcopy(I_sorted[random_index].J)
        I_new[-1].h = copy.deepcopy(I_sorted[random_index].h)
        I_new[-1].maskJ = copy.deepcopy(I_sorted[random_index].maskJ)
        # I_new[-1].maskJtriu = I_sorted[random_index].maskJtriu
        
        '''
        only important with critical learning
        '''
        # try:
        #     I_new[-1].C1 = I_sorted[random_index].C1
        # except NameError:
        #     pass

        # MUTATE SOMETIMES
        if np.random.random() < settings['mutationRateDup']:
            I_new[-1].mutate(settings)

        # random mutations in duplication

    # MATING OF LIVING POPULATION DOUBLE DIPPING ELITE
    for mate in range(0, numMate):
        # TODO: negative weight mutations?!
        # SELECTION (TRUNCATION SELECTION)
        candidatesMate = range(0, len(I_new)) # range(0, alive_num) to avoid double dipping
        random_index = sample(candidatesMate, 2)
        org_1 = I_sorted[random_index[0]]
        org_2 = I_sorted[random_index[1]]

        # CROSSOVER
        J_new = np.zeros((size, size))
        h_new = np.zeros(size)

        # load up a dummy maskJ which gets updated
        maskJ_new = np.zeros((size, size), dtype=bool)

        crossover_weight = random()

        # CROSS/MUTATE TEMPERATURE
        if settings['mutateB']:
            # folded normal distribution
            deltaB = np.abs( np.random.normal(1, settings['sigB']) )

            Beta_new = ((crossover_weight * org_1.Beta) + \
                            ((1 - crossover_weight) * org_2.Beta) ) * deltaB
        else:
            Beta_new = org_1.Beta

        # CROSS WEIGHTS
        for iJ in range(0, size):
            crossover_weight = random()

            h_new[iJ] = (crossover_weight * org_1.h[iJ]) + \
                        ((1 - crossover_weight) * org_2.h[iJ])

            for jJ in range(iJ + 1, size):
                crossover_weight = random()

                # check if these hidden neurons are disconnected to begin with
                if org_1.maskJ[iJ, jJ] != 0 and org_2.maskJ[iJ, jJ] != 0:
                    J_new[iJ, jJ] = (crossover_weight * org_1.J[iJ, jJ]) + \
                                    ((1 - crossover_weight) * org_2.J[iJ, jJ])
                    maskJ_new[iJ, jJ] = org_1.maskJ[iJ, jJ]
                elif np.random.randint(2) == 0:
                    J_new[iJ, jJ] = org_1.J[iJ, jJ]
                    maskJ_new[iJ, jJ] = org_1.maskJ[iJ, jJ]
                else:
                    J_new[iJ, jJ] = org_2.J[iJ, jJ]
                    maskJ_new[iJ, jJ] = org_2.maskJ[iJ, jJ]

                if np.abs(J_new[iJ, jJ]) > org_1.max_weights:
                    J_new[iJ, jJ] = org_1.max_weights


        # TODO: include name of parents
        name = 'gen[' + str(gen) + ']-org[' + str(orgCount) + ']'
        I_new.append(ising(settings, size, nSensors, nMotors, name))

        I_new[-1].Beta = Beta_new
        I_new[-1].J = J_new
        I_new[-1].h = h_new
        I_new[-1].maskJ = maskJ_new

        # MUTATE IN GENERAL
        I_new[-1].mutate(settings)

        orgCount += 1

    for I in I_new:
        I.fitness = 0


    return I_new

def save_settings(folder, settings):
    with open(folder + 'settings.csv', 'w') as f:
        for key in settings.keys():
            f.write("%s,%s\n" % (key, settings[key]))
    pickle_out = open('{}settings.pickle'.format(folder), 'wb')
    pickle.dump(settings, pickle_out)
    pickle_out.close()



def save_sim(folder, isings, fitness_stat, mutationrate, fitC, fitm, gen):


    filenameI = folder + 'isings/gen[' + str(gen) + ']-isings.pickle'
    filenameS = folder + 'stats/gen[' + str(gen) + ']-stats.pickle'

    if type(mutationrate) is not type(None):
        mutationh = mutationrate[0]
        mutationJ = mutationrate[1]
    else:
        mutationh = None
        mutationJ = None

    pickle_out = open(filenameI, 'wb')
    pickle.dump(isings, pickle_out)
    pickle_out.close()


def sigmoid(x):
    y = 1/(1 + np.exp(-x))
    return y

def logit(x):
    y = np.log(x / (1 - x))
    return y



def seasons_func(food_max, food_min, t, year_t):
    curr_t = (t % year_t)
    #Autumn
    if curr_t < (year_t / 2):
        wanted_food_len = int(np.round(food_max + ((food_min - food_max) / 
                                                   (year_t / 2)) * curr_t))
    else:
        wanted_food_len = int(np.round(food_min + ((food_max - food_min) / 
                                                   (year_t / 2)) * (curr_t - (year_t / 2))))
    return wanted_food_len
    

                
def seasons(settings, foods, t, T, total_timesteps):
    foods = deepcopy(foods)
    years_per_i = settings['years_per_iteration']
    min_food_rel = settings['min_food_winter']
    if years_per_i < 1:
        t = total_timesteps
    if min_food_rel > 1 or min_food_rel < 0:
        raise Exception("'min_food_winter' has to be a float between 0 and 1")
    max_food = settings['food_num']
    min_food = int(np.round(max_food * min_food_rel))
    year_t = T / years_per_i #amount of time steps corresponding to half a year

    wanted_food_len = seasons_func(max_food, min_food, t, year_t)


    
    diff_food_len = wanted_food_len - len(foods)
    
    if diff_food_len < 0:
        for i in range(abs(diff_food_len)):
            #rand = np.random.randint(0, len(foods)) Is randomness important here?
            del foods[-1]
    elif diff_food_len > 0:
        for i in range(abs(diff_food_len)):
            foods.append(food(settings))
     
    return foods

#TODO: double check if this is working as intended!
def interact(settings, isings, foods):
    '''
    consider making a matrix of values instead of looping through all organisms
    currently, there is redundancy in these loops which might end up being time consuming
    '''

    # calculate all agent-agent and agent-food distances
    Ipos = np.array( [[I.xpos, I.ypos] for I in isings] )
    foodpos = np.array( [[food.xpos, food.ypos] for food in foods] )
    dimensions = np.array([settings['x_max'] - settings['x_min'], settings['y_max'] - settings['y_min']])
    org_heading = np.array([I.r for I in isings]).reshape(len(Ipos), 1)

    dist_mat_org, theta_mat_org = pdistance_pairwise(Ipos, Ipos, dimensions, food=False)
    dist_mat_food, theta_mat_food = pdistance_pairwise(Ipos, foodpos, dimensions, food=True)

    # calculate agent-agent and agent-food angles
    theta_mat_org = theta_mat_org - org_heading
    theta_mat_food = theta_mat_food - org_heading

    theta_mat_org = np.mod(theta_mat_org, 360)
    theta_mat_org = np.where(theta_mat_org > 180, theta_mat_org - 360, theta_mat_org)

    theta_mat_food = np.mod(theta_mat_food, 360)
    theta_mat_food = np.where(theta_mat_food > 180, theta_mat_food - 360, theta_mat_food)

    # calculate org sensor

    # org_sensor = np.where(np.abs(theta_mat_org) > 90, 0, np.cos(np.deg2rad(theta_mat_org)))
    # org_radius = np.array([I.radius for I in isings]).reshape(len(Ipos), 1)
    # org_sensor = (org_sensor * org_radius) / (dist_mat_org + dist_mat_org.T + 1e-6) ** 2
    # np.fill_diagonal(org_sensor, 0)
    # org_sensor = np.sum(org_sensor, axis=1)


    for i, I in enumerate(isings):
        if settings['energy_model']:
            I.energies.append(I.energy)

        minFoodDist = np.min(dist_mat_food[i, :])
        foodInd = np.argmin(dist_mat_food[i, :])

        I.d_food = minFoodDist  # Distance to closest food
        I.r_food = theta_mat_food[i, foodInd] # "angle" to closest food

        if minFoodDist <= settings['org_radius']:
            if settings['energy_model']:
                I.energy += foods[foodInd].energy
            I.food += foods[foodInd].energy
            '''
            finess is proportional to energy
            '''
            foods[foodInd].respawn(settings)

        #I.org_sens = org_sensor[i]




#  TODO: Record mutation rate
# def mutation_rate(isings):
#     '''Record mutation rate for future plotting'''
#     for I in isings:
#
#         hmutation = np.abs(I.dh[I.maskh])
#         Jmutation = np.abs(I.dJ[I.maskJ])
#
#     hmutation = np.mean(hmutation)
#     Jmutation = np.mean(Jmutation)
#     return hmutation, Jmutation



