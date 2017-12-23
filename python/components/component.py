__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.1.0"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import os

# Livestock imports

# Grasshopper imports
#import Grasshopper.Kernel as gh

# -------------------------------------------------------------------------------------------------------------------- #
# Grasshopper Component Class


class GHComponent:

    def __init__(self, ghenv):
        self.outputs = None
        self.inputs = None
        self.description = None
        self.gh_env = ghenv

    # COMPONENT STUFF
    def config_component(self, component_number):
        """
        Sets up the component, with the following steps:
        - Load component data
        - Generate component data
        - Generate outputs
        - Generate inputs
        :param component_number: Integer with the component number
        """

        # Load component data
        comp_data = component_data(component_number)

        # Generate component data
        self.gh_env.Component.Name = comp_data[0]
        self.gh_env.Component.NickName = comp_data[1]
        self.gh_env.Component.Message = comp_data[2]
        self.gh_env.Component.IconDisplayMode = self.gh_env.Component.IconDisplayMode.application
        self.gh_env.Component.Category = comp_data[3]
        self.gh_env.Component.SubCategory = comp_data[4]
        self.gh_env.Component.Description = self.description

        # Generate outputs:
        for output_ in range(len(self.outputs)):
            self.add_output_parameter(output_)

        # Generate inputs:
        for input_ in range(len(self.inputs)):
            self.add_input_parameter(input_)

    def add_warning(self, warning):
        """
        Adds a Grasshopper warning to the component.
        :param warning: Warning text.
        """

        print(warning)
        w = gh.GH_RuntimeMessageLevel.Warning
        self.gh_env.Component.AddRuntimeMessage(w, warning)

    def add_output_parameter(self, output_):
        """
        Adds an output to the Grasshopper component.
        :param output_: Output index.
        """

        self.gh_env.Component.Params.Output[output_].NickName = self.outputs[output_]['name']
        self.gh_env.Component.Params.Output[output_].Name = self.outputs[output_]['name']
        self.gh_env.Component.Params.Output[output_].Description = self.outputs[output_]['description']

    def add_input_parameter(self, input_):
        """
        Adds an input to the Grasshopper component.
        :param input_: Input index.
        """

        # Set information
        self.gh_env.Component.Params.Input[input_].NickName = self.inputs[input_]['name']
        self.gh_env.Component.Params.Input[input_].Name = self.inputs[input_]['name']
        self.gh_env.Component.Params.Input[input_].Description = self.inputs[input_]['description']

        # Set type access
        if self.inputs[input_]['access'] == 'item':
            self.gh_env.Component.Params.Input[input_].Access = gh.GH_ParamAccess.item
        elif self.inputs[input_]['access'] == 'list':
            self.gh_env.Component.Params.Input[input_].Access = gh.GH_ParamAccess.list
        elif self.inputs[input_]['access'] == 'tree':
            self.gh_env.Component.Params.Input[input_].Access = gh.GH_ParamAccess.tree

    def add_default_value(self, parameter, param_number):
        """
        Adds a default value to a parameter.
        :param parameter: Parameter to add default value to
        :param param_number: Parameter number
        :return: Parameter
        """

        if not parameter:
            return self.inputs[param_number]['default_value']
        else:
            return parameter

def component_data(n):
    """Function that reads the grasshopper component list and returns the component data"""

    appdata = os.getenv('APPDATA')
    component_file = appdata + '/McNeel\Rhinoceros/5.0/scripts/livestock/components/component_list.txt'

    read = open(component_file, 'r')
    lines = read.readlines()
    line = lines[n]
    line = line.split('\n')[0]
    line = line.split(';')

    return line


class GroundTemperature(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)
