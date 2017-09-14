import cmf
from datetime import datetime,timedelta
import numpy as np

class Model_1D():

    def __init__(self, area, nCells, surfaceWater, RCurve, waterVolume):
        self.area = area
        self.nCells = nCells
        self.surfaceWater = surfaceWater
        self.RCurve = RCurve
        self.project = None
        self.potential = None
        self.moisture = None
        self.waterVolume = waterVolume
        if not self.project:
            self.project = self.createProject()

    def createProject(self):
        from datetime import datetime, timedelta

        project = cmf.project()

        # Add one cell at position (0,0,0), area according to input
        cell = project.NewCell(0, 0, 0, self.area, with_surfacewater = self.surfaceWater)

        # Create a retention curve
        r_curve = cmf.VanGenuchtenMualem(Ksat = self.RCurve[0], phi = self.RCurve[1], alpha = self.RCurve[2], n = self.RCurve[3])

        # Add ten layers of 10cm thickness
        for i in range(self.nCells):
            depth = (i + 1) * 0.1
            cell.add_layer(depth, r_curve)

        # Connect layers with Richards perc.
        # this can be shorten as
        cell.install_connection(cmf.Richards)

        # Create groundwater boundary (uncomment to use it)
        # Create the boundary condition
        gw = project.NewOutlet('groundwater', x=0, y=0, z=-1.1)

        # Set the potential
        gw.potential = -2

        # Connect the lowest layer to the groundwater using Richards percolation
        gw_flux = cmf.Richards(cell.layers[-1], gw)

        # Set inital conditions
        # Set all layers to a potential of -2 m
        cell.saturated_depth = 2.

        # 100 mm water in the surface water storage
        cell.surfacewater.depth = self.waterVolume

        # The run time loop, run for 72 hours
        # Save potential and soil moisture for each layer
        potential = [cell.layers.potential]
        moisture = [cell.layers.theta]

        # Create solver
        solver = cmf.CVodeIntegrator(self.project, 1e-6)
        solver.t = cmf.Time(1, 1, 2011)

        # Solve project
        for t in solver.run(solver.t, solver.t + timedelta(days=7), timedelta(hours=1)):
            potential.append(cell.layers.potential)
            moisture.append(cell.layers.theta)

        # Save results
        self.potential = potential
        self.moisture = moisture

