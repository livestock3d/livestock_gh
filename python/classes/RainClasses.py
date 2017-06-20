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

                if z > pt[2]:
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

    # Initialize Mesh
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
    warning = None

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

        print('Approx Z:',Z)

        # Create approximate volume mesh
        apxVert = []
        apxFace = []
        iApxVert = 0

        for af in adjFace:
            iApxVert = len(apxVert)
            apxVert.append(vertices[faceVert[af][0]])
            apxVert.append(vertices[faceVert[af][1]])
            apxVert.append(vertices[faceVert[af][2]])
            apxFace.append([iApxVert, iApxVert + 1, iApxVert + 2])

        # Create boundary mesh
        apxVert = array(apxVert)
        apxFace = array(apxFace)
        apxMesh = pm.form_mesh(apxVert, apxFace)

        #print('len apxVert', len(apxVert))
        #print('første vert', apxVert)

        # Boundary Box
        maxmin = apxMesh.bbox
        x1, y1, z1 = maxmin[0]
        x2, y2, z2 = maxmin[1]

        print('apxMesh:',maxmin[0],'\n\t',maxmin[1])

        zMax = mesh.bbox[1][2]
        print('zMax:',zMax)
        pm.save_mesh('apxmesh.obj', apxMesh)

        # Volume function to solve
        def findHeight(z):
            print('current z:',z)

            # Check if pools will overflow mesh
            if z > zMax:
                z = zMax
                warning = 'The pool have a greater volume than the mesh can contain. Pool set to fill entire mesh.'

            bVert = []
            bFace = []
            bVox = []

            # Add vertices
            bVert.append(array([x1, y1, z1]))  # 0
            bVert.append(array([x1, y2, z1]))  # 1
            bVert.append(array([x1, y2, z]))  # 2
            bVert.append(array([x1, y1, z]))  # 3

            bVert.append(array([x2, y2, z]))  # 4
            bVert.append(array([x2, y2, z1]))  # 5
            bVert.append(array([x2, y1, z1]))  # 6
            bVert.append(array([x2, y1, z]))  # 7

            # Add faces
            bFace.append([0, 1, 3])  # side 1
            bFace.append([1, 2, 3])  # side 1
            bFace.append([0, 3, 7])  # side 2
            bFace.append([0, 6, 7])  # side 2
            bFace.append([7, 6, 5])  # side 3
            bFace.append([5, 7, 4])  # side 3
            bFace.append([4, 5, 1])  # side 4
            bFace.append([4, 2, 1])  # side 4
            bFace.append([0, 1, 6])  # side 5
            bFace.append([1, 5, 6])  # side 5
            bFace.append([3, 7, 2])  # side 6
            bFace.append([2, 7, 4])  # side 6

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
            pm.save_mesh('bMesh.obj', bMesh)

            # Make intersection
            newMesh = pm.boolean(mesh,bMesh,'intersection')
            pm.save_mesh('intMesh.obj', newMesh)
            print('newMesh attributes',newMesh.get_attribute_names())

            # Get bottom part of mesh
            try:
                newSource = newMesh.get_attribute('source')
            except RuntimeError:
                # Change boolean engine to Cork and try different apporach to getting bottom faces
                warning = 'Changing Boolean Engine to Cork!'
                print(warning)
                newMesh = pm.boolean(mesh, bMesh, 'intersection', engine='cork')
                pm.save_mesh('intMesh.obj', newMesh)
                newMesh.add_attribute('face_centroid')
                newFace = newMesh.faces
                bottomFaces = []

                for newFaceIndex,newCen in enumerate(newMesh.get_attribute('face_centroid')):
                    if newCen < z:
                        bottomFaces.append(newFace[newFaceIndex])
                    else:
                        pass

            if not bottomFaces:
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

            if z == zMax:
                return 0

            else:
                # Compute volume
                volMesh.add_attribute('voxel_volume')
                volVol = volMesh.get_attribute('voxel_volume')
                volVol = sum(list((map(abs, volVol))))

                #print('volume',volume)
                #print('volVol1',volVol)

                return volume - volVol

        # Get final height
        zFinal = newton(findHeight,Z)

        """
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
        """

        # Save final mesh
        finalMesh, finalVol = findHeight(zFinal)
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

    # Open InData and edit last line
    file_obj = open("InData.txt",'r')
    file = file_obj.readlines()
    file_obj.close()

    mNames = ''
    for n in meshNames:
        mNames += ',' + n

    file[6] = 'meshNames.txt' + mNames

    outfile_obj = open("InData.txt", 'w')
    outfile_obj.writelines(file)

    # Write meshNames.txt
    file_obj = open("meshNames.txt", 'w')
    file_obj.write(mNames)
    file_obj.close()

    if warning:
        return warning


