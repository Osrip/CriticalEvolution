import numpy as np
from itertools import combinations, product
import copy


def mutate_genotype_main(isings_orig, gene_perturb, perturb_const, num_perturbed_edges, sim_settings):
    isings_orig = copy.deepcopy(isings_orig)
    isings_changed = []
    for I in isings_orig:
        isings_changed.append(change_genotype_ising(I, gene_perturb, perturb_const, num_perturbed_edges, sim_settings))
    return isings_changed


def change_genotype_ising(I, gene_perturb, perturb_const, num_perturbed_edges, sim_settings):
    numDisconnectedEdges = len(list(combinations(range(sim_settings['numDisconnectedNeurons']), 2)))
    totalPossibleEdges = len(list(combinations(range(I.size - I.Ssize - I.Msize), 2)))

    # number of (dis)connected edges
    connected = copy.deepcopy(I.maskJ)

    disconnected = ~connected #disconnected not connected
    np.fill_diagonal(disconnected, 0)
    disconnected = np.triu(disconnected)

    # things that need to be connected and not flagged to change
    connected[0:I.Ssize, :] = 0
    connected[:, -I.Msize:] = 0
    # things that need to be disconnected and not flagged to change
    disconnected[0:I.Ssize, -I.Msize:] = 0
    disconnected[0:I.Ssize, 0:I.Ssize] = 0

    numEdges = np.sum(connected) #number of edges, that can actuall be disconnected (in beginning of simulatpn curr settings 3)
    # positive value means too many edges, negative value means too little
    edgeDiff = numEdges - (totalPossibleEdges - numDisconnectedEdges)

    i_conn, j_conn = np.nonzero(connected) #Indecies of neurons connected by edges that are connected

    # !!!! Genotype changing Algorithm !!!!
    for _ in range(num_perturbed_edges):

        randindex = np.random.randint(0, len(i_conn))
        rand_sign = np.random.randint(0, 2) * 2 - 1

        i_change = i_conn[randindex]
        j_change = j_conn[randindex]

        I.J[i_change, j_change] += gene_perturb * perturb_const * rand_sign
    return I