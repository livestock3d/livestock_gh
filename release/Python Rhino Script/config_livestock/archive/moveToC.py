from shutil import copyfile

source_folder = r'C:\Users\Christian\Dropbox\Arbejde\DTU BYG\Livestock\livestock_gh\python'
destination_folder = r'C:\livestock\python'

# comp folder
src_comp = source_folder + '\\comp'
des_comp = destination_folder + '\\comp'

copyfile(src_comp + '\\__init__.py', des_comp + '\\__init__.py')
copyfile(src_comp + '\\comp_cmf.py', des_comp + '\\comp_cmf.py')
copyfile(src_comp + '\\comfort.py', des_comp + '\\comfort.py')
copyfile(src_comp + '\\component.py', des_comp + '\\component.py')
copyfile(src_comp + '\\component_list.txt', des_comp + '\\component_list.txt')
copyfile(src_comp + '\\geometry.py', des_comp + '/geometry.py')
copyfile(src_comp + '\\misc.py', des_comp + '\\misc.py')
copyfile(src_comp + '\\rain.py', des_comp + '\\rain.py')
copyfile(src_comp + '\\vegetation.py', des_comp + '\\vegetation.py')

# gh folder
src_gh = source_folder + '\\gh'
des_gh = destination_folder + '\\gh'

copyfile(src_gh + '\\__init__.py', des_gh + '\\__init__.py')
copyfile(src_gh + '\\misc.py', des_gh + '\\misc.py')
copyfile(src_gh + '\\geometry.py', des_gh + '\\geometry.py')
copyfile(src_gh + '\\ssh.py', des_gh + '\\ssh.py')
copyfile(src_gh + '\\xmltodict.py', des_gh + '\\xmltodict.py')

# lib folder
src_lib = source_folder + '\\lib'
des_lib = destination_folder + '\\lib'

copyfile(src_lib + '\\__init__.py', des_lib + '\\__init__.py')
copyfile(src_lib + '\\lib_cmf.py', des_lib + '\\lib_cmf.py')
copyfile(src_lib + '\\csv.py', des_lib + '\\csv.py')
copyfile(src_lib + '\\geometry.py', des_lib + '\\geometry.py')
copyfile(src_lib + '\\rain.py', des_lib + '\\rain.py')
copyfile(src_lib + '\\plant.py', des_lib + '\\plant.py')

# win folder
src_win = source_folder + '\\win'
des_win = destination_folder + '\\win'

copyfile(src_win + '\\__init__.py', des_win + '\\__init__.py')
copyfile(src_win + '\\templates.py', des_win + '\\templates.py')
copyfile(src_win + '\\ssh.py', des_win + '\\ssh.py')
copyfile(src_win + '\\misc.py', des_win + '\\misc.py')
copyfile(src_win + '\\win_cmf.py', des_win + '\\win_cmf.py')

# root folder
copyfile(source_folder + '\\__init__.py', destination_folder + '\\__init__.py')
copyfile(source_folder + '\\livestock_comp.py', destination_folder + '\\livestock_comp.py')
copyfile(source_folder + '\\livestock_lib.py', destination_folder + '\\livestock_lib.py')
copyfile(source_folder + '\\livestock_win.py', destination_folder + '\\livestock_win.py')
copyfile(source_folder + '\\livestock_gh.py', destination_folder + '\\livestock_gh.py')
copyfile(source_folder + '\\setup.py', destination_folder + '\\setup.py')