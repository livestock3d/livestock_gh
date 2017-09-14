__author__ = "Christian Kongsgaard"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Christian Kongsgaard"
__email__ = "ocni@dtu.dk"
__status__ = "Work in Progress"

#----------------------------------------------------------------------------------------------------------------------#
#Functions and Classes

def drainMeshTemplate():
    file = open('DrainMeshTemplate.py','w')
    file.write("print('Running template DrainMeshTemplate.py')\n")

    #file.write("# Get user\n")
    file.write("# Imports\n")
    file.write("from pathlib import Path\n")
    file.write("import sys\n")
    file.write("homeUser = str(Path.home())\n")
    file.write("sys.path.insert(0, homeUser + '/livestock/classes')\n")
    file.write("from RainClasses import drainMeshPaths\n")

    file.write("# Get files\n")
    file.write("meshPath = homeUser + '/livestock/templates/drainMesh.obj'\n")
    file.write("cpu = open(homeUser + '/livestock/templates/cpu.txt','r').readline()\n")

    file.write("# Run function\n")
    file.write("warn = drainMeshPaths(meshPath, int(cpu))\n")
    file.write("print(warn)\n")

    file.write("# Annouce that template finished and create out file\n")
    file.write("print('Finished with template')\n")

    return True

def drainPoolsTemplate():
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

def fixMeshTemplate():
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

def sshTemplate(path):
    file = open(path + '\\sshTemplate.py', 'w')

    file.write("# Imports\n")
    file.write("import sys\n")
    file.write("sys.path.insert(0, 'C:\livestock\python\classes')\n")
    file.write("from SSHClasses import sshConnection\n")

    file.write("# Run function\n")
    file.write("sshConnection()\n")

    file.write("# Announce that template finished and create out file\n")
    file.write("print('SSH Template written')")

    file.close()

    return True

def topologicalIndexTemplate(path):
    file = open(path + '\\TopologicalIndexTemplate.py', 'w')
    file.write("print('Running template topologicalIndexTemplate.py')\n")

    file.write("# Imports\n")
    file.write("from pathlib import Path\n")
    file.write("import sys\n")
    file.write("homeUser = str(Path.home())\n")
    file.write("sys.path.insert(0, homeUser + '/livestock/classes')\n")
    file.write("from RainClasses import topologicalIndex\n")

    file.write("# Get files\n")
    file.write("meshPath = homeUser + '/livestock/templates/drainMesh.obj'\n")
    file.write("drainfaces = open(homeUser + '/livestock/templates/drainfaces.txt','r').readline()\n")

    file.write("# Run function\n")
    file.write("topologicalIndex(meshPath, drainfaces)\n")

    file.write("# Announce that template finished and create out file\n")
    file.write("print('Finished with template')\n")

#path = r'C:\livestock\python\ssh'

