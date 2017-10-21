__author__ = "Christian Kongsgaard"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Christian Kongsgaard"
__email__ = "ocni@dtu.dk"
__status__ = "Work in Progress"

#----------------------------------------------------------------------------------------------------------------------#
# Imports
import sys
sys.path.insert(0, r'C:\livestock\python\classes')
import LivestockGH as ls
import LivestockCSV as csv
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
from ComponentClass import GHComponent

#----------------------------------------------------------------------------------------------------------------------#
# Classes

class CMF_Ground(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['Mesh', 'Topography as a mesh'],
                    1: ['Layers','Soil layers to add to the mesh in m'],
                    2: ['RetentionCurve','Retention curve'],
                    3: ['SurfaceProperties', 'Input from Livestock CMF SurfaceProperties'],
                    4: ['InitialSaturation', 'Initial saturation of the soil layers']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Ground', 'Livestock Ground Data Class']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.componetNumber = 11
        self.mesh = None
        self.layers = None
        self.retentionCurve = None
        self.surfaceProperties = None
        self.initialSaturation = None
        self.checks = [False, False, False, False, False]
        self.results = None

    def checkInputs(self, ghenv):
        warning = []

        if rs.IsMesh(self.mesh):
            self.checks[0] = True
        else:
            warning.append('Mesh input must be mesh! Input provided was:' + str(self.mesh))

        if isinstance(self.layers, list):
            layWarning = []
            for l in self.layers:
                if isinstance(l, float):
                    pass
                else:
                    layWarning.append(str(l))
            if not layWarning:
                self.checks[1] = True
            else:
                warning.append('Layer values must be float! Input provided was: ' + str(layWarning))

        elif isinstance(self.layers,float):
            self.checks[1] = True
        else:
            warning.append('Layer values must be float or list of floats! Input provided was: ' + str(self.layers))

        if isinstance(self.retentionCurve, list):
            self.checks[2] = True
        else:
            warning.append('Retention curve is wrong!')

        """
        if isinstance(self.surfaceProperties, list):
            surfacePropertiesWarning = []
            for g in self.surfaceProperties:
                if isinstance(g, int):
                    pass
                else:
                    surfacePropertiesWarning.append(str(g))
            if not surfacePropertiesWarning:
                self.checks[3] = True
            else:
                warning.append('Grass must be booleans! Input provided was: '+ str(surfacePropertiesWarning))
        elif isinstance(self.surfaceProperties, bool):
            self.checks[3] = True
        else:
            warning.append('Grass must be boolean or list of boolean! Input provided was: '+str(self.surfaceProperties))
        """

        if isinstance(self.initialSaturation, list):
            satWarning = []
            for i in self.initialSaturation:
                if isinstance(i, float):
                    pass
                else:
                    satWarning.append(str(i))
            if not satWarning:
                self.checks[4] = True
            else:
                warning.append('Initial saturation values must be float! Input provided was: ' + str(satWarning))

        elif isinstance(self.initialSaturation,float):
            self.checks[4] = True
        else:
            warning.append('Initial saturation must be float or list of floats! Input provided was: ' + str(self.initialSaturation))

        if warning:
            if isinstance(warning, list):
                for w in warning:
                    print(w + '\n')
            else:
                print(warning)

            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, str(warning))
        else:
            self.checks = True

    def config(self, ghenv):

        # Generate Component
        self.configComponent(ghenv, self.componetNumber)

    def runChecks(self, ghenv, mesh, layers, retentionCurve, grass, initialSaturation):
        # Gather data
        self.mesh = mesh
        self.layers = layers
        self.retentionCurve = retentionCurve
        self.grass = grass
        self.initialSaturation = initialSaturation

        # Run checks
        self.checkInputs(ghenv)

    def run(self):
        if self.checks == True:
            groundDict = {'mesh': self.mesh,
                          'layers': self.layers,
                          'retentionCurve': self.retentionCurve,
                          'surfaceProperties': self.surfaceProperties,
                          'initialSaturation': self.initialSaturation}

            self.results = ls.PassClass(groundDict,'CMF_Ground')


