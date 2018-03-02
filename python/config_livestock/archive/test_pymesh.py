import pymesh as pm
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, art3d
from matplotlib.collections import PolyCollection


def centerOfPoints(listOfPoints):
    x = [p[0] for p in listOfPoints]
    y = [p[1] for p in listOfPoints]
    z = [p[2] for p in listOfPoints]

    centroid = (sum(x) / len(listOfPoints), sum(y) / len(listOfPoints), sum(z) / len(listOfPoints))
    return centroid

def drainMeshPaths(mesh, cpus, fileAndPath):
    """ Estimates the trail of a drainage path on a mesh. Based on Benjamin
    Golders concept and Remy's VB code found here:
    http://www.grasshopper3d.com/forum/topics/drainage-direction-script """

    import threading
    import queue
    import pymesh as pm

    # Return list
    drainPoints = []
    startPoints = []

    # Construct center points
    mesh.enable_connectivity()
    mesh.add_attribute('face_centroid')
    mesh.add_attribute('face_index')
    startPts = mesh.get_attribute('face_centroid')
    cenZ = []
    faceIndex = mesh.get_attribute('face_index')

    i = 0
    while i < len(startPts):
        for j in range(0,len(faceIndex)):
            startPoints.append([faceIndex[j],np.array([startPts[i],startPts[i+1],startPts[i+2]])])
            cenZ.append(startPts[i+2])
            i += 3

    file_obj = open(fileAndPath,'w')

    # Task function
    def drainPath():

        while 1:
            # Particle list and current particle plane
            job = q.get()
            index = job[0]
            #print('index:',index)
            pt = job[1]
            #print('point:',pt)
            particles = []
            run = True

            while run:
                #print('index:',index)
                adjacents = mesh.get_face_adjacent_faces(int(index))
                particles.append(pt)

                z = 'Null'
                for ad in adjacents:
                    if z == 'Null':
                        z = cenZ[ad]
                        i = ad
                    elif z > cenZ[ad]:
                        z = cenZ[ad]
                        i = ad

                #print('pt2',pt[2],type(pt[2]))
                #print('z',z,type(z))

                if pt[2] <= z:
                    #print('Stop')
                    run = False

                else:
                    index = startPoints[i][0]
                    pt = startPoints[i][1]

            #print('particles:',particles)
            #print(len(particles))
            for pt in particles:
                file_obj.write(str(pt[0])+','+str(pt[1])+','+str(pt[2])+'\t')
            file_obj.write('\n')
            q.task_done()

    # Call task function
    q = queue.Queue()
    #file_obj = open(pathAndFile, 'w')
    for i in range(cpus):
        t = threading.Thread(target=drainPath)
        t.setDaemon(True)
        t.start()

    # Put jobs in queue
    #print('Num startspoints:',len(startPoints))
    for pts in startPoints:
        q.put(pts)

    # wait until all tasks in the queue have been processed
    q.join()

    # Make drain curves and endPoints
    #drainPaths = list(filter(None, drainPaths))
    #endPoints = [crv.PointAtEnd for crv in drainPaths]



#file = 'drainMesh.obj'
#mesh = pm.load_mesh(file)
#cpus = 1
#fileAndPath = "/mnt/c/Users/Christian/Dropbox/Arbejde/DTU BYG/Livestock/Kode - Livestock/01 Python/Tests/drainPoints.txt"
#a = drainMeshPaths(mesh, cpus, fileAndPath)

