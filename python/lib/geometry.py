__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# ---------------------------------------------------------------------------- #
# Imports

# Module imports
import os
import json

# Livestock imports

# Grasshopper imports
import Rhino.Geometry as rg
import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino as rc
from System.Threading.Tasks.Parallel import ForEach
from Rhino.Geometry.Brep import JoinBreps

# ---------------------------------------------------------------------------- #
# Livestock Grasshopper Geometry Classes and Functions


def bake(geo, doc):
    """
    Bakes geometry from Grasshopper

    :param geo: Geometry to bake
    :param doc: Grasshopper doc
    :return: Rhino ID
    """

    # we create or use some geometry
    geo_id = geo

    # we obtain the reference in the Rhino doc
    sc.doc = doc
    doc_object = rs.coercerhinoobject(geo_id)

    attributes = doc_object.Attributes
    geometry = doc_object.Geometry

    # we change the scriptcontext
    sc.doc = rc.RhinoDoc.ActiveDoc

    # we add both the geometry and the attributes to the Rhino doc
    rhino_line = sc.doc.Objects.Add(geometry, attributes)

    # we put back the original Grasshopper document as default
    sc.doc = doc
    return rhino_line


def export(ids, file_path, file_name, file_type, doc):
    """
    Exports Rhino geometry to a file.

    :param ids: Geometry ID
    :param file_path: File directory
    :param file_name: File name
    :param file_type: File extension
    :param doc: Grasshopper document
    :return: True on succes.
    """

    sel_ids = ""
    for i in range(len(ids)):
        sel_ids += "_SelId %s " % ids[i]

    file_name_and_type = file_name + file_type
    final_path = chr(34) + file_path + '\\' + file_name_and_type + chr(34)

    command_string = "_-Export " + sel_ids + "_Enter " + final_path + " _Enter _Enter _Enter"
    echo = False
    done = rs.Command(command_string, echo)

    sc.doc = rc.RhinoDoc.ActiveDoc
    rs.SelectObject(ids)
    rs.Command("_Delete", True)
    sc.doc = doc

    if done:
        return True
    else:
        return False


def bake_export_delete(geo, file_path, file_name, file_type, doc):
    """
    Bakes and exports Grasshopper geometry.

    :param geo: Grasshopper geometry.
    :param file_path: File directory
    :param file_name: File name
    :param file_type: File extension.
    :param doc: Grasshopper doument
    """

    g = bake(geo, doc)
    export([g, ], file_path, file_name, file_type, doc)


def import_obj(path):
    """
    Reads a .obj file and converts it into a Rhino Mesh.

    :param path: path including file name and file extension (.obj)
    :return: Rhino Mesh
    """

    # Initialize mesh
    mesh = rg.Mesh()

    # Open File
    file_ = open(path)
    lines = file_.readlines()
    file_.close()

    # Check if file is generated with PyMesh
    if lines[0].startswith('# Generated with PyMesh'):
        print('Generated with PyMesh')
        for line in lines:
            if line.find("v") == 0:
                mesh.Vertices.Add(rg.Point3d(float((line.split(' '))[1]),
                                             float((line.split(' '))[2]),
                                             float((line.split(' '))[3])
                                             )
                                  )

            if line.find("f") == 0:
                line = line[:-2]
                if len(line.split(' ')) == 4:
                    mesh.Faces.AddFace(rg.MeshFace(int(line.split(' ')[1]) - 1,
                                                   int(line.split(' ')[2]) - 1,
                                                   int(line.split(' ')[3]) - 1)
                                       )

                elif len(line.split(' ')) == 5:
                    mesh.Faces.AddFace(rg.MeshFace(int(line.split(' ')[1]) - 1,
                                                   int(line.split(' ')[2]) - 1,
                                                   int(line.split(' ')[3]) - 1,
                                                   int(line.split(' ')[4]) - 1)
                                       )
    else:
        for line in lines:
            if line.find("v") == 0 and line.find("n") == -1 and line.find("t") == -1:
                mesh.Vertices.Add(rg.Point3d(float((line.split(' '))[1]),
                                             float((line.split(' '))[2]),
                                             float((line.split(' '))[3])
                                             )
                                  )

            if line.find("f") == 0:
                if len(line.split(' ')) == 4:
                    mesh.Faces.AddFace(rg.MeshFace(int(line.split(' ')[1].split('/')[0])-1,
                                                   int(line.split(' ')[2].split('/')[0])-1,
                                                   int(line.split(' ')[3].split('/')[0])-1)
                                       )

    mesh.Normals.ComputeNormals()
    mesh.Compact()
    return mesh


