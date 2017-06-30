print('Running template FixMeshTemplate.py')

# Get user
user = open('user.txt','r').readline()

# Imports
import sys
import pymesh as pm
sys.path.insert(0, "/home/" + user + "/livestock/classes")
from GeometryClasses import fix_mesh

# Get files
meshPath = "/home/" + user + '/livestock/templates/mesh.obj'
outPath = "/home/" + user + '/livestock/templates/fixedMesh.obj'
detail = open('detail.txt','r').readline()

# Run function
mesh = pm.load_mesh(meshPath)
mesh = fix_mesh(mesh, detail = detail)
pm.save_mesh(outPath, mesh)

# Annouce that template finished and create out file
print('Finished with template')
file_obj = open('out.txt','w')