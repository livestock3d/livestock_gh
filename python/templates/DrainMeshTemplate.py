print('Running template DrainMeshTemplate.py')

# Get user
user = open('user.txt','r').readline()

# Imports
import sys
sys.path.insert(0, "~/livestock/classes")
from RainClasses import drainMeshPaths

# Get files
meshPath = '~/livestock/templates/drainMesh.obj'
cpu = open('~/livestock/templates/cpu.txt','r').readline()

# Run function
warn = drainMeshPaths(meshPath, int(cpu))
print(warn)

# Annouce that template finished and create out file
print('Finished with template')
file_obj = open('out.txt','w')
if warn:
    for w in warn:
        file_obj.write(w + '\n')
file_obj.close()