def load_points(point_file):
    """
    Loads a text file containing points

    :param point_file: Path to the points file.
    :type point_file: str
    :return: List of Rhino 3D points
    :rtype: list
    """

    points = []
    with open(point_file) as file:
        raw_pts = json.load(file)

    for line in raw_pts:
        points.append([rg.Point3d(float(pt[0]), float(pt[1]), float(pt[2]))
                       for pt in line])

    return points


def make_curves_from_points(points):
    """Converts a list of points to a 5-degree polynomial curve."""

    curves = []
    end_points = []

    for pts in points:
        if len(pts) == 1:
            end_points.append(pts[0])
        else:
            crv = rg.Curve.CreateControlPointCurve(pts, 5)
            if crv:
                curves.append(crv)
                end_points.append(pts[-1])

    return curves, end_points


def parallel_make_context_mesh(brep, parallel=False):
    #"""Ladybug - mesh breps parallel"""

    def make_mesh_from_srf(i):
        try:
            mesh[i] = rc.Mesh.CreateFromBrep(brep[i], mesh_param)
            brep[i].Dispose()
        except:
            print('Error in converting Brep to Mesh...')
            pass

    # prepare bulk list for each surface
    mesh = [None] * len(brep)

    # set-up mesh parameters for each surface based on surface size
    mesh_param = rc.MeshingParameters.Default  # Coarse
    rc.MeshingParameters.GridMaxCount.__set__(mesh_param, 1)
    rc.MeshingParameters.SimplePlanes.__set__(mesh_param, True)
    rc.MeshingParameters.GridAmplification.__set__(mesh_param, 1.5)

    # Call the mesh function
    if parallel:
        ForEach(xrange(len(brep)), make_mesh_from_srf)
    else:
        for i in range(len(mesh)):
            make_mesh_from_srf(i)

    return mesh


def clean_and_coerce_list(brep_list):
    #""" Ladybug - This definition cleans the list and adds them to RhinoCommon"""

    outputMesh = []
    outputBrep = []

    for id in brep_list:
        if rs.IsMesh(id):
            geo = rs.coercemesh(id)
            if geo is not None:
                outputMesh.append(geo)
                try:
                    rs.DeleteObject(id)
                except:
                    pass

        elif rs.IsBrep(id):
            geo = rs.coercebrep(id)
            if geo is not None:
                outputBrep.append(geo)
                try:
                    rs.DeleteObject(id)
                except:
                    pass

            else:
                # the idea was to remove the problematice surfaces
                # not all the geometry which is not possible since
                # badGeometries won't pass rs.IsBrep()
                tempBrep = []
                surfaces = rs.ExplodePolysurfaces(id)

                for surface in surfaces:
                    geo = rs.coercesurface(surface)
                    if geo is not None:
                        tempBrep.append(geo)
                        try:
                            rs.DeleteObject(surface)
                        except:
                            pass

                geo = JoinBreps(tempBrep, 0.01)

                for Brep in tempBrep:
                    Brep.Dispose()
                    try:
                        rs.DeleteObject(id)
                    except:
                        pass
                outputBrep.append(geo)

    return outputMesh, outputBrep


def join_mesh(mesh_list):
    #"""Ladybug - joinMesh"""

    joined_mesh = rg.Mesh()
    for m in mesh_list: joined_mesh.Append(m)

    return joined_mesh


