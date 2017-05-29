__author__ = "Christian Kongsgaard"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Christian Kongsgaard"
__email__ = "ocni@dtu.dk"
__status__ = "Work in Progress"

#----------------------------------------------------------------------------------------------------------------------#
#Functions and Classes

componentFile = r'C:\livestock\python\ComponetList.txt'

read = open(componentFile, 'r')
lines = read.readlines()
ComponentData = []
for l in lines:
    l = l.split('\t')
    ComponentData.append(l)

def tree_to_list(input, retrieve_base = lambda x: x[0]):
    """Returns a list representation of a Grasshopper DataTree"""
    def extend_at(path, index, simple_input, rest_list):
        target = path[index]
        if len(rest_list) <= target: rest_list.extend([None]*(target-len(rest_list)+1))
        if index == path.Length - 1:
            rest_list[target] = list(simple_input)
        else:
            if rest_list[target] is None: rest_list[target] = []
            extend_at(path, index+1, simple_input, rest_list[target])
    all = []
    for i in range(input.BranchCount):
        path = input.Path(i)
        extend_at(path, 0, input.Branch(path), all)
    return retrieve_base(all)

def list_to_tree(input, none_and_holes=True, source=[0]):
    """Transforms nestings of lists or tuples to a Grasshopper DataTree"""
    from Grasshopper import DataTree as Tree
    from Grasshopper.Kernel.Data import GH_Path as Path
    from System import Array
    def proc(input,tree,track):
        path = Path(Array[int](track))
        if len(input) == 0 and none_and_holes: tree.EnsurePath(path); return
        for i,item in enumerate(input):
            if hasattr(item, '__iter__'): #if list or tuple
                track.append(i); proc(item,tree,track); track.pop()
            else:
                if none_and_holes: tree.Insert(item,path,i)
                elif item is not None: tree.Add(item,path)
    if input is not None: t=Tree[object]();proc(input,t,source[:]);return t

class PassClass:
    def __init__(self, pyClass, name):
        self.c = pyClass
        self.n = name

    def __repr__(self):
        return "Livestock." + self.n

def bake(geo, doc):
    import scriptcontext as sc
    import rhinoscriptsyntax as rs
    import Rhino as rc

    # we create or use some geometry
    geo_id = geo
    #print(geo_id)
    # (we could do all operations here...

    # we obtain the reference in the Rhino doc
    sc.doc = doc
    #print(sc.doc)
    doc_object = rs.coercerhinoobject(geo_id)
    #print(type(doc_object))

    attributes = doc_object.Attributes
    #print('the type of attributes is: ' + str(type(attributes)))
    geometry = doc_object.Geometry
    #print('the type of geometry is: ' + str(type(geometry)))

    # we change the scriptcontext
    sc.doc = rc.RhinoDoc.ActiveDoc

    # we add both the geometry and the attributes to the Rhino doc
    rhino_line = sc.doc.Objects.Add(geometry, attributes)
    #print('the Rhino doc ID is: ' + str(rhino_line))

    # we put back the original Grasshopper document as default
    sc.doc = doc
    return rhino_line

def export(ids, filePath, fileName, fileType,doc):
    import scriptcontext as sc
    import rhinoscriptsyntax as rs
    import Rhino as rc

    selIds = ""
    for i in range(len(ids)):
        selIds += "_SelId %s " % ids[i]

    fileNameAndType = fileName + fileType
    finalPath = chr(34) + filePath + '\\' + fileNameAndType + chr(34)

    commandString = "_-Export " + selIds + "_Enter " + finalPath + " _Enter _Enter _Enter"
    echo = False
    done = rs.Command(commandString, echo)

    sc.doc = rc.RhinoDoc.ActiveDoc
    rs.SelectObject(ids)
    rs.Command("_Delete", True)
    sc.doc = doc

    if done:
        return True
    else:
        return False

def bakeExportDelete(geo, filePath, fileName, fileType,doc):
    g = bake(geo,doc)
    export([g, ], filePath, fileName, fileType,doc)

