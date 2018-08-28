"""
from openmesh import *

mesh = PolyMesh()

file = r'C:\Users\Christian\Desktop\drainMesh.obj'
read_mesh(mesh,file)

#print(len(mesh.faces()))
"""


def centerOfPoints(listOfPoints):
    x = [p[0] for p in listOfPoints]
    y = [p[1] for p in listOfPoints]
    z = [p[2] for p in listOfPoints]

    centroid = (sum(x) / len(listOfPoints), sum(y) / len(listOfPoints), sum(z) / len(listOfPoints))
    return centroid

def drainMeshPaths(mesh, tolerance, cpus):
    """ Estimates the trail of a drainage path on a mesh. Based on Benjamin
    Golders concept and Remy's VB code found here:
    http://www.grasshopper3d.com/forum/topics/drainage-direction-script """

    import subprocess
    import threading
    import Queue
    import openmesh as om

    # Return list
    drainPaths = []
    startPoints = []

    # Construct center points
    for fh in mesh.faces():
        ver = []
        for v in mesh.fv(fh):
            x = mesh.point(v)[0]
            y = mesh.point(v)[1]
            z = mesh.point(v)[2]
            ver.append([x, y, z])
        cen = centerOfPoints(ver)
        startPoints.append(cen)


    # Task function
    def drainPath():

        # Particle list and current particle plane
        pt = q.get()
        particles = []
        paPl = om.Plane3d(om.Vec3f(0,0,1),pt)

        #paPl = rc.Geometry.Plane(pt, rc.Geometry.Vector3d.ZAxis)
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
        q.task_done()

    # Call task function
    q = Queue.Queue()
    for i in range(cpus):
        t = threading.Thread(target=drainPath)
        t.setDaemon(True)
        t.start()

    # Put jobs in queue
    q.put(startPoints)

    # wait until all tasks in the queue have been processed
    q.join()

    # Make drain curves and endPoints
    drainPaths = list(filter(None, drainPaths))
    endPoints = [crv.PointAtEnd for crv in drainPaths]

    return drainPaths, endPoints

def makeDrainMeshPaths(path,tolerance,cpus):
    import openmesh as om

    mesh = om.PolyMesh()
    om.read_mesh(mesh, path)

    drainCurves = drainMeshPaths(mesh,tolerance,cpus)
    outfile = r'C:\Users\Christian\Desktop\drainCurves.obj'
    result = om.write_mesh(drainCurves,outfile)

    if result:
        return True
    else:
        return False

file = r'C:\Users\Christian\Desktop\drainMesh.obj'
a = makeDrainMeshPaths(file, 0.1,2)
