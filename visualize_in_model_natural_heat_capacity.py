from automatic_plot_helper import load_isings_attributes_from_list
import matplotlib.pyplot as plt
import matplotlib
import pickle
from os import path, makedirs


def plot_heat_cap(heat_cap_vecs, beta_vecs, gen, sim_name):
    savefolder =  'save/{}/figs/nat_heat_cap/'.format(sim_name)
    savefilename = savefolder + 'nat_heat_cap' + '-Nbetas_' + str(len(beta_vecs[0])) + '-gen_' + str(gen) + '.png'
    if not path.exists(savefolder):
        makedirs(savefolder)


    fig, ax = plt.subplots(1, 1, figsize=(11, 10), sharex=True)
    fig.text(0.51, 0.035, r'$\beta$', ha='center', fontsize=28)
    fig.text(0.005, 0.5, r'$C/N$', va='center', rotation='vertical', fontsize=28)
    title = 'Natural Specific Heat of Foraging Community\n Generation: ' + str(gen)
    fig.suptitle(title)

    for heat_cap_vec, beta_vec in zip(heat_cap_vecs, beta_vecs):
        plt.scatter(beta_vec, heat_cap_vec)
        ax.scatter(beta_vec, heat_cap_vec, s=30, alpha=0.3, marker='o', label=None)

    xticks = [0.1, 0.5, 1, 2, 4, 10]
    ax.set_xscale("log", nonposx='clip')
    #ax.set_xscale("log")
    ax.set_xticks(xticks)
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    upperbound = 0.4
    #plt.axis([0.1, 10, 0, upperbound])

    print('Saving nat heat capacity plot: {}'.format(savefilename))
    plt.savefig(savefilename, bbox_inches='tight', dpi=300)




def load_and_plot(sim_name, gens):
    heat_cap_vecs_gens = load_isings_attributes_from_list(sim_name, gens, 'heat_capacity_vec')
    beta_vecs_gens = load_isings_attributes_from_list(sim_name, gens, 'beta_vec')
    for heat_cap_vecs, beta_vecs, gen in zip(heat_cap_vecs_gens, beta_vecs_gens, gens):
        plot_heat_cap(heat_cap_vecs, beta_vecs, gen, sim_name)

def plot_all_possible_gens(sim_name):
    all_heat_capacity_gens = load_gens_with_heat_cap(sim_name)
    load_and_plot(sim_name, all_heat_capacity_gens)

def load_gens_with_heat_cap(sim_name):
    dir = 'save/{}/generations_nat_heat_capacity_calculated.pickle'.format(sim_name)
    file = open(dir, 'rb')
    all_heat_capacity_gens = pickle.load(file)
    file.close()
    return all_heat_capacity_gens

if __name__ == '__main__':
    plot_all_possible_gens('sim-20200415-215516-g_10_-t_50_-ref_0_-noplt_-c_gen_4')