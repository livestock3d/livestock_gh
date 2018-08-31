__author__ = "Christian Kongsgaard"
__license__ = "GNU GPLv3 "

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import subprocess

# Rhino and Grasshopper imports
import rhinoscriptsyntax as rs

# Livestock imports
from livestock.components.component import GHComponent
import livestock.lib.misc as gh_misc
import livestock.lib.ssh as gh_ssh
import livestock.lib.geometry as gh_geo
import livestock.lib.templates as template

# -------------------------------------------------------------------------------------------------------------------- #
# Livestock Comfort Classes and Functions


class AdaptiveClothing(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: ['Temperature', 'Temperature in C']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['ClothingValue', 'Calculated clothing value in clo.']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 10
        self.description = 'Computes the clothing values'
        self.temperature = None
        self.checks = False
        self.results = None

    def check_inputs(self):
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        if isinstance(self.temperature, float):
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            self.add_warning(warning)

    def insulation_clothing(self):
        """
        Calculates the clothing isolation in clo for a given outdoor temperature.
        Source: Havenith et al. - 2012 - "The UTCI-clothing model"
        """

        min_insulation = 0.1
        max_insulation = 1.43
        insulation = 1.372 \
                     - 0.01866 * self.temperature \
                     - 0.0004849 * self.temperature ** 2 \
                     - 0.000009333 * self.temperature ** 3

        if min_insulation < insulation < max_insulation:
            return insulation

        elif insulation < min_insulation:
            return min_insulation

        elif insulation > max_insulation:
            return max_insulation

        else:
            warning = 'Something went wring in the clothing function'
            self.add_warning(warning)

    def config(self):
        """
        Generates the Grasshopper component.
        """

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, temp):
        """
        Gathers the inputs and checks them.
        :param temp: Outdoor temperature.
        """

        # Gather data
        self.temperature = temp

        # Run checks
        self.check_inputs()

    def run(self):
        """
        In case all the checks have passed and run is True the component runs.
        It runs the insulation_clothing() function.
        """

        if self.checks:
            self.results = self.insulation_clothing()


