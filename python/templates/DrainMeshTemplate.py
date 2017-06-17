print('Running template DrainMeshTemplate.py')

# Get user
user = open(r'C:\livestock\python\ssh\user.txt','r').readline()

# Imports
import sys
sys.path.insert(0, "/home/" + user + "/livestock/classes")
from RainClasses import drainMeshPaths

# Get files
meshPath = '/home/' + user + '/livestock/templates/drainMesh.obj'
cpu = open('/home/' + user + '/livestock/templates/cpu.txt','r').readline()

# Run function
drainMeshPaths(meshPath, int(cpu))

# Annouce that template finished and create out file
print('Finished with template')
sys.stdout = open('out.txt','w')