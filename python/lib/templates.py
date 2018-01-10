__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.1.0"

# -------------------------------------------------------------------------------------------------------------------- #
# Livestock Templates Functions


def pick_template(template_name, path):
    """
    Writes a template given a template name and path to write it to.
    :param template_name: Template name.
    :param path: Path to save it to.
    """

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
        return new_air_conditions(path)

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
    """
    Writes the template for the drain mesh function.
    :param path: Path to write it to.
    """

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
    """
    Writes the ssh template.
    :param path: Path to write it to.
    """

    file_name = r'/ssh_template.py'
    print_template_header(file_name)
    file = open(path + file_name, 'w')

    file.write("# Imports\n")
    file.write("import sys\n")
    file.write("import livestock.ssh as ssh\n")

    file.write("# Run function\n")
    file.write("ssh.ssh_connection()\n")

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
    """
    Writes the CMF template.
    :param path: Path to write it to.
    """

    file_name = r'/cmf_template.py'
    print_template_header(file_name)
    file = open(path + file_name, 'w')

    file.write("# Imports\n")
    file.write("from pathlib import Path\n")
    file.write("home_user = str(Path.home())\n")
    file.write("from livestock.hydrology import CMFModel\n")

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
    """
    Writes the CMF result lookup template.
    :param path: Path to write it to.
    """

    file_name = r'/cmf_results_template.py'
    file = open(path + file_name, 'w')

    file.write("# Imports\n")
    file.write("import livestock.hydrology as lh\n")

    file.write("# Run function\n")
    file.write("lh.cmf_results(r'" + path + "')\n")

    file.write("# Announce that template finished and create out file\n")
    file.write("print('Finished with template')\n")

    file.close()

    return True


def process_cmf_surface_results(path):
    """
    Writes the CMF surface result template.
    :param path: Path to write it to.
    """

    file_name = r'/cmf_surface_results_template.py'
    file = open(path + file_name, 'w')

    file.write("# Imports\n")
    file.write("import livestock.hydrology as hy\n")

    file.write("# Run function\n")
    file.write("hy.surface_flux_results(r'" + path + "')\n")

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
    """
    Writes the new air condition template.
    :param path: Path to write it to.
    """

    file_name = r'/new_air_conditions_template.py'
    file = open(path + file_name, 'w')

    file.write("# Imports\n")
    file.write("import livestock.air as la\n")

    file.write("# Run function\n")
    file.write("if __name__ == '__main__':\n")
    file.write("\tla.new_temperature_and_relative_humidity(r'" + path + "')\n")

    file.write("# Announce that template finished and create out file\n")
    file.write("print('Finished with template')\n")

    file.close()

    return file_name
