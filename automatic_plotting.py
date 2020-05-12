import os
import matplotlib as mpl
mpl.use('Agg') #For server use
from automatic_plot_helper import load_settings
from automatic_plot_helper import load_isings
import compute_and_plot_heat_capacity_automatic
import plot_anything_combined
import plot_anythingXY_scatter
import plot_anythingXY_scatter_food_velocity_optimized
import sys


import plot_anythingXY_scatter_animation

def main(sim_name, load_isings_list=True, final=False):
    '''
    final defines whether this is the final/ last generation of simulation is plotted
    '''
    settings = load_settings(sim_name)
    if load_isings_list:
        isings_list = load_isings(sim_name)
    try:
        plot_anything_auto(sim_name, ['Beta', 'avg_velocity', 'food'], settings, isings_list=isings_list, autoLoad=False)
    except Exception:
        print('Could not create generational plots')
    #plot_var_tuples = [('Beta', 'avg_velocity'), ('avg_energy', 'avg_velocity'), ('avg_energy', 'food')]
    plot_var_tuples = [('generation', 'avg_energy'), ('generation', 'avg_velocity'), ('generation', 'food')]
    try:
        plot_scatter_auto(sim_name, settings, plot_var_tuples, isings_list, autoLoad=False)
    except Exception:
        print('Could not create scatter plot')
    try:
        plot_anythingXY_scatter_food_velocity_optimized.main(sim_name, settings, isings_list, 'avg_velocity', 'food', s=0.8,
                                                             alpha=0.05, autoLoad=False)
    except Exception:
        print('Could not create food velocity scatter plot')

    del isings_list
    if final:
        try:
            if settings['cores'] != 0:
                compute_and_plot_heat_capacity_automatic.main(sim_name, settings)

        except Exception:
            print('Could not compute and plot heat capacity')

    #  Trying to fix memory leak:

    del settings

    #plot_anythingXY_scatter_animation.main(sim_name, settings, isings_list, autoLoad=False, x_lim=None, y_lim=None)
    #  TODO: Animation dies not work for some reasone when called from here but does work when it is called itself... WHY???

def plot_scatter_auto(sim_name, settings, plot_var_tuples, isings_list, autoLoad = True):
    for plot_var_x, plot_var_y in plot_var_tuples:
        plot_anythingXY_scatter.main(sim_name, settings, isings_list, plot_var_x, plot_var_y, s=0.8, alpha=0.05,
                                     autoLoad=autoLoad, name_extension='')

def plot_anything_auto(sim_name, plot_vars, settings, isings_list = None, autoLoad = True):
    '''
    :param plot_vars: List of string of which each represents an attribute of the isings class
    :param isings_list: List of all isings generations in case it has been loaded previously
    '''

    if settings['energy_model']:
        #os.system("python plot__anything_combined {} avg_energy".format(sim_name))
        plot_anything_combined.main([sim_name], 'avg_energy', isings_lists=[isings_list], autoLoad=autoLoad)
    else:
        #os.system("python plot__anything_combined {} fitness".format(sim_name))
        plot_anything_combined.main([sim_name], 'fitness', isings_lists=[isings_list], autoLoad=autoLoad)

    for plot_var in plot_vars:
        plot_anything_combined.main([sim_name], plot_var, isings_lists=[isings_list], autoLoad=autoLoad, scatter=True)




def plot_all_in_folder(folder_name):
    '''
    :param folder_name: Has to be a sub_folder of save/
    :return:
    '''
    directory_list = [f.path for f in os.scandir('save/{}'.format(folder_name)) if f.is_dir()]
    for sim_name in directory_list:
        if 'sim-' in sim_name:
            sim_name = sim_name.replace('save/', '')
            main(sim_name)



if __name__ == '__main__':
    '''
    first argument sim_name
    second argument 'final_true' in case it is final run 'final_false' otherwise
    '''

    #sim_name ='3rd_4th_run_figures_training_runs_examples/sim-20200209-124814-ser_-b_10_-f_100_-n_1' #'sim-20200123-210723-g_20_-t_20_-ypi_0.05_-mf_0.1_-n_test' # 'sim-20191229-191241-ser_-s_-b_10_-ie_2_-a_0_500_1000_2000' #'sim-20200103-170603-ser_-s_-b_0.1_-ie_2_-a_0_200_500_1000_1500_1999'#'sim-20200103-170556-ser_-s_-b_1_-ie_2_-a_0_500_1000_1500_1999'
    final = False
    if sys.argv[2] == 'final_true':
        final = True
    main(sys.argv[1], final=final)
    # sim_names = ['sim-20200209-124814-ser_-b_10_-f_100_-n_1',
    #             'sim-20200209-124814-ser_-b_10_-f_10_-n_1',
    #             'sim-20200209-124814-ser_-b_1_-f_100_-n_1',
    #             'sim-20200209-124814-ser_-b_1_-f_10_-n_1']
    # for sim_name in sim_names:
    #     main(sim_name)
    #plot_all_in_folder('seasons_training_one_season')

