__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

#----------------------------------------------------------------------------------------------------------------------#
# Imports
import sys
sys.path.insert(0, r'C:\livestock\python\classes')
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
        self.description = None

    def config_component(self, ghenv, component_number):
        comp_data = component_data(component_number)

        # Generate component data
        ghenv.Component.Name = comp_data[0]
        ghenv.Component.NickName = comp_data[1]
        ghenv.Component.Message = comp_data[2]
        ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
        ghenv.Component.Category = comp_data[3]
        ghenv.Component.SubCategory = comp_data[4]
        ghenv.Component.Description = self.description

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


def component_data(n):
    """Function that reads the grasshopper component list and returns the component data"""

    component_file = r'C:\livestock\python\comp\component_list.txt'

    read = open(component_file, 'r')
    lines = read.readlines()
    line = lines[n]
    line = line.split('\n')[0]
    line = line.split(';')

    return line


class GroundTemperature(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)