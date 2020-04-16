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
    #dir = 'save/{}/generations_nat_heat_capacity_calculated.pickle'.format(sim_name)
    dir = 'save/{}/nat_heat_capacity_data/generations_nat_heat_capacity_calculated.pickle'.format(sim_name)
    file = open(dir, 'rb')
    all_heat_capacity_gens = pickle.load(file)
    file.close()
    return all_heat_capacity_gens

if __name__ == '__main__':
    sims = ['sim-20200416-003618-g_2000_-t_2000_-c_gen_200_-ref_200_-b_10_-c_props_-10_10_102_-n_first_nat_C_test_reset_line_enabled', 'sim-20200416-003611-g_2000_-t_2000_-c_gen_200_-ref_200_-b_0.1_-c_props_-10_10_102_-n_first_nat_C_test_reset_line_enabled', 'sim-20200416-003603-g_2000_-t_2000_-c_gen_200_-ref_200_-b_1_-c_props_-5_5_102_-n_first_nat_C_test_reset_line_enabled', 'sim-20200416-003527-g_2000_-t_2000_-c_gen_200_-ref_200_-b_1_-c_props_-10_10_102_-n_first_nat_C_test_reset_line_enabled', 'sim-20200416-003407-g_2000_-t_2000_-c_gen_200_-ref_200_-b_0.1_-n_first_nat_C_test_reset_line_enabled', 'sim-20200416-003357-g_2000_-t_2000_-c_gen_200_-ref_200_-b_10_-n_first_nat_C_test_reset_line_enabled', 'sim-20200416-003347-g_2000_-t_2000_-c_gen_200_-ref_200_-b_1_-n_first_nat_C_test_reset_line_enabled', 'sim-20200416-003238-g_2000_-t_2000_-c_gen_200_-ref_200_-b_10_-n_first_nat_C_test_reset_line_disabled', 'sim-20200416-003227-g_2000_-t_2000_-c_gen_200_-ref_200_-b_0.1_-n_first_nat_C_test_reset_line_disabled', 'sim-20200416-003217-g_2000_-t_2000_-c_gen_200_-ref_200_-b_1_-n_first_nat_C_test_reset_line_disabled']
    for sim in sims:
        plot_all_possible_gens(sim)
    # sim = 'sim-20200416-003618-g_2000_-t_2000_-c_gen_200_-ref_200_-b_10_-c_props_-10_10_102_-n_first_nat_C_test_reset_line_enabled'
    # plot_all_possible_gens(sim)