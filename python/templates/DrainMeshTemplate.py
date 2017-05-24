user = open('/mnt/c/livestock/python/templates/user.txt','r').readline()

# Import
import sys
sys.path.insert(0, "/home/" + user + "/classes/")
import RainClasses as rc

print('reached template')
meshPath = '/mnt/c/livestock/python/templates/drainMesh.obj'
cpu = open('cpu.txt','r').readline()
rc.drainMeshPaths(meshPath, int(cpu))
sys.stdout = open('out.txt','w')