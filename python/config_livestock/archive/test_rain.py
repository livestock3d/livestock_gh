
# Drain Function
def drainMeshPaths(mesh, tolerance):
    """ Estimates the trail of a drainage path on a mesh. Based on Benjamin
    Golders concept and Remy's VB code found here:
    http://www.grasshopper3d.com/forum/topics/drainage-direction-script """

    # Import
    import clr
    clr.AddReference("RhinoCommon")
    import Rhino as rc
    import System.Threading.Tasks as tasks

    # Tolerance Check
    if Tolerance == 0:
        print('Tolerance can not be 0')
        exit()

    # Return list
    drainPaths = []
    startPoints = []
    i = 0
    while i < mesh.Faces.Count:
        cen = mesh.Faces.GetFaceCenter(i)
        startPoints.append(cen)
        i += 1

    # Task function
    def drainPath(pt):

        # Particle list and current particle plane
        particles = []
        paPl = rc.Geometry.Plane(pt, rc.Geometry.Vector3d.ZAxis)
        run = True

        while run:

            # Get the point on the mesh closest to the particle
            meshPt = mesh.ClosestMeshPoint(paPl.Origin, 0.0)
            paPl = rc.Geometry.Plane(meshPt.Point, mesh.NormalAt(meshPt))

            # Check that first step has been taken and that current step is down slope
            if len(particles) != 0 and paPl.Origin.Z > particles[-1].Z:
                run = False

            else:
                # Add particle to list
                particles.append(paPl.Origin)

                # Move particle down slope
                an = rc.Geometry.Vector3d.VectorAngle(paPl.XAxis, -rc.Geometry.Vector3d.ZAxis, paPl)
                paPl.Rotate(an, paPl.ZAxis)
                paPl.Translate(paPl.XAxis * tolerance)

            lines = mesh.GetNakedEdges()
            for line in lines:
                lineParam = line.ClosestParameter(paPl.Origin)
                linePoint = line.PointAt(lineParam)
                pointDistance = linePoint.DistanceTo(paPl.Origin)
                if pointDistance <= tolerance:
                    run = False
                    particles.append(linePoint)

        # Make drain curve
        if len(particles) > 1:
            crv = rc.Geometry.Curve.CreateControlPointCurve(particles)
            drainPaths.append(crv)

    # Call task function
    tasks.Parallel.ForEach(startPoints, drainPath)

    return drainPaths

"""
# Run Component
if Toggle and Mesh:
    # Make mesh centerpoints as startpoint


    # Make drain curves
    DrainCurves = makeDrainMeshPaths(Mesh, startPoints, Tolerance)
    DrainCurves = list(filter(None, DrainCurves))
    EndPoints = [crv.PointAtEnd for crv in DrainCurves]
"""


import sys
sys.path.insert(0, r'C:\Users\Christian\Dropbox\Arbejde\DTU BYG\Livestock\Kode - Livestock\01 Python\Classes')
import LivestockGH as ls
import clr
clr.AddReference("RhinoCommon")
import Rhino as rc
import rhinoscriptsyntax as rs

mesh = rs.Mesh()

mesh.Vertices.Add(0.0, 0.0, 1.0)  # 0
mesh.Vertices.Add(1.0, 0.0, 1.0)  # 1
mesh.Vertices.Add(0.0, 1.0, 1.0)  # 2
mesh.Vertices.Add(2.0, 2.0, 1.0)  # 3
mesh.Faces.AddFace(0, 1, 2, 3)

mesh.Normals.ComputeNormals()
mesh.Compact()

"""
pt = rc.Geometry.Point3f()
m = rc.Geometry.Mesh()
print(pt.Z)

obj = 'C:\\Users\\Christian\\Desktop\\drainMesh.obj'
ls.OBJ(obj)

"""