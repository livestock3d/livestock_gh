print('Running template DrainPoolsTemplate.py')

# Get user
user = open('user.txt','r').readline()

# Import
import sys
sys.path.insert(0, "/home/" + user + "/livestock/classes")
from RainClasses import drainPools

# Get path
poolPath = '/home/' + user + '/livestock/templates/'

# Run function
b = drainPools(poolPath)

# Annouce that template finished and create out file
print('Finished with template')
sys.stdout = open('out.txt','w')