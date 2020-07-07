from automatic_plot_helper import load_settings
from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import detect_all_isings
import matplotlib.pyplot as plt
from os import path
from os import makedirs

def plot(sim_name, generation):
    #last_gen = detect_all_isings(sim_name)[-1]
    last_isings = load_isings_from_list(sim_name, [generation])[0]
    betas = [I.Beta for I in last_isings]
    avg_energies = [I.avg_energy for I in last_isings]
    plt.figure()
    plt.xlabel('Beta')
    plt.ylabel('avg_energy')
    plt.scatter(betas, avg_energies, s=5)
    savedir = 'save/{}/figs/beta_vs_avg_energy_one_gen/'.format(sim_name)
    if not path.exists(savedir):
        makedirs(savedir)
    savename = 'beta_vs_avg_energy_one_gen.png'
    plt.savefig(savedir+savename, dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    #sim_name = 'sim-20200705-212507-g_2000_-t_2000_-ref_100_-n_evolve_together_sim-20200604-235424-g_2000_-t_2000_-b_1___sim-20200604-235433-g_2000_-t_2000_-b_10'
    sim_name = 'sim-20200705-211207-g_2000_-t_2000_-ref_100_-n_evolve_together_sim-20200619-173349-g_2001_-ref_0_-noplt_-b_1_sim-20200619-173340-g_2001_-ref_0_-noplt_-b_10_random_time_steps_save_energies_4'
    plot(sim_name, 0)