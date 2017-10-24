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
from ComponentClass import GHComponent

#----------------------------------------------------------------------------------------------------------------------#
# Classes

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