from automatic_plot_helper import load_isings_from_list
from automatic_plot_helper import detect_all_isings
from automatic_plot_helper import load_settings
import numpy as np
import copy
from embodied_ising import EvolutionLearning
from embodied_ising import food


def test_robustness(sim_name, num_evaluate_different_inds = 5, repeat_mutations=20, load_generation=False, pop_size=50, time_steps=2000):
    if not load_generation:
        load_generation = detect_all_isings(sim_name)[-1]
    settings = load_settings(sim_name)
    settings['pop_size'] = pop_size
    settings['TimeSteps'] = time_steps
    settings['save_data'] = False
    settings['plot_pipeline'] = False
    # Das ist nur zu test-pfuschzwecken da kann irgendwann weg:_
    settings['random_time_steps'] = False
    foods = []
    for i in range(0, settings['food_num']):
        foods.append(food(settings))

    isings = load_isings_from_list(sim_name, [load_generation], wait_for_memory=False)[0]

    all_inds_evaluated = []
    for ind in range(num_evaluate_different_inds):
        # Only take first 20 inds, those are the not recently mutated
        chosen_I = isings[ind]
        one_agend_all_repeats_list = []
        for rep in range(repeat_mutations):
            network_edge_positions = np.argwhere(chosen_I.maskJ == True)
            rand_pos = np.random.randint(0, len(network_edge_positions))
            mutate_edge_pos = network_edge_positions[rand_pos]
            chosen_I.J[mutate_edge_pos] = np.random.uniform(-1, 1) * chosen_I.max_weights
            clone_isings = []
            for i in range(pop_size):
                clone_isings.append(copy.deepcopy(chosen_I))


            blub, evaluated_isings = EvolutionLearning(isings, foods, settings, Iterations=1)

            one_agend_all_repeats_list.append(evaluated_isings)
        all_inds_evaluated.append(one_agend_all_repeats_list)

    return all_inds_evaluated

if __name__ == '__main__':
    sim_name = 'Energies_Velocities_saved_during_2d_sim_random_time_steps_cut_off_animations/sim-20200604-235433-g_2000_-t_2000_-b_10_-dream_c_0_-nat_c_0_-ref_0_-rec_c_0_-n_energies_velocities_saved'
    num_evaluate_diff_inds = 2
    repeat_mutations = 20
    time_steps = 200
    test_robustness(sim_name, num_evaluate_different_inds=num_evaluate_diff_inds, repeat_mutations=repeat_mutations, time_steps=time_steps)