def rayTrace(startPts, startVectors, context, numOfBounce, lastBounceLen):
    #"""Ladybug - RayTrace"""

    # A failed attampt to use mesh instead of brep so the component could work with trimmed surfaces
    if len(context) != 0:
        ## clean the geometry and bring them to rhinoCommon separated as mesh and Brep
        contextMesh, contextBrep = clean_and_coerce_list(context)
        ## mesh Brep
        contextMeshedBrep = parallel_make_context_mesh(contextBrep)

        ## Flatten the list of surfaces
        contextMeshedBrep = flatten_list(contextMeshedBrep)
        contextSrfs = contextMesh + contextMeshedBrep
        joinedContext = join_mesh(contextSrfs)

    # Get rid of trimmed parts
    cleanBrep = rg.Brep.CreateFromMesh(joinedContext, False)

    rays = []
    for testPt in startPts:
        for vector in startVectors:
            vector.Unitize()
            ray = rg.Ray3d(testPt, vector)
            if numOfBounce > 0:
                intPts = rc.Intersect.Intersection.RayShoot(ray, [cleanBrep], numOfBounce)
                # print intPts
                if intPts:
                    ptList = [testPt]
                    ptList.extend(intPts)
                    ray = rc.Polyline(ptList).ToNurbsCurve()

                    try:
                        # create last ray
                        # calculate plane at intersection
                        intNormal = cleanBrep.ClosestPoint(intPts[-1], sc.doc.ModelAbsoluteTolerance)[5]

                        lastVector = rc.Vector3d(ptList[-2] - ptList[-1])
                        lastVector.Unitize()

                        crossProductNormal = rc.Vector3d.CrossProduct(intNormal, lastVector)

                        plane = rc.Plane(intPts[-1], intNormal, crossProductNormal)

                        mirrorT = rc.Transform.Mirror(intPts[-1], plane.Normal)

                        lastRay = rc.Line(intPts[-1], lastBounceLen * lastVector).ToNurbsCurve()
                        lastRay.Transform(mirrorT)

                        ray = rc.Curve.JoinCurves([ray, lastRay])[0]
                    except:
                        pass

                    rays.append(ray)
                else:
                    # no bounce so let's just create a line form the point
                    firstRay = rc.Line(testPt, lastBounceLen * vector).ToNurbsCurve()
                    rays.append(firstRay)

    if len(rays) == 0:
        print("No reflection!")
        return False

    return rays


def ray_shoot(start_pt, vector, context, num_of_bounce=1):
    #"""Build on: Ladybug - RayTrace"""

    ray = rg.Ray3d(start_pt, vector)
    print('ray', ray)

    if num_of_bounce > 0:
        int_pt = rg.RayShoot(ray, [context], num_of_bounce)
        print('intPt:', int_pt)

        if int_pt:
            print('Intersection!')
            return True
        else:
            print('No intersection!')
            return False

    else:
        print("No reflection!")
        return False


def load_mesh_data(path):
    """
    Load additional data for a mesh.

    :param path: Path for mesh file.
    :return: Data from the mesh
    """

    path = path.split('.')[0] + '_Data.txt'

    # Check if file exists
    exists = os.path.isfile(path)
    if exists:
        data = []
        file_obj = open(path, 'r')
        lines = file_obj.readlines()
        for l in lines:
            data.append(l[:-1])

        print('Mesh loaded with data')
        return data

    else:
        print("Mesh don't have any associated data")


def get_mesh_faces(mesh):
    """
    Takes a mesh and convert its faces into individual meshes.

    :param mesh: mesh
    :return: list of "face" meshes
    """

    mesh_faces = rs.MeshFaces(mesh)
    faces = []

    for i in range(0, len(mesh_faces), 4):
        vertices = [mesh_faces[i], mesh_faces[i + 1], mesh_faces[i + 2], mesh_faces[i + 3]]
        added_mesh = rs.AddMesh(vertices, [[0, 1, 2, 3]])
        faces.append(added_mesh)

    return faces

