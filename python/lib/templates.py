__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.1.0"

# -------------------------------------------------------------------------------------------------------------------- #
# Livestock Templates Functions


def pick_template(template_name, path):

    template_name = str(template_name)

    if template_name == 'drain_mesh':
        drain_mesh_template(path)

    elif template_name == 'drain_pools':
        pass
        # drain_pools_template(path)

    elif template_name == 'fix_mesh':
        pass
        # fix_mesh_template(path)

    elif template_name == 'ssh':
        ssh_template(path)

    elif template_name == 'topographic_index':
        pass
        # topographic_index_template(path)

    elif template_name == 'cmf':
        cmf_template(path)

    elif template_name == 'cmf_results':
        process_cmf_results(path)

    elif template_name == 'cfd_ssh':
        pass
        # cfd_ssh_template(path)

    elif template_name == 'cmf_surface_results':
        process_cmf_surface_results(path)

    elif template_name == 'new_air':
        new_air_conditions(path)

    else:
        raise NameError('Could not find template: ' + str(template_name))

    return True


def print_template_header(template):
    print('---------------------------------------------------')
    print('')
    print('                     LIVESTOCK                    ')
    print('                  Running Template:')
    print('                       ' + str(template))
    print('')
    print('---------------------------------------------------')


def drain_mesh_template(path):
    file_name = r'/drain_mesh_template.py'
    print_template_header(file_name)
    file = open(path + file_name, 'w')

    file.write("print('Running template drain_mesh_template.py')\n")

    file.write("# Imports\n")
    file.write("from pathlib import Path\n")
    file.write("home_user = str(Path.home())\n")
    file.write("from livestock_linux.rain import drain_mesh_paths\n")

    file.write("# Run function\n")
    file.write("drain_mesh_paths(home_user + '/livestock/ssh')\n")

    file.write("# Announce that template finished and create out file\n")
    file.write("print('Finished with template')\n")
    file.write("file_obj = open('out.txt', 'w')\n")
    file.write("file_obj.close()")
    file.close()

    return True

"""
def drain_pools_template(path):
    file = open('DrainPoolsTemplate.py', 'w')
    file.write("print('Running template DrainPoolsTemplate.py')")

    file.write("# Get user")
    file.write("user = open('user.txt', 'r').readline()")

    file.write("# Import")
    file.write("import sys")
    file.write("sys.path.insert(0, '/home/' + user + '/livestock/classes')")
    file.write("from RainClasses import drainPools")

    file.write("# Get path")
    file.write("poolPath = '/home/' + user + '/livestock/templates/'")

    file.write("# Run function")
    file.write("warn = drainPools(poolPath)")
    file.write("print(warn)")

    file.write("# Annouce that template finished and create out file")
    file.write("print('Finished with template')")

    return True
"""
"""
def fix_mesh_template(path):
    file = open('FixMeshTemplate.py', 'w')
    file.write("print('Running template FixMeshTemplate.py')")

    file.write("# Get user")
    file.write("user = open('user.txt', 'r').readline()")

    file.write("# Imports")
    file.write("import sys")
    file.write("import pymesh as pm")
    file.write("sys.path.insert(0, '/home/' + user + '/livestock/classes')")
    file.write("from GeometryClasses import fix_mesh")

    file.write("# Get files")
    file.write("meshPath = '/home/' + user + '/livestock/templates/mesh.obj'")
    file.write("outPath = '/home/' + user + '/livestock/templates/fixedMesh.obj'")
    file.write("detail = open('detail.txt', 'r').readline()")

    file.write("# Run function")
    file.write("mesh = pm.load_mesh(meshPath)")
    file.write("mesh = fix_mesh(mesh, detail=detail)")
    file.write("pm.save_mesh(outPath, mesh)")

    file.write("# Annouce that template finished and create out file")
    file.write("print('Finished with template')")
    file.write("file_obj = open('out.txt', 'w')")
"""

