__author__ = "Christian Kongsgaard"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Christian Kongsgaard"
__email__ = "ocni@dtu.dk"
__status__ = "Work in Progress"

#----------------------------------------------------------------------------------------------------------------------#
#Functions and Classes

def drainMeshPaths(meshPath,cpus):
    """ Estimates the trail of a drainage path on a mesh. """

    import threading
    import queue
    import pymesh as pm
    from numpy import array

    # Load mesh
    mesh = pm.load_mesh(meshPath)
    mesh.enable_connectivity()

    # Result list
    drainPoints = []

    # Construct center points
    mesh.add_attribute('face_centroid')
    mesh.add_attribute('face_index')
    startPts = mesh.get_attribute('face_centroid')
    centerZ = []
    faceIndex = mesh.get_attribute('face_index')

    # Construct startpoint list
    startPoints = []
    i = 0
    while i < len(startPts):
        for j in range(0,len(faceIndex)):
            startPoints.append([faceIndex[j],array([startPts[i],startPts[i+1],startPts[i+2]])])
            centerZ.append(startPts[i+2])
            i += 3

    # Task function
    def drainPath():

        while 1:
            # Get job from queue
            job = q.get()
            index = job[0]
            pt = job[1]

            particles = []
            run = True
            # print('index:',index)
            # print('point:',pt)

            while run:
                # Get adjacents faces
                adjacents = mesh.get_face_adjacent_faces(int(index))
                particles.append(pt)

                # Check if center points of adjacents faces have a lower Z-value
                z = None
                for ad in adjacents:
                    if z == None:
                        z = centerZ[ad]
                        i = ad
                    elif z > centerZ[ad]:
                        z = centerZ[ad]
                        i = ad

                if pt[2] <= z:
                    run = False

                else:
                    index = startPoints[i][0]
                    pt = startPoints[i][1]

            #print('particles:',particles)
            #print(len(particles))

            # End task
            drainPoints.append(particles)
            q.task_done()

    # Call task function
    q = queue.Queue()
    for i in range(cpus):
        t = threading.Thread(target=drainPath)
        t.setDaemon(True)
        t.start()

    # Put jobs in queue
    for pts in startPoints:
        q.put(pts)

    # Wait until all tasks in the queue have been processed
    q.join()

    # Open file, which the points should be written to
    file_obj = open('drainPoints.txt', 'w')

    # Write points to file
    for particles in drainPoints:
        for pt in particles:
            file_obj.write(str(pt[0]) + ',' + str(pt[1]) + ',' + str(pt[2]) + '\t')
        file_obj.write('\n')

    #Close out file and save mesh
    file_obj.close()
    pm.save_mesh('newDrainMesh.obj',mesh)

