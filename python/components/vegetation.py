__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.1.0"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports

# Livestock imports
import livestock.lib.plant as plant
from component import GHComponent

# Grasshopper imports

# -------------------------------------------------------------------------------------------------------------------- #
# Livestock Vegetation Classes


class StomatalResistance(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'StomatalResistance_min',
                        'description': 'Minimum of stomatal resistance in s/m',
                        'access': 'item',
                        'default_value': None},
                    1: {'name': 'Radiation',
                        'description': 'Short wave radiation in W/m2',
                        'access': 'item',
                        'default_value': None},
                    2: {'name': 'Temperature',
                        'description': 'Air Temperature in C',
                        'access': 'item',
                        'default_value': None},
                    3: {'name': 'RelativeHumidity',
                        'description': 'Relative humidity is unitless',
                        'access': 'item',
                        'default_value': None}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},
                    1: {'name': 'StomatalResistance',
                        'description': 'Stomatal resistance in s/m'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 19
        self.description = 'Calculates the stomatal resistance of a plant.\n' \
                           'From Manickathan, Lento et.al 2018 - Parametric study of the influence of environmental ' \
                           'factors and tree properties on the transpirative cooling effect of trees.'
        self.rs_min = None
        self.radiation = None
        self.temperature = None
        self.relhum = None
        self.checks = [False, False, False, False]
        self.results = None

    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, stomatal_resistance_min, radiation, temperature, relhum):

        # Gather data
        self.rs_min = stomatal_resistance_min
        self.radiation = radiation
        self.temperature = temperature
        self.relhum = relhum

        # Run checks
        self.check_inputs()

    def run(self):
        if self.checks:
            self.results = plant.stomatal_resistance(self.rs_min, self.radiation, self.temperature, self.relhum)


class LeafTemperature(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'AirTemperature',
                        'description': 'Temperature of the air in C',
                        'access': 'item',
                        'default_value': None},

                    1: {'name': 'RadiativeHeatFluxLeaf',
                        'description': 'Radiative heat flux of leaf W/m2',
                        'access': 'item',
                        'default_value': None},

                    2: {'name': 'LatentHeatFluxLeaf',
                        'description': 'Latent heat flux of leaf W/m2',
                        'access': 'item',
                        'default_value': None},

                    3: {'name': 'AerodynamicResistanceLeaf',
                        'description': 'Air resistance of leaf s/m',
                        'access': 'item',
                        'default_value': None}
                    }

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},
                    1: {'name': 'LeafTemperature',
                        'description': 'Leaf temperature in C'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 20
        self.description = 'Calculates the leaf temperature of a plant.\n' \
                           'From Manickathan, Lento et.al 2018 - Parametric study of the influence of environmental ' \
                           'factors and tree properties on the transpirative cooling effect of trees.'
        self.air_temperature = None
        self.rad_leaf = None
        self.lat_leaf = None
        self.air_resistance = None
        self.checks = [False, False, False, False]
        self.results = None

    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, air_temperature, q_rad_leaf, q_lat_leaf, air_resistance):

        # Gather data
        self.air_temperature = air_temperature
        self.rad_leaf = q_rad_leaf
        self.lat_leaf = q_lat_leaf
        self.air_resistance = air_resistance

        # Run checks
        self.check_inputs()

    def run(self):
        if self.checks:
            self.results = plant.leaf_temperature(self.air_temperature, self.rad_leaf,
                                                  self.lat_leaf, self.air_resistance)