class simpleRain():
    def __init__(self, cpus, precipitation, windSpeed, windDirection, testPoints, testVectors, context, temperature, k):
        self.prec = precipitation
        self.windSpeed = windSpeed
        self.windDir = windDirection
        self.testPts = testPoints
        self.testVecs = testVectors
        self.context = context
        self.temp = temperature
        self.kMiss = k[0]
        self.kHit = k[1]
        self.dirVec = False
        self.hourlyResult = False
        self.wdr = False
        self.xyAngles = []
        self.yzAngles = []
        self.cpus = int(cpus)

    # Final function
    def rainHits(self):
        from System.Threading.Tasks.Parallel import ForEach
        from math import degrees, exp, log, acos, sqrt
        from rhinoscriptsyntax import XformMultiply, VectorCreate, AddPoint, VectorTransform, XformRotation2
        from Rhino.Geometry.Intersect.Intersection import RayShoot
        from Rhino.Geometry import Ray3d
        import threading
        import Queue
        import math

        # Help functions

        def rain_vector(Vw, regn):

            # Rain drop radius:
            A = 1.3
            p = 0.232
            n = 2.25

            if regn == 0:
                return 0

            def f_a(I):
                return A * I ** p

            a = f_a(regn)
            r = a * exp(log(-log(0.5)) / n) / 1000

            # Angle:
            # rho_L = 1.2
            # rho_w = 1000
            # g = 9.81
            # c = 0.3
            # alpha = 3*c*rho_L*Vw^2*r^2/sqrt(4*r^4*(9*Vw^2*c^2*rho_L^2+64*g^2*r^2*rho_w^2))
            # Simplified it becomes:

            a = (0.54 * Vw ** 2 * r ** 2) / sqrt(r ** 4 * (1.1664 * Vw ** 2 + 6.159110400 * 10 ** 9 * r ** 2))
            if a > 1:
                a = 1
            alpha = acos(a)

            return alpha

        def rotate_yz(angle):
            return XformRotation2(angle, [1, 0, 0], [0, 0, 0])

        def rotate_xy(angle):
            return XformRotation2(angle, [0, 0, 1], [0, 0, 0])

        # Correction of wind direction
        def B_wind(angle, direction):
            c = 360 - (angle + 90)
            # print(c)

            a = abs(c - direction)
            if a < 180:
                b = a
            else:
                b = 360 - a

            return math.radians(b)

        def rayShoot():
            """Build on: Ladybug - RayTrace"""

            # Initialize
            while True:

                numOfBounce = 1
                startPt, xyAngle, yzAngle = q.get()
                if startPt is None:
                    break

                vector = direction_vector
                ray = Ray3d(startPt, vector)
                # Check the wind direction
                B = B_wind(xyAngle, self.windDir[i])
                if B > math.pi / 2:
                    hourly_rain.append(0)
                    hourly_result.append(False)


                else:
                    # Compute rain amount
                    K_wind = math.cos(B) / math.sqrt(
                        1 + 1142 * (math.sqrt(self.prec[i]) / self.windSpeed[i] ** 4)) * math.exp(
                        -12 / (self.windSpeed[i] * 5 * self.prec[i] ** (0.25)))

                    # Shoot ray
                    intPt = RayShoot(ray, [self.context], numOfBounce)

                    # Check for intersection
                    if intPt:
                        # print('Intersection!')
                        hourly_result.append(True)
                        kRain = self.kHit
                        verticalFactor = (1/(90*K_wind*kRain)-1/90)*yzAngle
                        hourly_rain.append((K_wind * kRain * self.prec[i])*verticalFactor)

                    else:
                        # print('No intersection!')
                        hourly_result.append(False)
                        kRain = self.kMiss
                        verticalFactor = (1 / (90 * K_wind * kRain) - 1 / 90) * yzAngle
                        hourly_rain.append((K_wind * kRain * self.prec[i])*verticalFactor)

                # print('done')
                q.task_done()

        result = []
        dirVec_hourly = []
        wdr = []

        for i in range(0, len(self.prec)):

            if self.temp[i] <= -2 or self.windSpeed[i] <= 0 or self.prec[i] <= 0:
                dirVec_hourly.append(None)
                result.append([False] * len(self.testPts))

            else:

                # Rotate vectors towards the sky
                R_v = rain_vector(self.windSpeed[i], self.prec[i])
                towards_sky = rotate_yz(degrees(R_v))

                # Rotate vectors towards the wind
                w_d = self.windDir[i]
                towards_wind = rotate_xy(w_d)

                # Combine:
                transformation = XformMultiply(towards_wind, towards_sky)
                north_vector = VectorCreate(AddPoint(0, 0, 0), AddPoint(0, -1, 0))
                direction_vector = VectorTransform(north_vector, transformation)
                hourly_result = []
                hourly_rain = []

                # Put jobs in queue
                q = Queue.Queue()

                # Call task function

                for c in range(self.cpus):
                    t = threading.Thread(target=rayShoot)
                    # t.setDaemon(True)
                    t.start()

                for fi, pts in enumerate(self.testPts):
                    q.put((pts, self.xyAngles[fi], self.yzAngles[fi]))

                # Wait until all tasks in the queue have been processed
                q.join()

                dirVec_hourly.append(direction_vector)
                result.append(hourly_result)
                wdr.append(hourly_rain)

        self.hourlyResult = result
        self.dirVec = dirVec_hourly
        self.wdr = wdr

    def computeAngles(self):
        import Rhino.Geometry as rc
        from math import degrees

        # Construct planes
        zero = rc.Point3d(0, 0, 0)
        z = rc.Vector3d(0, 0, 1)
        x = rc.Vector3d(1, 0, 0)
        y = rc.Vector3d(0, 1, 0)
        xy = rc.Plane(zero, z).WorldXY
        yz = rc.Plane(zero, x).WorldYZ

        # Compute angles on the XY and YZ plane
        for fn in self.testVecs:
            self.xyAngles.append(degrees(rc.Vector3d.VectorAngle(fn, y, xy)))
            yz = degrees(rc.Vector3d.VectorAngle(fn, z, yz))

            #Correct angles
            if yz > 90:
                yz = 180-yz
            elif yz > 180:
                yz = yz-180
            elif yz > 270:
                yz = abs(yz-360)
            elif yz < 0:
                yz = yz*(-1)

            self.yzAngles.append(yz)