class CMF_Model():

    def __init__(self, meshPath, weatherPath, analysisLength = 8760):
        self.project = cmf.project
        self.mesh = meshPath
        self.weatherPath = weatherPath
        self.weather = {}
        self.analysisLenght = analysisLength
        self.solved = False
        self.results = {}

    def meshToCells(self, meshPath, project):
        """
        Takes a mesh and converts it into CMF cells
        :param meshPath: Path to mesh file
        :param project: CMF project object
        :return: True
        """

        #Imports
        import pymesh as pm
        import numpy as np
        from itertools import compress

        # Load mesh
        mesh = pm.load_mesh(meshPath)
        mesh.enable_connectivity()

        # Initilize mesh data
        mesh.add_attribute('face_centroid')
        mesh.add_attribute('face_index')
        mesh.add_attribute('face_area')
        cenPts = mesh.get_attribute('face_centroid')
        faceIndex = mesh.get_attribute('face_index')
        faceArea = mesh.get_attribute('face_area')
        faces = mesh.faces
        vertices = mesh.vertices

        # Helper functions
        def faceVertices(faceIndex):
            """
            Returns the vertices of a face
            :param faceIndex: Face index (int)
            :return: v0, v1, v2
            """

            face = faces[int(faceIndex)]
            v0 = vertices[face[0]]
            v1 = vertices[face[1]]
            v2 = vertices[face[2]]

            return v0, v1, v2

        def faceFaceEdge(face0, face1):
            """
            Returns the width of the edge between to faces
            :param face0: Face index
            :param face1: Face index
            :return: 
            """

            #Get vertices
            v00, v01, v02 = faceVertices(int(face0))
            v10, v11, v12 = faceVertices(int(face1))

            #Find out which edge is shared
            com0 = np.equal(v00, [v10, v11, v12])
            com1 = np.equal(v01, [v10, v11, v12])
            com2 = np.equal(v02, [v10, v11, v12])

            if np.sum(com0) > 0:
                V = list(compress([v10, v11, v12], com0)).append(v00)

            elif np.sum(com1) > 0:
                V = list(compress([v10, v11, v12], com1)).append(v01)

            elif np.sum(com2) > 0:
                V = list(compress([v10, v11, v12], com2)).append(v02)

            else:
                # No shared edge
                return None

            #Compute the width of the edge
            dx = abs(V[0][0]-V[1][0])
            dy = abs(V[0][1]-V[1][1])
            dz = abs(V[0][2]-V[1][2])
            width = np.sqrt(dx**2+dy**2+dz**2)

            return width

        # Construct centroid list
        centroids = []
        i = 0
        while i < len(cenPts):
            for j in range(0,len(faceIndex)):
                centroids.append([faceIndex[j],np.array([cenPts[i],cenPts[i+1],cenPts[i+2]])])
                i += 3

        # Create cells
        for i in range(0,len(centroids)):
            x, y, z = centroids[i][1]
            a = faceArea[i]
            project.NewCell(x,y,z,a)

        # Connect cells
        for face in faceIndex:
            adjacentsFaces = mesh.get_face_adjacent_faces(int(face))

            for adj in adjacentsFaces:
                width = faceFaceEdge(face,adj)
                if width:
                    project[face].topology.AddNeighbor(project[adj],width)
                else:
                    pass

        return True

    def addTree(self, cellIndex):
        """Adds a tree to the model"""
        return None

    def addGrass(self, cellIndices):
        """Adds grass to the model"""
        return None

    def addLayersToCells(self, layers, depthOfLayers, rCurve):
        """Adds 'depth' to the cells"""

        for c in self.project.cells:
            # Add layers
            for i in range(layers):
                c.add_layer((i+1)*depthOfLayers, rCurve)

            # Install connections
            c.install_connection(cmf.Richards)
            c.install_connection(cmf.GreenAmptInfiltration)
            c.surfacewater_as_storage()

        # Connect fluxes
        cmf.connect_cells_with_flux(self.project, cmf.Darcy)
        cmf.connect_cells_with_flux(self.project, cmf.KinematicSurfaceRunoff)

        return True

    def createStream(self):
        """Create a stream"""
        return None

    def readWeather(self):
        """Reads a epw file and convert it into something usefull"""
        return None

    def solve(self, tolerance = 1e-9):
        """Solves the model"""
        # Create solver and set time
        solver = cmf.CVodeIntegrator(self.project, tolerance)
        solver.t = cmf.Time(1,1,2017)

        # Save potential and soil moisture for each layer, start with initial conditions
        potential = []
        moisture = []
        potentialHourly = []
        moistureHourly = []

        for c in self.project.cells:
            potentialHourly.append(c.layers.potential)
            moistureHourly.append(c.layers.theta)
        potential.append(potentialHourly)
        moisture.append(moistureHourly)

        # Run solver
        for t in solver.run(solver.t, solver.t + timedelta(hours = self.analysisLenght), timedelta(hours=1)):
            potentialHourly = []
            moistureHourly = []

            for c in self.project.cells:
                potential.append(c.layers.potential)
                moisture.append(c.layers.theta)
            potential.append(potentialHourly)
            moisture.append(moistureHourly)

        # Save results
        self.results['potential'] = potential
        self.results['moisture'] = moisture

        self.solved = True
        return True

    def saveResults(self, filePath):
        """Saves the computed results to a numpy file"""

        if not self.solved:
            print('Project not solved!')
            return None

        else:
            paths = []

            for res in self.results.keys():
                filePathExtention = filePath + '\\' + res
                np.save(filePathExtention, self.results[res])
                paths.append(filePathExtention + '.npy')

            return paths