class CMF_Weather(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['Temperature', 'Temperature in C - List of floats'],
                    1: ['WindSpeed','Wind speed in m/s - List of floats'],
                    2: ['RelativeHumidity','Relative humidity in % - List of floats'],
                    3: ['CloudCover', 'Cloud cover, unitless between 0 and 1 - list of floats'],
                    4: ['GlobalRadiation', 'Global Radiation in MJ/(m^2*h) - list of floats'],
                    5: ['Rain', 'Horizontal precipitation in mm/h - list of floats'],
                    6: ['GroundTemperature', 'Ground temperature in C - list of floats'],
                    7: ['Location', 'A Ladybug Tools Location']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Weather', 'Livestock Weather Data Class']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.componetNumber = 12
        self.temp = None
        self.wind = None
        self.relHum = None
        self.cloudCover = None
        self.globalRadiation = None
        self.rain = None
        self.groundTemp = None
        self.location = None
        self.checks = [False, False, False, False, False, False, False, False]
        self.results = None

    def checkInputs(self, ghenv):
        if self.temp:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def config(self, ghenv):

        # Generate Component
        self.configComponent(ghenv, self.componetNumber)

    def runChecks(self, ghenv, temp, wind, relhum, cloudCover, globalRadiation, rain, groundTemp, location):

        # Gather data
        self.temp = temp
        self.wind = wind
        self.relhum = relhum
        self.cloudCover = cloudCover
        self.globalRadiation = globalRadiation
        self.rain = rain
        self.groundTemp = groundTemp
        self.location = location

        # Run checks
        self.checkInputs(ghenv)

    def convertCloudCover(self):
        return None

    def convertLocation(self):
        locationName, lat, long, timeZone, elevation = ls.decomposeLadybugLocation(self.location)
        return lat, long, timeZone

    def run(self):
        if self.checks == True:

            sun = self.convertCloudCover()
            latitude, longitude, timeZone = self.convertLocation()

            weatherDict = {'temp': self.temp,
                           'wind': self.wind,
                           'relHum': self.relHum,
                           'sun': sun,
                           'rad': self.globalRadiation,
                           'rain': self.rain,
                           'groundTemp': self.groundTemp,
                           'latitude': latitude,
                           'longitude': longitude,
                           'timeZone': timeZone}

            self.results = ls.PassClass(weatherDict, 'CMF_Weather')


class CMF_Stream(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs(x):
            if x == 0:
                return {0: ['MidStreamCurve', 'Curve following the middle of the stream'],
                        1: ['CrossSections','Cross section curves along the stream']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Stream', 'Livestock Stream Data Class'],
                    2: ['ReconstructedStream', 'The reconstructed stream as represented in CMF']}

        self.inputs = inputs(0)
        self.outputs = outputs()
        self.componetNumber = 13
        self.midCurve = None
        self.crossSections = None
        self.shape = []
        self.x = None
        self.y = None
        self.z = None
        self.lengths = None
        self.width = None
        self.slopeBank = None
        self.waterDepth = None
        self.checks = [False, False]
        self.results = None

    def checkInputs(self, ghenv):
        warning = []

        if self.midCurve:
            self.checks = True

    def config(self, ghenv):

        # Generate Component
        self.configComponent(ghenv, self.componetNumber)

    def runChecks(self, ghenv, midCurve, crossSections):
        # Gather data
        self.midCurve = midCurve
        self.crossSections = crossSections

        # Run checks
        self.checkInputs(ghenv)

    def processCurves(self):

        def intersectionMidCrossSectionCurves(crossSections, midCurve):
            # get crossSection vertecies and midPoint and crossSection intersections
            intersectionPoints = []
            crossSectionVerts = []

            for crv in crossSections:
                intersectionPoints.append(rs.CurveCurveIntersection(midCurve, crv)[0][1])
                crossSectionVerts.append(rs.PolylineVertices(crv))

            if len(crossSectionVerts[0]) == 3:
                shape = 0 #triangular reach
                return intersectionPoints, crossSectionVerts, shape
            elif len(crossSectionVerts[0]) == 4:
                shape = 1 #rectangular reach
                return intersectionPoints, crossSectionVerts, shape
            else:
                print('Error in shape')
                return None, None, None

        def getMidPoints(intersectionPoints):
            midPoints = []
            x = []
            y = []
            z = []

            for i in range(len(intersectionPoints)):
                pt = intersectionPoints[i] - intersectionPoints[i + 1]
                midPoints.append(pt)
                x.append(pt.X)
                y.append(pt.Y)
                z.append(pt.Z)

            return midPoints, x, y, z

        def sortCrossSectionVerts(crossSectionVerts, shape):
            if shape == 0:
                left = []
                right = []
                bottom = []
                for i in range(len(crossSectionVerts)):
                    pass
            elif shape == 1:
                return
            else:
                print('Shape with value:',str(shape),'not defined!')
                return None

        intersectionPoints, crossSectionVerts, self.shape = intersectionMidCrossSectionCurves(self.crossSections, self.midCurve)

        return None


    def run(self):
        if self.checks == True:
            groundDict = {'mesh': self.mesh,
                          'layers': self.layers,
                          'retentionCurve': self.retentionCurve,
                          'grass': self.grass,
                          'initialSaturation': self.initialSaturation}

            self.results = ls.PassClass(groundDict,'CMF_Ground')


class CMF_SurfaceProperties(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['FaceIndices', 'Mesh face indices where to chosen surface property should be applied'],
                    1: ['Property','0-1 grasses. 2-6 soils']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Units', 'Shows the units of the surface values'],
                    2: ['SurfaceValues','Chosen surface properties values'],
                    3: ['SurfaceProperties','Livestock surface properties data']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.componetNumber = 13
        self.data = None
        self.units = None
        self.dataPath = r'C:\livestock\data\surfaceData.csv'
        self.propertyIndex = None
        self.property = None
        self.faceIndices = None
        self.checks = False
        self.results = None


    def checkInputs(self, ghenv):
        if self.propertyIndex:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def config(self, ghenv):

        # Generate Component
        self.configComponent(ghenv, self.componetNumber)

    def runChecks(self, ghenv, faceIndices, property):

        # Gather data
        self.faceIndices = faceIndices
        self.propertyIndex = property

        # Run checks
        self.checkInputs(ghenv)

    def load_csv(self):

        load = csv.read_csv(self.dataPath)
        self.units = load[0]
        self.data = load[1]

    def pickProperty(self):
        self.load_csv()
        self.property = self.data[self.propertyIndex]

    def run(self):
        if self.checks:
            self.pickProperty()
            dic = {'faceIndices': self.faceIndices,
                   'property': self.property}

            self.results = ls.PassClass(dic, 'SurfaceProperty')


class CMF_SyntheticTree(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['FaceIndex', 'Mesh face index where tree is placed'],
                    1: ['TreeType','Tree types: 0 - Deciduous, 1 - Coniferous, 2 - Shrubs'],
                    2: ['Height','Height of tree in meters']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Units', 'Shows the units of the tree values'],
                    2: ['TreeValues','Chosen tree properties values'],
                    3: ['TreeProperties','Livestock tree properties data']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.componetNumber = 13
        self.data = None
        self.units = None
        self.dataPath = [r'C:\livestock\data\syntheticDeciduous.csv', r'C:\livestock\data\syntheticConiferous.csv',
                         r'C:\livestock\data\syntheticShrubs.csv']
        self.treeType = None
        self.height = None
        self.property = None
        self.faceIndex = None
        self.checks = False
        self.results = None


    def checkInputs(self, ghenv):
        if self.height:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def config(self, ghenv):

        # Generate Component
        self.configComponent(ghenv, self.componetNumber)

    def runChecks(self, ghenv, faceIndex, treeType, height):

        # Gather data
        self.faceIndex = faceIndex
        self.treeType = treeType
        self.height = height

        # Run checks
        self.checkInputs(ghenv)

    def load_csv(self):

        load = csv.read_csv(self.dataPath[self.treeType])
        self.units = load[0]
        self.data = load[1]

    def computeTree(self):
        self.load_csv()
        self.property = {'name': 'Synthetic Deciduous',
                         'height': self.height,
                         'lai': float(self.data[0][2]) * self.height + float(self.data[1][2]),
                         'albedo': float(self.data[0][3]) * self.height + float(self.data[1][3]),
                         'canopyClosure': float(self.data[2][4]),
                         'canopyPAR': float(self.data[2][5]),
                         'canopyCapasity': float(self.data[0][6]) * self.height + float(self.data[1][6]),
                         'sc': float(self.data[0][7]) * self.height + float(self.data[1][7]),
                         'rd': float(self.data[2][8]),
                         'frac_root': float(self.data[2][9])}

    def run(self):
        if self.checks:
            self.computeTree()
            dic = {'faceIndex': self.faceIndex,
                   'property': self.property}

            self.results = ls.PassClass(dic, 'SyntheticTreeProperty')


class CMF_RetentionCurve(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['SoilIndex', 'Index for chosing soil type']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Units', 'Shows the units of the curve values'],
                    2: ['CurveValues','Chosen curve properties values'],
                    3: ['RetentionCurve','Livestock Retention Curve']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.componetNumber = 15
        self.data = None
        self.units = None
        self.dataPath = r'C:\livestock\data\soilData.csv'
        self.property = None
        self.soilIndex = None
        self.checks = False
        self.results = None


    def checkInputs(self, ghenv):
        if isinstance(self.soilIndex, int):
            self.checks = True
        else:
            warning = 'soilIndex should be an integer'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def config(self, ghenv):

        # Generate Component
        self.configComponent(ghenv, self.componetNumber)

    def runChecks(self, ghenv, soilIndex):

        # Gather data
        self.soilIndex = soilIndex

        # Run checks
        self.checkInputs(ghenv)

    def load_csv(self):

        load = csv.read_csv(self.dataPath)
        self.units = load[0]
        self.data = load[1]

    def loadRetentionCurve(self):
        self.load_csv()
        self.property = {'type': str(self.data[self.soilIndex][0]),
                         'K_sat': float(self.data[self.soilIndex][1]),
                         'phi': float(self.data[self.soilIndex][2]),
                         'alpha': float(self.data[self.soilIndex][3]),
                         'n': float(self.data[self.soilIndex][4]),
                         'm': float(self.data[self.soilIndex][5]),
                         'l': float(self.data[self.soilIndex][6])}

    def run(self):
        if self.checks:
            self.loadRetentionCurve()
            self.results = ls.PassClass(self.property, 'SyntheticTreeProperty')


class CMF_Solve(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['Ground', 'Input from Livestock CMF_Ground'],
                    1: ['Weather','Input from Livestock CMF_Weather'],
                    2: ['Trees','Input from Livestock CMF_Tree'],
                    3: ['Stream','Input from Livestock CMF_Stream'],
                    4: ['Folder', 'Path to folder'],
                    5: ['CaseName','Case name as string'],
                    6: ['Write','Boolean to write files'],
                    7: ['Run', 'Boolean to run analysis']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['ResultPath', 'Path to result files']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.componetNumber = 14
        self.ground = None
        self.weather = None
        self.trees = None
        self.stream = None
        self.folder = None
        self.caseName = None
        self.writeCase = None
        self.runCase = None
        self.written = False
        self.checks = False
        self.results = None

    def checkInputs(self, ghenv):
        if self.ground:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def config(self, ghenv):

        # Generate Component
        self.configComponent(ghenv, self.componetNumber)

    def runChecks(self, ghenv, ground, weather, trees, stream, folder, name, write, run):

        # Gather data
        self.ground = ground
        self.weather = weather
        self.trees = trees
        self.stream = stream
        self.folder = folder
        self.caseName = name
        self.writeCase = write
        self.runCase = run

        # Run checks
        self.checkInputs(ghenv)

    def write(self):
        import pandas as pd

        # check if folder exists
        if os.path.exists(self.folder + '/' + self.caseName):
            pass
        else:
            os.mkdir(self.folder + '/' + self.caseName)

        # Process weather
        weatherDic = self.weather.c
        weatherDF = pd.DataFrame(weatherDic)

        # Process ground


        # Process trees

        # Process stream

        # Write to HDF
        file = self.folder + '/' + self.caseName + '.hdf5'
        store = pd.HDFStore(file, "w", complib=str("zlib"), complevel=5)
        store.put("weather", weatherDF, data_columns=weatherDF.columns)
        store.put()
        store.close()




    def doCase(self):
        return None

    def run(self, ghenv):
        if self.checks and self.writeCase:
            self.write()

        if self.written:
            self.results = self.doCase()