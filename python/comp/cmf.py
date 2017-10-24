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
import os
import xml.etree.ElementTree as ET

#----------------------------------------------------------------------------------------------------------------------#
# Classes

class CMF_Ground(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['Layers','Soil layers to add to the mesh in m'],
                    1: ['RetentionCurve','Retention curve'],
                    2: ['SurfaceProperties', 'Input from Livestock CMF SurfaceProperties'],
                    3: ['InitialSaturation', 'Initial saturation of the soil layers'],
                    4: ['FaceIndices', 'List of face indices, on where the ground properties are applied.']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Ground', 'Livestock Ground Data Class']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.componetNumber = 11
        self.faceIndices = None
        self.layers = None
        self.retentionCurve = None
        self.surfaceProperties = None
        self.initialSaturation = None
        self.checks = [False, False, False, False, False]
        self.results = None

    def checkInputs(self, ghenv):
        warning = []

        if self.layers:
            self.checks[1] = True
        else:
            warning.append('Layer values must be float or list of floats! Input provided was: ' + str(self.layers))

        if self.retentionCurve:
            self.checks[2] = True
        else:
            warning.append('Retention curve is wrong!')

        if isinstance(self.initialSaturation,float):
            self.checks[4] = True
        else:
            warning.append('Initial saturation must be float! Input provided was: ' + str(self.initialSaturation))

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

    def runChecks(self, ghenv, layers, retentionCurve, surfaceProperties, initialSaturation, faceIndices):

        # Gather data
        self.layers = layers
        self.retentionCurve = retentionCurve
        self.surfaceProperties = surfaceProperties
        self.initialSaturation = initialSaturation
        self.faceIndices = faceIndices

        # Run checks
        self.checkInputs(ghenv)

    def run(self):
        if self.checks == True:
            groundDict = {'faceIndices': self.faceIndices,
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
            return {0: ['Property','0-1 grasses. 2-6 soils']}

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

    def runChecks(self, ghenv, property):

        # Gather data
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

            self.results = ls.PassClass(self.property, 'SurfaceProperty')


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
            self.results = ls.PassClass(self.property, 'RetentionCurve')


class CMF_Solve(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['Mesh', 'Topography as a mesh'],
                    1: ['Ground', 'Input from Livestock CMF_Ground'],
                    2: ['Weather','Input from Livestock CMF_Weather'],
                    3: ['Trees','Input from Livestock CMF_Tree'],
                    4: ['Stream','Input from Livestock CMF_Stream'],
                    5: ['Folder', 'Path to folder. Default is Desktop'],
                    6: ['CaseName','Case name as string. Default is CMF'],
                    7: ['Write','Boolean to write files'],
                    8: ['Overwrite', 'If True excisting case will be overwritten. Default is set to True'],
                    9: ['WithSSH', 'If True, case will be run through ssh connection.'
                                   '\nConfigure the connection with Livestock SSH'],
                    10: ['Run', 'Boolean to run analysis']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['ResultPath', 'Path to result files']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.componetNumber = 14
        self.mesh = None
        self.ground = None
        self.weather = None
        self.trees = None
        self.stream = None
        self.folder = None
        self.caseName = None
        self.casePath = None
        self.writeCase = None
        self.overwrite = True
        self.sshRun = False
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

    def runChecks(self, ghenv, mesh, ground, weather, trees=None, stream=None, folder=r'%systemdrive%\users\%username%\Desktop',
                  name='CMF', write=False, overwrite=True, ssh=False, run=False):

        # Gather data
        self.mesh = mesh
        self.ground = ground
        self.weather = weather
        self.trees = trees
        self.stream = stream
        self.folder = folder
        self.caseName = name
        self.writeCase = write
        self.overwrite = overwrite
        self.sshRun = ssh
        self.runCase = run
        self.updateCasePath()

        # Run checks
        self.checkInputs(ghenv)

    def updateCasePath(self):
        self.casePath = self.folder + '\\' + self.caseName

    def write(self, doc):

        # check if folder exists
        if os.path.exists(self.casePath):
            self.written = True
        else:
            os.mkdir(self.folder + '/' + self.caseName)

        # Process weather
        weatherDic = self.weather.c
        weather_root = ET.Element('weather')
        weather_keys = weatherDic.keys()

        for k in weather_keys:
            data = ET.SubElement(weather_root, str(k))
            data.text = str(weatherDic[str(k)])

        weather_tree = ET.ElementTree(weather_root)
        weather_tree.write(self.casePath + '/' + 'weather.xml')

        # Save Mesh
        ls.bakeExportDelete(self.mesh, self.casePath, 'mesh', '.obj', doc)

        # Process ground
        groundDic = list(ground.c for ground in self.ground)
        ground_root = ET.Element('ground')

        for i in range(0, len(groundDic)):
            ground = ET.SubElement(ground_root, 'ground_%i' % i)
            g_keys = groundDic[i].keys()

            for g in g_keys:
                data = ET.SubElement(ground, str(g))
                #print(type(groundDic[i][str(g)]))
                try:
                    data.text = str(groundDic[i][str(g)].c)
                except:
                    data.text = str(groundDic[i][str(g)])

        ground_tree = ET.ElementTree(ground_root)
        ground_tree.write(self.casePath + '/' + 'ground.xml')

        # Process trees
        treeDic = list(tree.c for tree in self.trees)
        tree_root = ET.Element('tree')

        for i in range(0, len(treeDic)):
            tree = ET.SubElement(tree_root, 'tree_%i' % i)
            t_keys = treeDic[i].keys()

            for t in t_keys:
                data = ET.SubElement(tree, str(t))
                data.text = str(treeDic[i][str(t)])

        tree_tree = ET.ElementTree(tree_root)
        tree_tree.write(self.casePath + '/' + 'trees.xml')


        # Process stream
        #Add later


    def doCase(self):
        return None

    def doSSH(self):
        return None

    def checkResults(self, ghenv):
        resultpath = self.casePath + '/results.csv'

        if not self.sshRun:
            if os.path.exists(resultpath):
                return resultpath
            else:
                warning = 'Could not find result file. Unknown error occured'
                print(warning)
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, warning)

        else:
            warning = 'Alpha - SSH not coded yet!!!'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)


    def run(self, ghenv, doc):
        if self.checks and self.writeCase:
            self.write(doc)

        elif self.written and self.sshRun:
            self.doSSH()
            self.results = self.checkResults(ghenv)

        elif self.written and self.run:
            self.doCase()
            self.results = self.checkResults(ghenv)

        elif self.written:
            print('Set Run to True to run case')


class CMF_Results(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)
