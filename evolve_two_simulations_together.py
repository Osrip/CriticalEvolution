from train import create_settings  # This runs arg parser and sets up settings
from embodied_ising import EvolutionLearning
from embodied_ising import ising
from embodied_ising import food
from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import detect_all_isings

def evolve_together(sim_name1, sim_name2):

    settings, Iterations = create_settings()

    foods = []
    for i in range(0, settings['food_num']):
        foods.append(food(settings))

    isings_new = merge_ising_files(sim_name1, sim_name2)
    sim_name, not_used_isings = EvolutionLearning(isings_new, foods, settings, Iterations)


def merge_ising_files(sim_name1, sim_name2):
    last_gen1 = detect_all_isings(sim_name1)[-1]
    last_gen2 = detect_all_isings(sim_name2)[-1]
    isings1 = load_isings_from_list(sim_name1, [last_gen1], wait_for_memory=False)[0]
    isings2 = load_isings_from_list(sim_name2, [last_gen2], wait_for_memory=False)[0]

    isings_new = isings1[:25] + isings2[:25]

    return isings_new

if __name__ == '__main__':
    # sim_name1 = 'Energies_Velocities_saved_during_2d_sim_random_time_steps_cut_off_animations/sim-20200604-235424-g_2000_-t_2000_-b_1_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    # sim_name2 = 'Energies_Velocities_saved_during_2d_sim_random_time_steps_cut_off_animations/sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    sim_name1 = 'Energies_Velocities_saved_during_2d_sim_random_time_steps_cut_off_animations/sim-20200619-173349-g_2001_-ref_0_-noplt_-b_1_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4'
    sim_name2 = 'Energies_Velocities_saved_during_2d_sim_random_time_steps_cut_off_animations/sim-20200619-173340-g_2001_-ref_0_-noplt_-b_10_-dream_c_500_-c_4_-a_1995_1996_1997_1998_1999_-n_random_time_steps_save_energies_4'
    evolve_together(sim_name1, sim_name2)
