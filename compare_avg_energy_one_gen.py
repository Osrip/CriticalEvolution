from automatic_plot_helper import load_isings_attributes_from_list
from automatic_plot_helper import detect_all_isings
import warnings


def main(sim_name1, sim_name2):
    all_generations1 = detect_all_isings(sim_name1)
    all_generations2 = detect_all_isings(sim_name2)
    if all_generations1 != all_generations2:
        warnings.warn('Both simulations have a differnt amount of generations, plotting generationb {} of simulation 1 '
                      'and generation {} of simulation 2'.format(all_generations1[-1], all_generations2[-1]))

    load_isings_attributes_from_list(sim_name1, all_generations1, 'avg_energy')