def drainPools(path):
    import pymesh as pm
    from numpy import array, allclose
    from numpy import sum as npsum
    from scipy.optimize import newton

    # Paths
    meshFile = path + '/drainMesh.obj'
    endPtsFile = path + '/EndPoints.txt'
    volPtsFile = path + '/VolumePoints.txt'

    # Initilize Mesh
    mesh = pm.load_mesh(meshFile)
    mesh.enable_connectivity()
    mesh.add_attribute('face_centroid')
    mesh.add_attribute('face_index')
    mesh.add_attribute('face_area')
    cenPts = mesh.get_attribute('face_centroid')
    faceIndex = mesh.get_attribute('face_index')
    faceArea = mesh.get_attribute('face_area')
    faceVert = mesh.faces
    vertices = mesh.vertices
    #print(mesh.get_attribute_names())

    # Construct face center list
    faceCen = []
    i = 0
    while i < len(cenPts):
        faceCen.append(array([float(cenPts[i]), float(cenPts[i + 1]), float(cenPts[i + 2])]))
        i += 3

    # Load points
    ptsLine = open(endPtsFile, 'r').readlines()
    endPts = []
    for l in ptsLine:
        l = l[:-1]
        l = l.split(',')
        endPts.append(array([float(l[0]), float(l[1]), float(l[2])]))
    #print(len(endPts))

    # Load volumes
    volLine = open(volPtsFile, 'r').readlines()
    vol = []
    for v in volLine:
        v = v[:-1]
        vol.append(float(v))

    pts = []
    vols = []
    fI = []

    for i,pt in enumerate(endPts):

        # Check if point is in list:
        if i == 0:
            pts.append(pt)
            vols.append(vol[i])

            # Find equivalent face center of points
            for index, cen in enumerate(faceCen):
                if allclose(cen,pt):
                    fI.append(index)
                    break

        else:
            found = False
            j = 0
            while j < len(pts):
                # If it is in list: add volume
                if allclose(pts[j], pt):
                    vols[j] += vol[i]
                    j = len(pts)
                    found = True
                j += 1

            # Else: put point and volume in list
            if not found:
                pts.append(pt)
                vols.append(vol[i])

                # Find equivalent face center of points
                for index, cen in enumerate(faceCen):
                    if allclose(cen,pt):
                        fI.append(index)
                        break

    # Pool function
    def pool(faceIndex,point,volume):
        found = False

        # Compute first z-value
        A = faceArea[faceIndex]
        h = volume/A
        Z = point[2]+h

        # Initialize face index, z-values and areas
        adjFace = [faceIndex, ]
        faceZ = [point[2],]
        faceA = [A,]

        # Find adjacent faces
        for faceIn in adjFace:

            for af in mesh.get_face_adjacent_faces(faceIn):

                # Get Z-value of face-centroid
                fc = faceCen[af][2]

                # Append them to list if their centroid is lower than the computed Z-value and are not already in list
                if fc < Z:
                    if af not in adjFace:

                        # If current face holds a volume add that volume to the current volume
                        if af in fI:
                            #print('found in fI')
                            queueIndex = fI.index(af)

                            if queueIndex in notDoneList:
                                #print('found in notDoneList')
                                volume += vols[queueIndex]
                                notDoneList.remove(queueIndex)
                                doneList.append(queueIndex)

                            elif queueIndex in doneList:
                                #print('found in doneList')
                                vols[queueIndex] += volume
                                notDoneList.append(queueIndex)
                                doneList.remove(queueIndex)
                                return

                            else:
                                pass

                        # Append Z-value, area and face-index
                        faceZ.append(fc)
                        faceA.append(faceArea[af])
                        adjFace.append(int(af))

                        # Convert to numpy array
                        faZ = array(faceZ)
                        faA = array(faceA)

                        # Compute new z-value
                        Z = (npsum(faZ*faA)+volume)/npsum(faA)

        # Volume function to solve
        def findHeight(z):

            # Boundary Box
            maxmin = mesh.bbox
            bVert = []
            bFace = []
            bVox = []
            x1, y1, z1 = maxmin[0]
            x2, y2, z2 = maxmin[1]
            z2 = z

            # Add vertices
            bVert.append(array([x1, y1, z1])) #0
            bVert.append(array([x1, y2, z1])) #1
            bVert.append(array([x1, y2, z2])) #2
            bVert.append(array([x1, y1, z2])) #3

            bVert.append(array([x2, y2, z2])) #4
            bVert.append(array([x2, y2, z1])) #5
            bVert.append(array([x2, y1, z1])) #6
            bVert.append(array([x2, y1, z2])) #7

            # Add faces
            bFace.append([0, 1, 3]) # side 1
            bFace.append([1, 2, 3]) # side 1
            bFace.append([0, 3, 7]) # side 2
            bFace.append([0, 6, 7]) # side 2
            bFace.append([7, 6, 5]) # side 3
            bFace.append([5, 7, 4]) # side 3
            bFace.append([4, 5, 1]) # side 4
            bFace.append([4, 2, 1]) # side 4
            bFace.append([0, 1, 6]) # side 5
            bFace.append([1, 5, 6]) # side 5
            bFace.append([3, 7, 2]) # side 6
            bFace.append([2, 7, 4]) # side 6

            # Add voxels
            bVox.append([0, 2, 3, 7])
            bVox.append([0, 1, 2, 7])
            bVox.append([0, 1, 6, 7])
            bVox.append([2, 4, 5, 7])
            bVox.append([1, 2, 5, 6])
            bVox.append([2, 4, 6, 7])

            # Create boundary mesh
            bVert = array(bVert)
            bFace = array(bFace)
            bVox = array(bVox)
            bMesh = pm.form_mesh(bVert,bFace,bVox)

            # Make intersection
            newMesh = pm.boolean(mesh,bMesh,'intersection')

            # Get bottom part of mesh
            newSource = newMesh.get_attribute('source')
            newFace = newMesh.faces
            bottomFaces = []
            for i,s in enumerate(newSource):
                if int(s) == 1:
                    bottomFaces.append(newFace[i])

            # Prepare to create volume mesh
            newMeshVert = newMesh.vertices
            volVert = []
            volFace = []
            volVox = []

            # Get bottom part of mesh
            for f in bottomFaces:
                iVer = len(volVert)

                oldVerts = []
                newVerts = []
                for v in f:
                    oldVerts.append(newMeshVert[v])
                    newV = array([newMeshVert[v][0],newMeshVert[v][1],z])
                    newVerts.append(newV)

                # Append vertices
                volVert += oldVerts
                volVert += newVerts

                # Append faces
                volFace.append([iVer, iVer+1, iVer+2])
                volFace.append([iVer+3, iVer+4, iVer+5])

                # Append voxels
                volVox.append([iVer, iVer+1, iVer+2, iVer+3])
                volVox.append([iVer+1, iVer+3, iVer+4, iVer+5])
                volVox.append([iVer+1, iVer+2, iVer+3, iVer+5])

            # Create volume mesh
            volVert = array(volVert)
            volFace = array(volFace)
            volVox = array(volVox)
            volMesh = pm.form_mesh(volVert, volFace, volVox)

            # Compute volume
            volMesh.add_attribute('voxel_volume')
            volVol = volMesh.get_attribute('voxel_volume')
            volVol = sum(list((map(abs, volVol))))

            #print('volume',volume)
            #print('volVol1',volVol)

            return volume - volVol

        # Get final height
        z = newton(findHeight,Z)

        # Create final mesh
        def finalMesh(z):

            # Boundary Box
            maxmin = mesh.bbox
            bVert = []
            bFace = []
            bVox = []
            x1, y1, z1 = maxmin[0]
            x2, y2, z2 = maxmin[1]
            z2 = z

            # Add vertices
            bVert.append(array([x1, y1, z1])) #0
            bVert.append(array([x1, y2, z1])) #1
            bVert.append(array([x1, y2, z2])) #2
            bVert.append(array([x1, y1, z2])) #3

            bVert.append(array([x2, y2, z2])) #4
            bVert.append(array([x2, y2, z1])) #5
            bVert.append(array([x2, y1, z1])) #6
            bVert.append(array([x2, y1, z2])) #7

            # Add faces
            bFace.append([0, 1, 3]) # side 1
            bFace.append([1, 2, 3]) # side 1
            bFace.append([0, 3, 7]) # side 2
            bFace.append([0, 6, 7]) # side 2
            bFace.append([7, 6, 5]) # side 3
            bFace.append([5, 7, 4]) # side 3
            bFace.append([4, 5, 1]) # side 4
            bFace.append([4, 2, 1]) # side 4
            bFace.append([0, 1, 6]) # side 5
            bFace.append([1, 5, 6]) # side 5
            bFace.append([3, 7, 2]) # side 6
            bFace.append([2, 7, 4]) # side 6

            # Add voxels
            bVox.append([0, 2, 3, 7])
            bVox.append([0, 1, 2, 7])
            bVox.append([0, 1, 6, 7])
            bVox.append([2, 4, 5, 7])
            bVox.append([1, 2, 5, 6])
            bVox.append([2, 4, 6, 7])

            # Create boundary mesh
            bVert = array(bVert)
            bFace = array(bFace)
            bVox = array(bVox)
            bMesh = pm.form_mesh(bVert,bFace,bVox)

            # Make intersection
            newMesh = pm.boolean(mesh,bMesh,'intersection')

            # Get bottom part of mesh
            newSource = newMesh.get_attribute('source')
            newFace = newMesh.faces
            bottomFaces = []
            for i,s in enumerate(newSource):
                if int(s) == 1:
                    bottomFaces.append(newFace[i])

            # Prepare to create volume mesh
            newMeshVert = newMesh.vertices
            volVert = []
            volFace = []
            volVox = []

            for f in bottomFaces:
                iVer = len(volVert)

                oldVerts = []
                newVerts = []
                for v in f:
                    oldVerts.append(newMeshVert[v])
                    newV = array([newMeshVert[v][0],newMeshVert[v][1],z])
                    newVerts.append(newV)

                # Append vertices
                volVert += oldVerts
                volVert += newVerts

                # Append faces
                volFace.append([iVer, iVer+1, iVer+2])
                volFace.append([iVer+3, iVer+4, iVer+5])

                # Append voxels
                volVox.append([iVer, iVer+1, iVer+2, iVer+3])
                volVox.append([iVer+1, iVer+3, iVer+4, iVer+5])
                volVox.append([iVer+1, iVer+2, iVer+3, iVer+5])

            # Create volume mesh
            volVert = array(volVert)
            volFace = array(volFace)
            volVox = array(volVox)
            volMesh = pm.form_mesh(volVert, volFace, volVox)

            volMesh.add_attribute('voxel_volume')
            volVol = volMesh.get_attribute('voxel_volume')
            volVol = sum(list(map(abs, volVol)))

            # Clean up mesh
            volMesh, info = pm.remove_isolated_vertices(volMesh)
            #print('num vertex removed', info["num_vertex_removed"])
            volMesh, info = pm.remove_duplicated_faces(volMesh)


            return volMesh, volVol

        # Save final mesh
        finalMesh, finalVol = finalMesh(z)
        meshName = "poolMesh_" + str(faceIndex) + ".obj"
        pm.save_mesh(meshName, finalMesh)

        print(' ')
        print('volume',"{0:.3f}".format(volume))
        print('computed volume',"{0:.3f}".format(finalVol))
        print('closed?',finalMesh.is_closed())
        print(' ')

        return meshName

    # Initialize pool-loop
    Z = []
    i = 0
    doneList = []
    notDoneList = list(range(0,len(pts)))
    loopLength = len(notDoneList)
    meshNames = []

    # Use pool function on each set of points
    while i < loopLength:
        I = notDoneList.pop(i)
        names = pool(fI[I],pts[I],vols[I])

        # Put meshNames in name list
        if names:
            if not names in meshNames:
                meshNames.append(names)
            else:
                pass

        doneList.append(i)
        loopLength = len(notDoneList)

    file_obj = open("InData.txt",'r')
    file = file_obj.readlines()

    mNames = ''
    for n in meshNames:
        mNames += ',' + n

    file[6] = 'meshNames.txt,' + mNames
    print('out', file[6])
    file_obj.close()




