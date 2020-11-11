from automatic_plot_helper import all_folders_in_dir_with

def delete(delete_settings):
    dirs_in_save = all_folders_in_dir_with(delete_settings['delete_in_dir'], 'sim')
    for dir_in_save in dirs_in_save:
        if

if __name__ == '__main__':
    delete_settings = {}
    delete_settings['delete_in_dir'] = 'save/'
    delete(delete_settings)