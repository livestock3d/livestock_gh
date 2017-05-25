user = open('/mnt/c/livestock/python/templates/user.txt','r').readline()

# Import
import sys
sys.path.insert(0, "/home/" + user + "/livestock/classes")
import RainClasses as rc

print('reached template')
meshPath = '/mnt/c/livestock/python/templates/drainMesh.obj'
cpu = open('/mnt/c/livestock/python/templates/cpu.txt','r').readline()
rc.drainMeshPaths(meshPath, int(cpu))
print('finished with template')
sys.stdout = open('out.txt','w')