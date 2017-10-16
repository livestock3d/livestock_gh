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
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs

#----------------------------------------------------------------------------------------------------------------------#
# Classes


class GHComponent:

    def __init__(self):
        self.outputs = None
        self.inputs = None

    def configComponent(self, ghenv, componetNumber):
        compData = ls.componetData(componetNumber)

        # Generate component data
        ghenv.Component.Name = compData[0]
        ghenv.Component.NickName = compData[1]
        ghenv.Component.Message = compData[2]
        ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
        ghenv.Component.Category = compData[3]
        ghenv.Component.SubCategory = compData[4]
        ghenv.Component.Description = compData[5]

        # Generate outputs:
        for output in range(len(self.outputs)):
            ghenv.Component.Params.Output[output].NickName = self.outputs[output][0]
            ghenv.Component.Params.Output[output].Name = self.outputs[output][0]
            ghenv.Component.Params.Output[output].Description = self.outputs[output][1]

        # Generate inputs:
        for input in range(len(self.inputs)):
            ghenv.Component.Params.Input[input].NickName = self.inputs[input][0]
            ghenv.Component.Params.Input[input].Name = self.inputs[input][0]
            ghenv.Component.Params.Input[input].Description = self.inputs[input][1]


class AdaptiveClothing(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['Temperature', 'Temperature in C']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['ClothingValue', 'Calculated clothing value in clo.']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.componetNumber = 10
        self.T = None
        self.checks = False
        self.results = None


    def checkInputs(self, ghenv):
        if isinstance(self.T, float):
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def I_cl(self, ghenv):
        minI = 0.1
        maxI = 1.43
        i = 1.372 - 0.01866 * self.T - 0.0004849 * self.T ** 2 - 0.000009333 * self.T ** 3

        if minI < i < maxI:
            return i
        elif i < minI:
            return minI
        elif i > maxI:
            return maxI
        else:
            warning = 'Something went wring in the clothing function'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return False

    def config(self, ghenv):

        # Generate Component
        self.configComponent(ghenv, self.componetNumber)

    def runChecks(self, ghenv, t):
        # Gather data
        self.T = t
        # Run checks
        self.checkInputs(ghenv)

    def run(self, ghenv):
        if self.checks:
            self.results = self.I_cl(ghenv)


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
            return {0: ['faceIndices', 'Face indices on where the surface properties, should be applied - List of integers'],
                    1: ['CustomGrass', 'Create a custom vegetation type. Input as string.\n Albedo, CanopyCapcityPerLAI,'
                                      'CanopyClosure, CanopyPARExtinction, fraction_at_rootdepth, Height, LAI,'
                                      'LeafWidth, RootContent, snow_albedo, StomatalResistance.\n'
                                      'For further information see:\n'
                                      'http://fb09-pasig.umwelt.uni-giessen.de/cmf/chrome/site/doxygen/classcmf_1_1upslope_1_1vegetation_1_1_vegetation.html']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['GrassData', "Prints the selected grass' properties"],
                    2: ['Grass', 'Livestock Grass Data Class']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.componetNumber = 13
        self.grass = None
        self.customGrass = None
        self.checks = False
        self.results = None

    def config(self, ghenv):

        # Generate Component
        self.configComponent(ghenv, self.componetNumber)

    def checkInputs(self, ghenv):
        self.checks = True

    def runChecks(self, ghenv, grass, customGrass):
        # Gather data
        self.grass = grass
        self.customGrass = customGrass

        # Run checks
        self.checkInputs(ghenv)

    def grassData(self, grassIndex):
        return None
    
    def run(self, ghenv):
        if self.checks:
            self.results = None


class CMF_Tree(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)


class CMF_Solve(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)


class GroundTemperature(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)