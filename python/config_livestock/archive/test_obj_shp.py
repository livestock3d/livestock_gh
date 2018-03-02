import shapefile as sf
path = r'C:\Users\Christian\Desktop\test_cmf\test_02\mesh.obj'
outpath = r'C:\Users\Christian\Desktop\test.shp'


def obj_to_panda(obj_file):
    """Convert a obj file into a panda data frame"""

    # Initialization
    vertices = []
    normals = []
    faces = []
    file = open(obj_file, 'r')
    lines = file.readlines()
    file.close()

    # Find data
    for line in lines:
        if line.startswith('v '):
            data = line.split(' ')
            vertices.append([float(data[1]), float(data[2]), float(data[3][:-1])])

        elif line.startswith('vn'):
            data = line.split(' ')
            normals.append([float(data[1]), float(data[2]), float(data[3][:-1])])

        elif line.startswith('f'):
            data = line[:-1].split(' ')
            d = []
            for elem in data:
                d.append(elem.split('/'))
            faces.append(d[1:])

        else:
            pass

    return vertices, normals, faces


def obj_to_shp(obj_file, shp_file):
    """Convert a obj file into a shape file"""

    mesh = obj_to_panda(obj_file)

    writer = sf.Writer(shapeType=15)
    writer.fields('name', 'C')

    return True

obj_to_shp(path, outpath)
