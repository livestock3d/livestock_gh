print('Running template DrainPoolsTemplate.py')

# Get user
user = open('user.txt','r').readline()

# Import
import sys
sys.path.insert(0, "/home/" + user + "/livestock/classes")
from RainClasses import drainPools

# Get path
poolPath = "/home/" + user + '/livestock/templates/'

# Run function
warn = drainPools(poolPath)
print(warn)

# Annouce that template finished and create out file
print('Finished with template')
file_obj = open('out.txt','w')
if warn:
    for w in warn:
        file_obj.write(w + '\n')
file_obj.close()
