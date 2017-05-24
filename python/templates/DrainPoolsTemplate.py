user = open('/mnt/c/livestock/python/templates/user.txt','r').readline()

# Import
import sys
sys.path.insert(0, "/home/" + user + "/classes/")
import RainClasses as rc

print('reached template')
poolPath = "/mnt/c/livestock/python/templates"
b = rc.drainPools(poolPath)
sys.stdout = open('out.txt','w')