def ssh_template(path):
    file_name = r'/ssh_template.py'
    print_template_header(file_name)
    file = open(path + file_name, 'w')

    file.write("# Imports\n")
    file.write("import sys\n")
    file.write("import livestock_win.ssh as win_ssh\n")

    file.write("# Run function\n")
    file.write("win_ssh.ssh_connection()\n")

    file.close()

    return True

"""
def topographic_index_template(path):
    file = open(path + '\\topographicIndexTemplate.py', 'w')
    file.write("print('Running template topographicIndexTemplate.py')\n")

    file.write("# Imports\n")
    file.write("from pathlib import Path\n")
    file.write("import sys\n")
    file.write("homeUser = str(Path.home())\n")
    file.write("sys.path.insert(0, homeUser + '/livestock/classes')\n")
    file.write("from RainClasses import topographicIndex\n")

    file.write("# Get files\n")
    file.write("meshPath = homeUser + '/livestock/templates/drainMesh.obj'\n")
    file.write("drainfaces = homeUser + '/livestock/templates/drainfaces.txt'\n")

    file.write("# Run function\n")
    file.write("topographicIndex(meshPath, drainfaces)\n")

    file.write("# Announce that template finished and create out file\n")
    file.write("print('Finished with template')\n")
    file.write("file_obj = open('out.txt', 'w')")
"""

def cmf_template(path):
    file_name = r'/cmf_template.py'
    print_template_header(file_name)
    file = open(path + file_name, 'w')

    file.write("# Imports\n")
    file.write("from pathlib import Path\n")
    file.write("home_user = str(Path.home())\n")
    file.write("from livestock_linux.lib_cmf import CMFModel\n")

    file.write("# Run CMF Model\n")
    file.write("folder = home_user + '/livestock/ssh'\n")
    file.write("model = CMFModel(folder)\n")
    file.write("model.run_model()\n")

    file.write("# Announce that template finished and create out file\n")
    file.write("print('Finished with template')\n")
    file.write("file_obj = open('out.txt', 'w')\n")
    file.write("file_obj.close()")

    return True


def process_cmf_results(path):
    file_name = r'/cmf_results_template.py'
    file = open(path + file_name, 'w')

    file.write("# Imports\n")
    file.write("import livestock_win.win_cmf as win_cmf\n")

    file.write("# Run function\n")
    file.write("win_cmf.cmf_results(r'" + path + "')\n")

    file.write("# Announce that template finished and create out file\n")
    file.write("print('Finished with template')\n")

    file.close()

    return True


def process_cmf_surface_results(path):
    file_name = r'/cmf_surface_results_template.py'
    file = open(path + file_name, 'w')

    file.write("# Imports\n")
    file.write("import livestock_win.win_cmf as win_cmf\n")

    file.write("# Run function\n")
    file.write("win_cmf.surface_flux_results(r'" + path + "')\n")

    file.write("# Announce that template finished and create out file\n")
    file.write("print('Finished with template')\n")

    file.close()

    return True

"""
def cfd_ssh_template(path):
    file_name = r'/cfd_ssh_template.py'
    file = open(path + file_name, 'w')
    print_template_header(file_name)

    file.write("# Imports\n")
    file.write("from pathlib import Path\n")
    file.write("import sys\n")
    file.write("home_user = str(Path.home())\n")
    file.write("sys.path.insert(0, home_user + '/livestock')\n")
    file.write("from lib.misc import run_cfd\n")

    file.write("# Run function\n")
    file.write("run_cfd(home_user + '/livestock/ssh')\n")

    file.write("# Announce that template finished and create out file\n")
    file.write("print('Finished with template')\n")
    file.write("file_obj = open('out.txt', 'w')\n")
    file.write("file_obj.close()")
"""

def new_air_conditions(path):
    file_name = r'/new_air_conditions_template.py'
    file = open(path + file_name, 'w')

    file.write("# Imports\n")
    file.write("import livestock_linux.air as la\n")

    file.write("# Run function\n")
    file.write("la.NewTemperatureAndRelativeHumidity(r'" + path + "').run()\n")

    file.write("# Announce that template finished and create out file\n")
    file.write("print('Finished with template')\n")

    file.close()

    return True
