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
import os

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


class GroundTemperature(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)