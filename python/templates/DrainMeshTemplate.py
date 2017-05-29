print('Running template DrainMeshTemplate.py')

# Get user
user = open('user.txt','r').readline()

# Imports
import sys
sys.path.insert(0, "/home/" + user + "/livestock/classes")
import RainClasses as rc

# Get files
meshPath = '/home/' + user + '/livestock/templates/drainMesh.obj'
cpu = open('/home/' + user + '/livestock/templates/cpu.txt','r').readline()

# Run function
rc.drainMeshPaths(meshPath, int(cpu))

# Annouce that template finished and create out file
print('Finished with template')
sys.stdout = open('out.txt','w')