def importObj(path):
    """
    Reads a .obj file and converts it into a Rhino Mesh
    :param path: path including file name and file extension (.obj)
    :return: Rhino Mesh
    """

    import Rhino.Geometry as rg

    # Initilize mesh
    mesh = rg.Mesh()

    # Open File
    file = open(path)
    lines = file.readlines()

    # Check if file is generated with PyMesh
    if lines[0].startswith('# Generated with PyMesh'):
        print('PyMesh')
        for line in lines:
            if line.find("v") == 0:
                mesh.Vertices.Add(rg.Point3d(float((line.split(' '))[1]), float((line.split(' '))[2]), float((line.split(' '))[3])))

            if line.find("f") == 0:
                line = line[:-2]
                if len(line.split(' ')) == 4:
                    mesh.Faces.AddFace(rg.MeshFace(int(line.split(' ')[1]) - 1, int(line.split(' ')[2]) - 1, int(line.split(' ')[3]) - 1))

                elif len(line.split(' ')) == 5:
                    mesh.Faces.AddFace(rg.MeshFace(int(line.split(' ')[1]) - 1, int(line.split(' ')[2]) - 1, int(line.split(' ')[3]) - 1, int(line.split(' ')[4]) - 1))
    else:
        for line in lines:
            if line.find("v")==0 and line.find("n")==-1 and line.find("t")==-1:
                mesh.Vertices.Add(rg.Point3d(float((line.split(' '))[1]),float((line.split(' '))[2]),float((line.split(' '))[3])))

            if line.find("f")==0:
                if len(line.split(' ')) == 4:
                    mesh.Faces.AddFace(rg.MeshFace(int(line.split(' ')[1].split('/')[0])-1,int(line.split(' ')[2].split('/')[0])-1,int(line.split(' ')[3].split('/')[0])-1))

                #if line.split(' ').Count==5:
                    #mesh.Faces.AddFace(rg.MeshFace(int(line.split(' ')[1].split('/')[0])-1,int(line.split(' ')[2].split('/')[0])-1,int(line.split(' ')[3].split('/')[0])-1,int(line.split(' ')[4].split('/')[0])-1))

    mesh.Normals.ComputeNormals()
    mesh.Compact()
    file.close()
    return mesh

def writeFile(text, path, name, filetype='txt'):
    import os

    # Make file path name with extension
    filePath = os.path.join(path, name + "." + str(filetype))

    # Open file
    fileWrite = open(filePath, "w")

    # Write text data to file
    # If integer
    if isinstance(text,int):
        fileWrite.write(str(text))

    else:
        i = 0
        while i < len(text):
            if i == len(text) - 1:
                fileWrite.write(str(text[i]))
            else:
                fileWrite.write(str(text[i]) + "\n")
            i += 1

    # Close file
    fileWrite.close()

def binarySearch(alist, item):
    first = 0
    last = len(alist)-1
    found = False

    while first<=last and not found:
        midpoint = (first + last)//2
        if alist[midpoint] == item:
            found = True
        else:
            if item < alist[midpoint]:
                last = midpoint-1
            else:
                first = midpoint+1

    return found

def loadPoints(pathAndFile):
    from Rhino.Geometry import Point3d
    from os import remove

    points = []
    file_obj = open(pathAndFile,'r')
    for l in file_obj.readlines():
        line = l.split("\t")[:-1]
        pts = []
        for p in line:
            pt = p.split(',')
            pts.append(Point3d(float(pt[0]),float(pt[1]),float(pt[2])))
        points.append(pts)

    file_obj.close()
    remove(pathAndFile)
    return points

def makeCurvesFromPoints(points):
    from Rhino import Geometry as rc

    curves = []
    for pts in points:
        crv = rc.Curve.CreateControlPointCurve(pts,5)
        if crv:
            curves.append(crv)

    return curves

def lineIntersection(p1, p2, p3, p4):
    """
    Computes the intersection between two lines given 4 points on those lines.
    :param p1: Numpy array. First point on line 1
    :param p2: Numpy array. Second point on line 1
    :param p3: Numpy array. First point on line 2
    :param p4: Numpy array. Second point on line 2
    :return: Numpy array. Intersection point
    """

    # Imports
    from numpy import cross
    from numpy.linalg import norm

    # Direction vectors
    v1 = (p2 - p1)
    v2 = (p4 - p3)

    # Cross-products and vector norm
    cv12 = cross(v1, v2)
    cpv = cross((p1 - p3), v2)
    t = norm(cpv) / norm(cv12)

    return p1 + t * v1
