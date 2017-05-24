# Import
import sys
sys.path.insert(0, "/mnt/c/Users/Christian/Dropbox/Arbejde/DTU BYG/Livestock/Kode - Livestock/01 Python/Classes/")
import RainClasses as rc
import os

print('reached template')
meshPath = 'drainMesh.obj'
cpu = open('cpu.txt','r').readline()
rc.drainMeshPaths(meshPath, int(cpu))
sys.stdout = open('out.txt','w')