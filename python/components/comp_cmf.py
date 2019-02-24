__author__ = "Christian Kongsgaard"
__license__ = "GNU GPLv3"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import os
import xml.etree.ElementTree as ET
import collections
import subprocess
from shutil import copyfile
import pprint
import json
import datetime
from System.Diagnostics import Process
import shutil
import tempfile

# Livestock imports
import livestock.lib.ssh as ssh
import livestock.lib.cmf_lib as cmf_lib
import livestock.lib.geometry as gh_geo
import livestock.lib.livestock_csv as csv
from livestock.components.component import GHComponent
from livestock.components import component
import livestock.lib.misc as gh_misc
from livestock.lib.templates import pick_template

# Grasshopper imports
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs


# -------------------------------------------------------------------------------------------------------------------- #
# Classes


class CMFGround(GHComponent):
    """A component class that generates the CMF ground"""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: component.inputs('required'),

                    1: {'name': 'MeshFaces',
                        'description': 'The mesh the where the ground '
                                       'properties should be applied.',
                        'access': 'item',
                        'default_value': None},

                    2: {'name': 'Write',
                        'description': 'Boolean to write the mesh to disk',
                        'access': 'item',
                        'default_value': False},

                    3: component.inputs('optional'),

                    4: {'name': 'Layers',
                        'description': 'List of the depth of soil layers to '
                                       'add to the mesh in m.\n'
                                       'If the values 1 and 2 are given, two '
                                       'layers will be created. '
                                       'One from 0 to 1m and one from 1m to 2m.'
                                       '\nDefault is 1m',
                        'access': 'list',
                        'default_value': 1},

                    5: {'name': 'GroundType',
                        'description': 'Ground type to be applied. A number '
                                       'from 0-6 can be provided or the '
                                       'Livestock Ground Type component can be '
                                       'connected.\n'
                                       '0 - Short grass with medium ground\n'
                                       '1 - Gravel (light color and '
                                       'permeable)\n'
                                       '2 - Pavement (dark color and '
                                       'non-permeable)\n'
                                       'Default is 0 - Short grass with medium '
                                       'ground',
                        'access': 'item',
                        'default_value': 0},

                    6: {'name': 'SurfaceWater',
                        'description': 'Initial volume of surface water placed '
                                       'on each mesh face in m3.\n'
                                       'Default is set to 0m3',
                        'access': 'item',
                        'default_value': 0},

                    7: {'name': 'ETMethod',
                        'description': 'Set method to calculate '
                                       'evapotranspiration.\n'
                                       '0: No evapotranspiration\n'
                                       '1: Penman-Monteith\n'
                                       '2: Shuttleworth-Wallace\n'
                                       'Default is set to no '
                                       'evapotranspiratio.',
                        'access': 'item',
                        'default_value': 0},

                    8: {'name': 'SurfaceRunOffMethod',
                        'description': 'Set the method for computing the '
                                       'surface run-off.\n'
                                       '0 - Kinematic Wave.\n'
                                       '1 - Diffusive Wave.\n'
                                       'Default is set 0 - Kinematic Wave.',
                        'access': 'item',
                        'default_value': 0}
                    }

        def outputs():
            return {0: component.outputs('readme'),

                    1: {'name': 'GroundData',
                        'description': 'Livestock Ground Data'},

                    2: {'name': 'Ground',
                        'description': 'Livestock Ground Data Class'}}

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 11
        self.description = 'Generates CMF ground' \
                           '\nCMF ground is a mesh surface with porous or ' \
                           'glass-like properties.' \
                           'CMF ground can be used to model surface runoff and ' \
                           'water transport on and within the mesh.' \
                           '\nIcon art based created by Ben Davis from the ' \
                           'Noun Project.'
        self.checks = False
        self.results = None

        # Data Parameters
        self.mesh_faces = None
        self.layers = None
        self.ground_type = None
        self.surface_water = None
        self.et_number = None
        self.surface_run_off_method = None
        self.ground_dict = {'mesh': None, 'layers': None, 'ground_type': None, 'surface_water': None,
                            'et_method': None, 'runoff_method': None}

    def check_inputs(self):
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, mesh_faces, write, layers, ground_type, surface_water,
                   et_method, surface_run_off_method):
        """
        Gathers the inputs and checks them.

        :param layers: Depth of layers.
        :param retention_curve: Livestock retention curve dict.
        :param vegetation_properties: Livestock vegetation properties dict.
        :param saturated_depth: Saturated depth of the cell.
        :param surface_water: Initial surface water volume.
        :param face_indices: Face indices where the properties should be applied to.
        :param et_method: Evapotranspriation calculation method.
        :param manning_: Manning roughness.
        :param puddle: Puddle depth.
        :param surface_run_off_method: Surface Run-off method.
        """

        # Gather data
        self.mesh_faces = self.add_default_value(mesh_faces, 1)
        self.write = self.add_default_value(write, 2)
        self.layers = self.add_default_value(layers, 4)
        self.ground_type = self.convert_ground_type(ground_type)
        self.surface_water = self.add_default_value(surface_water, 6)
        self.et_number = self.add_default_value(et_method, 7)
        self.surface_run_off_method = self.add_default_value(
            surface_run_off_method, 8)

        # Run checks
        self.check_inputs()

    def convert_ground_type(self, ground_type):
        if isinstance(ground_type, int) or isinstance(ground_type, float):
            return self.construct_ground_type(ground_type)

        elif not ground_type:
            return self.construct_ground_type(0)

        else:
            return ground_type.c

    @staticmethod
    def construct_ground_type(index):
        manning = None
        puddle = 0.01
        saturated_depth = 3

        if index == 0:
            return {'retention_curve': cmf_lib.load_retention_curve(0),
                    'surface_properties': cmf_lib.load_surface_cover(0),
                    'manning': manning,
                    'puddle_depth': puddle,
                    'saturated_depth': saturated_depth, }

        elif index == 1:
            return {'retention_curve': cmf_lib.load_retention_curve(1),
                    'surface_properties': cmf_lib.load_surface_cover(3),
                    'manning': manning,
                    'puddle_depth': puddle,
                    'saturated_depth': saturated_depth, }

        elif index == 2:
            return {'retention_curve': cmf_lib.load_retention_curve(0,
                                                                    {'k_sat':
                                                                         0.01}),
                    'surface_properties': cmf_lib.load_surface_cover(5),
                    'manning': manning,
                    'puddle_depth': puddle,
                    'saturated_depth': saturated_depth, }

        else:
            raise ValueError('Ground type should be an integer from 0-2. '
                             'Given value was:' + str(index))

    def convert_et_number_to_method(self):
        """
        Converts a number into a ET method.

        :return: ET method name.
        """

        if self.et_number == 0:
            return None
        elif self.et_number == 1:
            return 'penman_monteith'
        elif self.et_number == 2:
            return 'shuttleworth_wallace'
        else:
            w = 'ETMethod has to between 0 and 2. Input was: ' + \
                str(self.et_number)
            self.add_warning(w)
            raise ValueError(w)

    def convert_runoff_number_to_method(self):
        """
        Converts a number into a surface run-off method.

        :return: Surface run-off name
        """

        if self.surface_run_off_method == 0:
            return 'kinematic'
        elif self.surface_run_off_method == 1:
            return 'diffusive'
        else:
            w = 'SurfaceRunOffMethod has to between 0 and 1. Input was: ' + \
                str(self.surface_run_off_method)
            self.add_warning(w)
            raise ValueError(w)

    def write_mesh(self, doc):
        tmp_folder = os.path.join(tempfile.gettempdir(), 'livestock')
        if not os.path.exists(tmp_folder):
            os.mkdir(tmp_folder)

        mesh_name = 'mesh_' + str(self.mesh_faces)
        gh_geo.bake_export_delete(self.mesh_faces, tmp_folder,
                                  mesh_name, '.obj', doc)

        return mesh_name

    def run(self, doc):
        """
        In case all the checks have passed the component runs.
        The component puts all the inputs into a dict and uses PassClass
        to pass it on.
        """

        if self.checks and self.write:
            self.ground_dict = {
                'mesh': self.write_mesh(doc),
                'layers': self.layers,
                'ground_type': self.ground_type,
                'surface_water': self.surface_water,
                'et_method': self.convert_et_number_to_method(),
                'runoff_method': self.convert_runoff_number_to_method()
            }

            self.results = gh_misc.PassClass(self.ground_dict, 'Ground')


class CMFGroundType(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: component.inputs('optional'),

                    1: {'name': 'RetentionCurve',
                        'description': 'Sets the retention curve for the '
                                       'ground. Can either be an integer from '
                                       '0-5 or'
                                       'the output from CMF RetentionCurve.\n'
                                       '0 - Standard CMF Retention Curve\n'
                                       '1 - Coarse Soil\n'
                                       '2 - Medium Soil\n'
                                       '3 - Medium Fine Soil\n'
                                       '4 - Fine Soil\n'
                                       '5 - Very Fine Soil\n'
                                       'Default is set to 0: Standard CMF Retention Curve',
                        'access': 'item',
                        'default_value': 0},

                    2: {'name': 'SurfaceCover',
                        'description': 'Sets the surface cover for the ground. '
                                       'Can either be an integer from 0-6 or'
                                       'the output from CMF Surface Cover.\n'
                                       '0 - Short Grass: 0.12m\n'
                                       '1 - High Grass: 0.4m\n'
                                       '2 - Wet Sand\n'
                                       '3 - Yellow Sand\n'
                                       '4 - White Sand\n'
                                       '5 - Bare Moist Soil\n'
                                       '6 - Bare Dry Soil\n'
                                       'Default is set to 0: Short Grass: 0.12m',
                        'access': 'item',
                        'default_value': 0},

                    3: {'name': 'Manning',
                        'description': 'Set Manning roughness. '
                                       '\nIf not set CMF calculates it from '
                                       'the above given values.',
                        'access': 'item',
                        'default_value': None},

                    4: {'name': 'PuddleDepth',
                        'description': 'Set puddle depth. Puddle depth is the '
                                       'height were run-off begins.\n '
                                       'Default is set to 0.01m',
                        'access': 'item',
                        'default_value': 0.01},

                    5: {'name': 'SaturatedDepth',
                        'description': 'Set the saturated depth. '
                                       'The saturated depth is where the ground water level is at.\n '
                                       'Default is set to 3m',
                        'access': 'item',
                        'default_value': 3.0},
                    }

        def outputs():
            return {0: component.outputs('readme'),

                    1: {'name': 'GroundTypeData',
                        'description': 'Livestock Ground Type Data'},

                    2: {'name': 'GroundType',
                        'description': 'Livestock Ground Type Data Class'}}

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 11
        self.description = 'Specifies the CMF Ground Type properties.'
        self.checks = False

        # Data Parameters
        self.retention_curve = None
        self.surface_properties = None
        self.manning = None
        self.puddle = None
        self.saturated_depth = None
        self.results = None

    def check_inputs(self):
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, retention_curve, surface_properties, manning_roughness, puddle_depth, saturated_depth):
        """
        Gathers the inputs and checks them.

        :param retention_curve: Livestock retention curve dict.
        :param surface_properties: Livestock surface properties dict.
        :param manning_roughness: Manning roughness.
        :param puddle_depth: Puddle depth.
        :param saturated_depth: Saturated depth of the cell.
        """

        # Gather data
        self.retention_curve = self.convert_retention_curve(retention_curve)
        self.surface_properties = self.convert_surface_properties(surface_properties)
        self.manning = self.add_default_value(manning_roughness, 2)
        self.puddle = self.add_default_value(puddle_depth, 3)
        self.saturated_depth = self.add_default_value(saturated_depth, 4)

        # Run checks
        self.check_inputs()

    @staticmethod
    def convert_retention_curve(retention_curve):
        if isinstance(retention_curve, int):
            return cmf_lib.load_retention_curve(retention_curve)
        elif not retention_curve:
            return cmf_lib.load_retention_curve(0)
        else:
            return retention_curve.c

    @staticmethod
    def convert_surface_properties(surface_cover):
        if isinstance(surface_cover, int):
            return cmf_lib.load_surface_cover(surface_cover)
        elif not surface_cover:
            return cmf_lib.load_surface_cover(0)
        else:
            return surface_cover.c

    def run(self):
        """
        In case all the checks have passed the component runs.
        The component puts all the inputs into a dict and uses
        PassClass to pass it on.
        """

        if self.checks:
            ground_type_dict = {'retention_curve': self.retention_curve,
                                'surface_properties': self.surface_properties,
                                'manning': self.manning,
                                'puddle_depth': self.puddle,
                                'saturated_depth': self.saturated_depth,
                                }

            self.results = gh_misc.PassClass(ground_type_dict, 'Ground Type')


class CMFWeather(GHComponent):
    """A component class that generates the CMF weather"""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: component.inputs('required'),

                    1: {'name': 'Location',
                        'description': 'A Ladybug Tools Location',
                        'access': 'item',
                        'default_value': None},

                    2: {'name': 'MeshFaceCount',
                        'description': 'Number of faces in the ground mesh',
                        'access': 'item',
                        'default_value': None},

                    3: component.inputs('optional'),

                    4: {'name': 'Temperature',
                        'description': 'Temperature in C. Either a list or a tree where the number of branches is equal'
                                       ' to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},

                    5: {'name': 'WindSpeed',
                        'description': 'Wind speed in m/s. Either a list or a tree where the number of branches is'
                                       ' equal to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},

                    6: {'name': 'RelativeHumidity',
                        'description': 'Relative humidity in %. Either a list or a tree where the number of branches is'
                                       ' equal to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},

                    7: {'name': 'CloudCover',
                        'description': 'Cloud cover, unitless between 0 and 1. Either a list or a tree where the number'
                                       ' of branches is equal to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},

                    8: {'name': 'GlobalRadiation',
                        'description': 'Global Radiation in W/m2. Either a list or a tree where the number of branches'
                                       ' is equal to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},

                    9: {'name': 'Rain',
                        'description': 'Horizontal precipitation in mm/h. Either a list or a tree where the number of'
                                       ' branches is equal to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},

                    10: {'name': 'GroundTemperature',
                         'description': 'Ground temperature in C. Either a list or a tree where the number of branches'
                                        ' is equal to the number of mesh faces.',
                         'access': 'tree',
                         'default_value': None},
                    }

        def outputs():
            return {0: component.outputs('readme'),

                    1: {'name': 'Weather',
                        'description': 'Livestock Weather Data Class'}}

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 12
        self.description = 'Generates CMF weather' \
                           '\nIcon art based created by Adrien Coquet from the Noun Project.'
        self.checks = [False, False, False, False, False, False, False, False]
        self.results = None

        # Data Parameters
        self.temp = None
        self.wind = None
        self.rel_hum = None
        self.cloud_cover = None
        self.global_radiation = None
        self.rain = None
        self.ground_temp = None
        self.location = None
        self.face_count = None

    def check_inputs(self):
        """Checks inputs and raises a warning if an input is not the correct type."""

        self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, location, face_count, temp, wind, rel_hum, cloud_cover, global_radiation,
                   rain, ground_temp):
        """
        Gathers the inputs and checks them.

        :param temp: Temperature
        :param wind: Wind speed
        :param rel_hum: Relative humidity
        :param cloud_cover: Cloud cover
        :param global_radiation: Global radiation
        :param rain: Rain
        :param ground_temp: Ground temperature.
        :param location: Ladybug Tool location
        :param face_count: Number of mesh faces in project
        """

        # Gather data
        if face_count:
            self.face_count = int(face_count)
        self.location = location

        self.temp = self.match_cell_count(temp)
        self.wind = self.match_cell_count(wind)
        self.rel_hum = self.match_cell_count(rel_hum)
        self.cloud_cover = self.match_cell_count(cloud_cover)
        self.global_radiation = self.match_cell_count(global_radiation)
        self.rain = self.match_cell_count(rain)
        self.ground_temp = self.match_cell_count(ground_temp)

        # Run checks
        self.check_inputs()

    def convert_cloud_cover(self):
        """
        | Converts cloud cover to sun shine fraction.
        | Sun shine = 1 - cloud cover

        :return: list with sun shine fractions.
        """

        if self.cloud_cover:
            sun_shine = {}

            for cloud_key in self.cloud_cover.keys():
                sun_shine[cloud_key] = []
                for cc in self.cloud_cover[cloud_key]:
                    sun_shine[cloud_key].append(1 - float(cc))

            return sun_shine

    def convert_radiation_unit(self):
        """
        | Converts radiation from W/m\ :sup:`2` to MJ/(m\ :sup:`2` day)
        | 1 W/m\ :sup:`2` => 60s * 60min * 24hours/10\ :sup:`6` => MJ/(m\ :sup:`2` day)
        | 1 W/m\ :sup:`2` = 0.0864 MJ/(m\ :sup:`2` day)

        """

        if self.global_radiation:
            converted_radiation = {}

            for radiation_key in self.global_radiation.keys():
                converted_radiation[radiation_key] = []
                for rad in self.global_radiation[radiation_key]:
                    converted_radiation[radiation_key].append(float(rad) * 0.0864)

            self.global_radiation = converted_radiation

    def convert_rain_unit(self):
        """
        | Converts rain from mm/h to mm/day
        | 1 mm/h = 24 mm/day

        """

        if self.rain:
            converted_rain = {}

            for rain_key in self.rain.keys():
                converted_rain[rain_key] = []
                for rain in self.rain[rain_key]:
                    converted_rain[rain_key].append(float(rain) * 24)

            self.rain = converted_rain

    def convert_location(self):
        """
        Extracts information from a Ladybug Tools location

        :return: Latitude, longitude and time zone
        """

        if self.location:
            location_name, latitude, longitude, time_zone, elevation = gh_misc.decompose_ladybug_location(self.location)

            return latitude, longitude, time_zone

        else:
            self.add_warning('Component needs a Ladybug Location to run')
            return None, None, None

    def match_cell_count(self, weather_parameter):
        """
        Checks whether a whether a weather parameter has the correct number of sublists,
        so they matches the number of cells. Then converts it into a dict with a list for each cell.

        :param weather_parameter: Weather parameter to check.
        :return: Corrected weather parameter as dict.
        """

        def find_list(weather_list_):
            if weather_list_:
                cleaned_list = []

                for element in weather_list_:
                    if isinstance(element, list):
                        cleaned_list.append(element)
                    else:
                        pass

                if len(cleaned_list) == 1:
                    return cleaned_list
                else:
                    return cleaned_list
            else:
                return None

        if weather_parameter:
            weather_list = gh_misc.tree_to_list(weather_parameter)
            clean_weather_list = find_list(weather_list)
            weather_dict = {}

            if not clean_weather_list:
                return None

            elif len(clean_weather_list) == 1:
                weather_dict['all'] = clean_weather_list[0]

            elif len(weather_list) == self.face_count:
                for i in range(0, len(weather_list)):
                    cell_number = 'cell_' + str(i)
                    weather_dict[cell_number] = weather_list[i]

            return weather_dict

        else:
            return None

    def print_weather_lengths(self):
        """Prints the length of each weather parameter."""

        def printer(parameter_name, parameter):
            if parameter:
                print(str(parameter_name) + ' includes: ' + str(
                    len(parameter.keys())) + ' lists')
            else:
                print(str(parameter_name) + ' is empty')

        printer('Temperature', self.temp)
        printer('Wind Speed', self.wind)
        printer('Relative Humidity', self.rel_hum)
        printer('Sunshine',
                self.cloud_cover)  # are converted from cloud cover to sun later, but have same length.
        printer('Global Radiation', self.global_radiation)
        printer('Rain', self.rain)
        printer('Ground Temperature', self.ground_temp)

    def run(self):
        """
        In case all the checks have passed the component runs.
        The following functions are run:

        - print_weather_lengths()
        - convert_cloud_cover()
        - convert_radiation_unit()
        - convert_location()

        A weather dict is created an passes on with PassClass.
        """

        if self.checks:
            # Make print statement
            self.print_weather_lengths()

            # Convertions
            sun = self.convert_cloud_cover()
            self.convert_rain_unit()
            self.convert_radiation_unit()
            latitude, longitude, time_zone = self.convert_location()

            # Construct dict
            weather_dict = {'temp': self.temp,
                            'wind': self.wind,
                            'rel_hum': self.rel_hum,
                            'sun': sun,
                            'rad': self.global_radiation,
                            'rain': self.rain,
                            'ground_temp': self.ground_temp,
                            'latitude': latitude,
                            'longitude': longitude,
                            'time_zone': time_zone}

            self.results = gh_misc.PassClass(weather_dict, 'Weather')


class CMFSurfaceProperties(GHComponent):
    """A component class that generates the CMF Vegetation Properties."""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: component.inputs('optional'),

                    1: {'name': 'SurfaceCover',
                        'description': 'Sets the surface cover for the ground.\n'
                                       '0 - Short Grass: 0.12m\n'
                                       '1 - High Grass: 0.4m\n'
                                       '2 - Wet Sand\n'
                                       '3 - Yellow Sand\n'
                                       '4 - White Sand\n'
                                       '5 - Bare Moist Soil\n'
                                       '6 - Bare Dry Soil\n'
                                       '7 - Deciduous Tree(s)'
                                       'Default is set to 0: Short Grass: 0.12m',
                        'access': 'item',
                        'default_value': 0},

                    2: {'name': 'Height',
                        'description': 'Height of the surface cover in meters.\n'
                                       'Default is 0.12m. Unless for trees there it is 5m',
                        'access': 'item',
                        'default_value': None},

                    3: {'name': 'LeafAreaIndex',
                        'description': 'Leaf area index of the surface cover. Leaf area index is unitless.\n'
                                       'Default is 2.88',
                        'access': 'item',
                        'default_value': None},

                    4: {'name': 'Albedo',
                        'description': 'Albedo of the surface cover. Albedo is unitless.\n'
                                       'Default is 0.23',
                        'access': 'item',
                        'default_value': None},

                    5: {'name': 'CanopyClosure',
                        'description': 'Canopy closure of the surface cover. Canopy closure is unitless.\n'
                                       'Default is 1.0',
                        'access': 'item',
                        'default_value': None},

                    6: {'name': 'CanopyPARExtinction',
                        'description': 'Canopy PAR Extinction of the surface cover. '
                                       'Canopy PAR Extinction is unitless.\n'
                                       'Default is 0.6',
                        'access': 'item',
                        'default_value': None},

                    7: {'name': 'CanopyCapacityLAI',
                        'description': 'Canopy Capacity per LAI of the surface cover. '
                                       'Canopy Capacity per LAI is in millimeters.\n'
                                       'Default is 0.1',
                        'access': 'item',
                        'default_value': None},

                    8: {'name': 'StomatalResistance',
                        'description': 'Stomatal Resistance of the surface cover. '
                                       'Stomatal Resistance is in s/m.\n'
                                       'Default is 100.0',
                        'access': 'item',
                        'default_value': None},

                    9: {'name': 'RootDepth',
                        'description': 'Root Depth of the surface cover. '
                                       'Root Depth is in meters.\n'
                                       'Default is 0.25',
                        'access': 'item',
                        'default_value': None},

                    10: {'name': 'FractionRootDepth',
                         'description': 'Fraction at root depth of the surface cover. '
                                        'Fraction at root depth is unitless.\n'
                                        'Default is 1',
                         'access': 'item',
                         'default_value': None},

                    11: {'name': 'LeafWidth',
                         'description': 'Leaf width of the surface cover. '
                                        'Leaf width is in meters.\n'
                                        'Default is 0.005m',
                         'access': 'item',
                         'default_value': None}
                    }

        def outputs():
            return {0: component.outputs('readme'),

                    1: {'name': 'Units',
                        'description': 'Shows the units of the surface values'},

                    2: {'name': 'SurfaceValues',
                        'description': 'Chosen Surface Properties Values'},

                    3: {'name': 'SurfaceProperties',
                        'description': 'Livestock Surface Properties Data Class'}}

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 13
        self.description = 'Generates CMF Surface Cover Properties' \
                           '\nIcon art based created by Ben Davis from the Noun Project.'
        self.checks = False
        self.units = cmf_lib.vegetation_units()
        self.results = None

        # Data Parameters
        self.property_index = None
        self.property = None
        self.properties_dict = {}
        self.height = None
        self.lai = None
        self.albedo = None
        self.canopy_closure = None
        self.canopy_par = None
        self.canopy_capacity = None
        self.stomatal = None
        self.root_depth = None
        self.root_fraction = None
        self.leaf_width = None

    def check_inputs(self):
        """Checks inputs and raises a warning if an input is not the correct type."""

        self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, property_, height, lai, albedo, canopy_closure,
                   canopy_par, canopy_cap,
                   stomatal, root_depth, root_fraction, leaf_width):
        """
        Gathers the inputs and checks them.

        :param property_: Property index.
        """

        # Gather data
        self.property_index = self.add_default_value(property_, 1)
        self.height = self.add_default_value(height, 2)
        self.lai = self.add_default_value(lai, 3)
        self.albedo = self.add_default_value(albedo, 4)
        self.canopy_closure = self.add_default_value(canopy_closure, 5)
        self.canopy_par = self.add_default_value(canopy_par, 6)
        self.canopy_capacity = self.add_default_value(canopy_cap, 7)
        self.stomatal = self.add_default_value(stomatal, 8)
        self.root_depth = self.add_default_value(root_depth, 9)
        self.root_fraction = self.add_default_value(root_fraction, 10)
        self.leaf_width = self.add_default_value(leaf_width, 11)
        self.modified_properties()

        # Run checks
        self.check_inputs()

    def modified_properties(self):
        self.properties_dict = collections.OrderedDict([
            ('height', self.height),
            ('lai', self.lai),
            ('albedo', self.albedo),
            ('canopy_closure', self.canopy_closure),
            ('canopy_par', self.canopy_par),
            ('canopy_capacity', self.canopy_capacity),
            ('stomatal_res', self.stomatal),
            ('root_depth', self.root_depth),
            ('root_fraction', self.root_fraction),
            ('leaf_width', self.leaf_width),
        ])

    def run(self):
        """
        | In case all the checks have passed the component runs.
        | It run pick_properties()
        | And passes on the property dict with PassClass.

        """

        if self.checks:
            self.property = cmf_lib.load_surface_cover(self.property_index,
                                                       self.properties_dict)
            self.results = gh_misc.PassClass(self.property, 'SurfaceCover')


class CMFSyntheticTree(GHComponent):
    """A component class that generates a synthetic tree."""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'FaceIndex',
                        'description': 'Mesh face index where tree is placed',
                        'access': 'item',
                        'default_value': None},

                    1: {'name': 'TreeType',
                        'description': 'Tree types: 0 - Deciduous. Default is deciduous',
                        'access': 'item',
                        'default_value': 0},

                    2: {'name': 'Height',
                        'description': 'Height of tree in meters. Default is set to 10m',
                        'access': 'item',
                        'default_value': 10}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},

                    1: {'name': 'Units',
                        'description': 'Shows the units of the tree values'},

                    2: {'name': 'TreeValues',
                        'description': 'Chosen tree properties values'},

                    3: {'name': 'TreeProperties',
                        'description': 'Livestock tree properties data'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 18
        self.description = 'Generates a synthetic tree'
        self.data = None
        self.units = None
        self.data_path = [os.getenv('APPDATA') +
                          r'\McNeel\Rhinoceros\5.0\scripts\livestock\data\syntheticDeciduous.csv',
                          os.getenv('APPDATA') +
                          r'\McNeel\Rhinoceros\5.0\scripts\livestock\data\syntheticConiferous.csv',
                          os.getenv('APPDATA') +
                          r'\McNeel\Rhinoceros\5.0\scripts\livestock\data\syntheticShrubs.csv']
        self.tree_type = None
        self.height = None
        self.property = None
        self.face_index = None
        self.checks = False
        self.results = None

    def check_inputs(self):
        """Checks inputs and raises a warning if an input is not the correct type."""

        if self.height:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            self.add_warning(warning)

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, face_index, tree_type, height):
        """
        Gathers the inputs and checks them.

        :param face_index: Mesh face index.
        :param tree_type: Tree type.
        :param height: Tree height.
        """

        # Gather data
        self.face_index = self.add_default_value(int(face_index), 0)
        self.tree_type = self.add_default_value(int(tree_type), 1)
        self.height = self.add_default_value(height, 2)

        # Run checks
        self.check_inputs()

    def load_csv(self):
        """Loads a csv file with the tree properties."""

        load = csv.read_csv(self.data_path[self.tree_type])
        self.units = load[0]
        self.data = load[1]

    def compute_tree(self):
        """Selects the correct tree property. It computes the property information and stores it as a ordered dict."""

        self.load_csv()
        self.property = collections.OrderedDict(
            [('name', 'Synthetic Deciduous'),
             ('height', self.height),
             ('lai',
              float(self.data[0][2]) * self.height + float(self.data[1][2])),
             ('albedo', float(self.data[0][3]) *
              self.height + float(self.data[1][3])),
             ('canopy_closure', float(self.data[2][4])),
             ('canopy_par', float(self.data[2][5])),
             ('canopy_capacity', float(self.data[0][6]) *
              self.height + float(self.data[1][6])),
             ('stomatal_res', float(self.data[0][7]) *
              self.height + float(self.data[1][7])),
             ('root_depth', float(self.data[2][8])),
             ('root_fraction', float(self.data[2][9])),
             ('leaf_width', 0.05)
             ])

    def run(self):
        """
        In case all the checks have passed the component runs.
        It runs the function compute_tree.
        Creates a dict and passes it on with PassClass.
        """

        if self.checks:
            self.compute_tree()
            dic = {'face_index': self.face_index,
                   'property': self.property}

            self.results = gh_misc.PassClass(dic, 'SyntheticTreeProperty')


class CMFRetentionCurve(GHComponent):
    """A component class that generates the CMF retention curve"""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'SoilIndex',
                        'description': 'Index for choosing soil type. '
                                       'Index from 0-5.\n'
                                       'Default is set to 0, which is the '
                                       'default CMF retention curve.',
                        'access': 'item',
                        'default_value': 0},

                    1: {'name': 'K_sat',
                        'description': 'Saturated conductivity in m/day',
                        'access': 'item',
                        'default_value': None},

                    2: {'name': 'Phi',
                        'description': 'Porosity in m3/m3',
                        'access': 'item',
                        'default_value': None},

                    3: {'name': 'Alpha',
                        'description': 'Inverse of water entry potential in 1/cm',
                        'access': 'item',
                        'default_value': None},

                    4: {'name': 'N',
                        'description': 'Pore size distribution parameter is unitless',
                        'access': 'item',
                        'default_value': None},

                    5: {'name': 'M',
                        'description': 'Van Genuchten m (if negative, 1-1/n is used) is unitless',
                        'access': 'item',
                        'default_value': None},

                    6: {'name': 'L',
                        'description': 'Mualem tortoisivity is unitless',
                        'access': 'item',
                        'default_value': None}
                    }

        def outputs():
            return {0: component.outputs('readme'),

                    1: {'name': 'Units',
                        'description': 'Shows the units of the curve values'},

                    2: {'name': 'CurveValues',
                        'description': 'Chosen curve properties values'},

                    3: {'name': 'RetentionCurve',
                        'description': 'Livestock Retention Curve'}}

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 15
        self.description = 'Generates CMF retention curve'
        self.checks = False
        self.results = None
        self.units = cmf_lib.retention_curve_units()

        # Data Parameters
        self.property = None
        self.properties_dict = {}
        self.soil_index = None
        self.k_sat = None
        self.phi = None
        self.alpha = None
        self.n = None
        self.m = None
        self.l = None

    def check_inputs(self):
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, soil_index, k_sat, phi, alpha, n, m, l):
        """
        Gathers the inputs and checks them.

        :param soil_index: Soil index.
        :param k_sat: Ksat
        :param phi: Phi
        :param alpha: Alpha
        :param n: N
        :param m: M
        :param l: L
        """

        # Gather data
        self.soil_index = self.add_default_value(soil_index, 0)
        self.k_sat = self.add_default_value(k_sat, 1)
        self.phi = self.add_default_value(phi, 2)
        self.alpha = self.add_default_value(alpha, 3)
        self.n = self.add_default_value(n, 4)
        self.m = self.add_default_value(m, 5)
        self.l = self.add_default_value(l, 6)
        self.modified_properties()

        # Run checks
        self.check_inputs()

    def modified_properties(self):
        self.properties_dict = collections.OrderedDict([
            ('k_sat', self.k_sat),
            ('phi', self.phi),
            ('alpha', self.alpha),
            ('n', self.n),
            ('m', self.m),
            ('l', self.l)
        ])

    def run(self):
        """
        In case all the checks have passed the component runs.
        Loads the retention curve data and passes it on with PassClass.
        """

        if self.checks:
            self.property = cmf_lib.load_retention_curve(self.soil_index,
                                                         self.properties_dict)
            self.results = gh_misc.PassClass(self.property, 'RetentionCurve')


class CMFSolve(GHComponent):
    """A component class that solves the CMF Case."""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: component.inputs('required'),

                    1: {'name': 'Ground',
                        'description': 'Output from Livestock CMF Ground',
                        'access': 'list',
                        'default_value': None},

                    2: {'name': 'Write',
                        'description': 'Boolean to write files',
                        'access': 'item',
                        'default_value': False},

                    3: {'name': 'Run',
                        'description': 'Boolean to run analysis\n',
                        'access': 'item',
                        'default_value': False},

                    4: component.inputs('optional'),

                    5: {'name': 'Weather',
                        'description': 'Input from Livestock CMF Weather',
                        'access': 'item',
                        'default_value': None},

                    6: {'name': 'Trees',
                        'description': 'Input from Livestock CMF Tree',
                        'access': 'list',
                        'default_value': None},

                    7: {'name': 'BoundaryConditions',
                        'description': 'Input from Livestock CMF Boundary Condition',
                        'access': 'list',
                        'default_value': None},

                    8: {'name': 'SolverSettings',
                        'description': 'Input from Livestock CMF Solver Settings',
                        'access': 'item',
                        'default_value': None},

                    9: {'name': 'Outputs',
                        'description': 'Connect Livestock Outputs',
                        'access': 'item',
                        'default_value': None},

                    10: {'name': 'CaseName',
                         'description': 'Case name as string.\n'
                                        'Default is: unnamed_cmf_case',
                         'access': 'item',
                         'default_value': 'unnamed_cmf_case'},

                    11: {'name': 'Folder',
                         'description': 'Path to case folder.\n'
                                        'Default is C:/livestock/analyses',
                         'access': 'item',
                         'default_value': r'C:\livestock\analyses'},

                    12: {'name': 'SSH',
                         'description': 'If True the case will be computed '
                                        'through the SSH connection.'
                                        'To get the SSH connection to work; '
                                        'the Livestock SSH Component '
                                        'should be configured. If False; '
                                        'the case will be run locally.\n'
                                        'Default is set to False',
                         'access': 'item',
                         'default_value': False},
                    }

        def outputs():
            return {0: component.outputs('readme'),

                    1: {'name': 'ResultPath',
                        'description': 'Path to result files'}}

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 14
        self.description = 'Solves CMF Case.\n' \
                           'Icon art based on Vectors Market from the ' \
                           'Noun Project.'
        self.checks = False
        self.results = None

        # Data Parameters
        self.ground = None
        self.write_case = None
        self.run_case = None
        self.weather = None
        self.trees = None
        self.boundary_conditions = None
        self.solver_settings = None
        self.output_config = None
        self.folder = None
        self.case_name = None
        self.ssh = None

        # Additional Parameters
        self.case_path = None
        self.mesh = None
        self.py_exe = self.get_cpython()
        self.written = False

    def check_inputs(self):
        """Checks inputs and raises a warning if an input is not
        the correct type."""

        self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, ground, write, run, weather, trees,
                   boundary_conditions, solver_settings,
                   outputs, name, folder, ssh, ):
        """
        Gathers the inputs and checks them.

        :param ground: Livestock Ground dict
        :param write: Whether to write or not
        :param run: Whether to run or not.
        :param weather: Livestock Weather dict
        :param trees: Livestock Tree dict
        :param boundary_conditions: Livestock Boundary Condition dict
        :param solver_settings: Livestock Solver settings dict
        :param outputs: Livestock Outputs dict
        :param name: Case name
        :param folder: Case folder
        :param ssh: Whether to run on ssh or not.
        """

        # Gather data
        self.ground = self.add_default_value(ground, 1)
        self.write_case = self.add_default_value(write, 2)
        self.run_case = self.add_default_value(run, 3)
        self.weather = self.add_default_value(weather, 5)
        self.trees = self.add_default_value(trees, 6)
        self.boundary_conditions = self.add_default_value(boundary_conditions,
                                                          7)
        self.solver_settings = self.convert_solver_settings(solver_settings)
        self.output_config = self.convert_outputs(outputs)
        self.case_name = self.add_default_value(name, 10)
        self.folder = self.add_default_value(folder, 11)
        self.ssh = self.add_default_value(ssh, 12)

        self.update_case_path()

        # Run checks
        self.check_inputs()

    def update_case_path(self):
        """Updates the case folder path."""

        self.case_path = self.folder + '\\' + self.case_name + '\\cmf'

    @staticmethod
    def convert_solver_settings(solver_settings):
        if not solver_settings:
            return cmf_lib.default_solver_settings()
        else:
            return solver_settings.c

    @staticmethod
    def convert_outputs(outputs):
        if not outputs:
            return cmf_lib.default_outputs()
        else:
            return outputs.c

    def write(self, doc):
        """
        Writes the needed files.

        :param doc: Grasshopper document.
        """

        # Helper functions
        def write_weather(weather_dict, folder):

            # Write json file
            weather_file = 'weather.json'
            with open(folder + '/' + weather_file, 'w') as outfile:
                json.dump(weather_dict.c, outfile)

            return weather_file

        def write_ground(ground_dict_, folder):

            # Process ground
            ground_dict = [ground.c
                           for ground in ground_dict_]

            # Copy meshes
            tmp_folder = os.path.join(tempfile.gettempdir(), 'livestock')
            meshes = []
            for ground in ground_dict:
                mesh_name = ground['mesh'] + '.obj'
                tmp_mesh = os.path.join(tmp_folder, mesh_name)
                case_mesh = os.path.join(self.case_path,
                                         mesh_name)
                shutil.copyfile(tmp_mesh, case_mesh)
                meshes.append(mesh_name)

            # Write json file
            ground_file = 'ground.json'
            with open(folder + '/' + ground_file, 'w') as outfile:
                json.dump(ground_dict, outfile)

            return [ground_file, ] + meshes

        def write_trees(tree_dict_, folder):
            # Process trees

            tree_dict = list(tree.c for tree in tree_dict_)
            tree_root = ET.Element('tree')

            for i in range(0, len(tree_dict)):
                tree = ET.SubElement(tree_root, 'tree_%i' % i)
                t_keys = tree_dict[i].keys()

                for t in t_keys:
                    data = ET.SubElement(tree, str(t))
                    data_to_write = tree_dict[i][str(t)]
                    if isinstance(data_to_write, dict):
                        data.text = str(dict(data_to_write))
                    else:
                        data.text = str(data_to_write)

            tree_tree = ET.ElementTree(tree_root)
            tree_file = 'trees.xml'
            tree_tree.write(folder + '/' + tree_file, xml_declaration=True)

            return tree_file

        def write_outputs(output_dict, folder):

            # Write json file
            output_file = 'outputs.json'
            with open(folder + '/' + output_file, 'w') as outfile:
                json.dump(output_dict, outfile)

            return output_file

        def write_boundary_conditions(boundary_dict_, folder):
            # Process boundary conditions
            boundary_conditions_dict = list(bc.c
                                            for bc in boundary_dict_)

            boundary_conditions_root = ET.Element('boundary_conditions')

            for i in range(0, len(boundary_conditions_dict)):
                boundary_condition = ET.SubElement(boundary_conditions_root,
                                                   'boundary_condition_%i' % i)

                bc_type = ET.SubElement(boundary_condition, 'type')
                bc_type.text = str(boundary_conditions_dict[i]['type'])

                bc_cell = ET.SubElement(boundary_condition, 'cell')
                bc_cell.text = str(boundary_conditions_dict[i]['cell'])

                bc_layer = ET.SubElement(boundary_condition, 'layer')
                bc_layer.text = str(boundary_conditions_dict[i]['layer'])

                if boundary_conditions_dict[i]['type'] == 'inlet':
                    bc_flux = ET.SubElement(boundary_condition, 'inlet_flux')
                    bc_flux.text = str(
                        boundary_conditions_dict[i]['inlet_flux'])

                    bc_step = ET.SubElement(boundary_condition, 'time_step')
                    bc_step.text = str(boundary_conditions_dict[i]['time_step'])

                elif boundary_conditions_dict[i]['type'] == 'outlet':
                    bc_flux = ET.SubElement(boundary_condition, 'outlet_type')

                    outlet_connection = ET.SubElement(bc_flux,
                                                      'outlet_connection')
                    outlet_connection.text = str(
                        boundary_conditions_dict[i]['outlet_type'][
                            'connection'])

                    outlet_parameter = ET.SubElement(bc_flux,
                                                     'connection_parameter')
                    outlet_parameter.text = str(
                        boundary_conditions_dict[i]['outlet_type'][
                            'connection_parameter'])

                    bc_flux = ET.SubElement(boundary_condition, 'location')
                    bc_flux.text = str(boundary_conditions_dict[i]['location'])

            boundary_conditions_tree = ET.ElementTree(boundary_conditions_root)
            boundary_condition_file = 'boundary_condition.xml'
            boundary_conditions_tree.write(
                folder + '/' + boundary_condition_file, xml_declaration=True)

            return boundary_condition_file

        def write_solver_info(solver_dict, folder):

            # Write json file
            solver_file = 'solver.json'
            with open(folder + '/' + solver_file, 'w') as outfile:
                json.dump(solver_dict, outfile)

            return solver_file

        def write_ssh_files(files_written_):
            # Clean SSH folder
            ssh.clean_ssh_folder()

            # SSH commands
            ssh_command = ssh.get_ssh()

            file_transfer = files_written_
            file_run = ['cmf_template.py']
            file_return = ['results.json']

            ssh_command['file_transfer'] = ','.join(file_transfer) + \
                                           ',cmf_template.py'
            ssh_command['file_run'] = ','.join(file_run)
            ssh_command['file_return'] = ','.join(file_return)
            ssh_command['template'] = 'cmf'

            ssh.write_ssh_commands(ssh_command)

            return ssh_command

        # check if folder exists
        if os.path.exists(self.case_path):
            shutil.rmtree(self.case_path)
            os.mkdir(self.case_path)
        else:
            os.mkdir(self.case_path)

        # Append to files written
        files_written = list()
        files_written.append(write_ground(self.ground, self.case_path))
        files_written.append(write_outputs(self.output_config, self.case_path))
        files_written.append(write_solver_info(self.solver_settings, self.case_path))

        if self.trees:
            files_written.append(write_trees(self.trees, self.case_path))

        if self.boundary_conditions:
            files_written.append(write_boundary_conditions(self.boundary_conditions, self.case_path))

        if self.weather:
            files_written.append(write_weather(self.weather, self.case_path))

        # template
        pick_template('cmf', self.case_path)

        # ssh
        if self.ssh:
            ssh_cmd = write_ssh_files(files_written)
            transfer_files = ssh_cmd['file_transfer'].split(',')

            # Copy files from case folder to ssh folder
            for file_ in transfer_files:
                copyfile(os.path.join(self.case_path, file_), os.path.join(ssh.ssh_path, file_))

        self.written = True

        return True

    def do_case(self):
        """Spawns a new subprocess, that runs the ssh template."""

        if self.ssh:
            template = ssh.ssh_path + '/ssh_template.py'
        else:
            template = self.case_path + '/cmf_template.py'

        # Run template
        Process.Start(self.py_exe, '"' + str(template) + '"').WaitForExit()

        return True

    def check_results(self):
        """
        Checks if the result files exists and then copies them form the ssh
        folder to the case folder.
        If not then a warning is raised.
        """

        ssh_result = ssh.ssh_path + '/results.json'
        result_path = self.case_path + '/results.json'

        if os.path.exists(ssh_result):
            copyfile(ssh_result, result_path)
            ssh.clean_ssh_folder()
            return result_path

        elif os.path.exists(result_path):
            return result_path

        else:
            warning = 'Could not find result file. Unknown error occurred'
            self.add_warning(warning)

    @staticmethod
    def read_log():
        log_file = os.path.join(ssh.livestock_path, 'logs', 'livestock_info.log')

        if os.path.exists(log_file):
            with open(log_file, 'r') as file_:
                log_lines = file_.readlines()

            for line in log_lines:
                print(line.strip())

    def run(self, doc):
        """
        In case all the checks have passed and write_case is True the
        component writes the case files.
        If all checks have passed and run_case is True the
        simulation is started.
        """

        if self.checks and self.write_case:
            self.write(doc)

        if self.checks and self.run_case:
            self.do_case()
            self.results = self.check_results()
            self.read_log()


class CMFResults(GHComponent):
    """A component class that loads the CMF results."""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: component.inputs('required'),

                    1: {'name': 'ResultFolder',
                        'description': 'Path to result folder. '
                                       'Accepts output from Livestock Solve.',
                        'access': 'item',
                        'default_value': None},

                    2: {'name': 'FetchResult',
                        'description': 'Choose which result should be loaded:'
                                       '\n0 - Evapotranspiration'
                                       '\n1 - Surface water volume'
                                       '\n2 - Surface water flux'
                                       '\n3 - Heat flux'
                                       '\n4 - Soil layer water flux'
                                       '\n5 - Soil layer potential'
                                       '\n6 - Soil layer theta'
                                       '\n7 - Soil layer volume'
                                       '\n8 - Soil layer wetness',
                        'access': 'item',
                        'default_value': 0},

                    3: {'name': 'Run',
                        'description': 'Run component',
                        'access': 'item',
                        'default_value': False},
                    }

        def outputs():
            return {0: component.outputs('readme'),

                    1: {'name': 'Units',
                        'description': 'Shows the units of the results'},

                    2: {'name': 'Values',
                        'description': 'List with chosen result values'},
                    }

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 17
        self.description = 'Load CMF results'
        self.checks = False

        # Data Parameters
        self.unit = None
        self.path = None
        self.fetch_result = None
        self.run_component = None
        self.results = None

    def check_inputs(self):
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, path, fetch_result, run):
        """
        Gathers the inputs and checks them.

        :param path: Result path
        :param fetch_result: Which result to fetch
        :param run: Whether to run the component or not.
        """

        # Gather data
        if path:
            self.path = os.path.join(path, 'results.json')
        else:
            self.path = None
        self.fetch_result = self.add_default_value(fetch_result, 1)
        self.run_component = self.add_default_value(run, 3)

        # Run checks
        self.check_inputs()

    def set_fetch_result(self):
        """Function to organize the output units."""

        if self.fetch_result == 0:
            self.fetch_result = 'evapotranspiration'
            self.unit = 'm3/day'

        elif self.fetch_result == 1:
            self.fetch_result = 'surface_water_volume'
            self.unit = 'm3'

        elif self.fetch_result == 2:
            self.fetch_result = 'surface_water_flux'
            self.unit = 'm3/day'

        elif self.fetch_result == 3:
            self.fetch_result = 'heat_flux'
            self.unit = 'W/m2'

        elif self.fetch_result == 4:
            self.fetch_result = 'volumetric_flux'
            self.unit = 'm3/day'

        elif self.fetch_result == 5:
            self.fetch_result = 'potential'
            self.unit = 'm'

        elif self.fetch_result == 6:
            self.fetch_result = 'theta'
            self.unit = 'm3'

        elif self.fetch_result == 7:
            self.fetch_result = 'volume'
            self.unit = 'm3'

        elif self.fetch_result == 8:
            self.fetch_result = 'wetness'
            self.unit = '-'

    def run(self):
        """
        In case all the checks have passed and run is True the component runs.
        Following functions are run: set_units(), load_cmf_result_file()
        The results are converted into a Grasshopper Tree structure.
        """

        if self.checks and self.run_component:
            self.set_fetch_result()
            results = cmf_lib.load_cmf_result_file(self.path,
                                                   self.fetch_result)
            self.results = gh_misc.list_to_tree(results)


class CMFOutputs(GHComponent):
    """
    A component class that specifies the wanted outputs from the
    CMF simulation.
    """

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: component.inputs('optional'),

                    1: {'name': 'Evapotranspiration',
                        'description': 'Cell evaporation'
                                       '\nDefault is set to False',
                        'access': 'item',
                        'default_value': None},

                    2: {'name': 'SurfaceWaterVolume',
                        'description': 'Cell surface water\n'
                                       'Default is set to True',
                        'access': 'item',
                        'default_value': 'init'},

                    3: {'name': 'SurfaceWaterFlux',
                        'description': 'Cell surface water flux\n'
                                       'Default is set to False',
                        'access': 'item',
                        'default_value': None},

                    4: {'name': 'HeatFlux',
                        'description': 'Cell surface heat flux\n'
                                       'Default is set to False',
                        'access': 'item',
                        'default_value': None},

                    5: {'name': 'VolumetricFlux',
                        'description': 'Soil layer volumetric flux vectors\n'
                                       'Default is set to False',
                        'access': 'item',
                        'default_value': None},

                    6: {'name': 'Potential',
                        'description': 'Soil layer total potential '
                                       '(Psi_tot = Psi_M + Psi_G)\n'
                                       'Default is set to False',
                        'access': 'item',
                        'default_value': None},

                    7: {'name': 'Theta',
                        'description': 'Soil layer volumetric water content of '
                                       'the layer\n'
                                       'Default is set to False',
                        'access': 'item',
                        'default_value': None},

                    8: {'name': 'Volume',
                        'description': 'Soil layer volume of water in the '
                                       'layer\n'
                                       'Default is set to True',
                        'access': 'item',
                        'default_value': 'init'},

                    9: {'name': 'Wetness',
                        'description': 'Soil layer wetness of the soil '
                                       '(V_volume/V_pores)\n'
                                       'Default is set to False',
                        'access': 'item',
                        'default_value': None}
                    }

        def outputs():
            return {0: component.outputs('readme'),

                    1: {'name': 'ChosenOutputs',
                        'description': 'Shows the chosen outputs'},

                    2: {'name': 'Outputs',
                        'description': 'Livestock Output Data'}
                    }

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 16
        self.description = "Specify the wanted outputs from the CMF simulation."
        self.results = None
        self.checks = False

        # Data Parameters
        self.evapo_trans = None
        self.surface_water_volume = None
        self.surface_water_flux = None
        self.heat_flux = None
        self.three_d_flux = None
        self.potential = None
        self.theta = None
        self.volume = None
        self.wetness = None
        self.output_dict = None

    def check_inputs(self):
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, evapo_trans, surface_water_volume, surface_water_flux,
                   heat_flux, three_d_flux,
                   potential, theta, volume, wetness):
        """
        Gathers the inputs and checks them.

        :param evapo_trans: Whether to include evapotranspiration or not.
        :param surface_water_volume: Whether to include surface water volume or not.
        :param surface_water_flux: Whether to include surface water flux or not.
        :param heat_flux: Whether to include surface heat flux or not.
        :param three_d_flux: Whether to include soil water flux or not.
        :param potential: Whether to include soil potential or not.
        :param theta: Whether to include soil theta or not.
        :param volume: Whether to include soil water volume or not.
        :param wetness: Whether to include soil wetness or not.
        """

        # Gather data
        self.evapo_trans = self.add_default_value(evapo_trans, 1)
        self.surface_water_volume = self.add_default_value(surface_water_volume,
                                                           2)
        self.surface_water_flux = self.add_default_value(surface_water_flux, 3)
        self.heat_flux = self.add_default_value(heat_flux, 4)
        self.three_d_flux = self.add_default_value(three_d_flux, 5)
        self.potential = self.add_default_value(potential, 6)
        self.theta = self.add_default_value(theta, 7)
        self.volume = self.add_default_value(volume, 8)
        self.wetness = self.add_default_value(wetness, 9)

        # Run checks
        self.check_inputs()

    def set_outputs(self):
        """
        Converts the wanted outputs into a dict

        :return: output dict.
        """

        output_dict = {'cell': [], 'layer': []}

        if self.evapo_trans:
            output_dict['cell'].append('evaporation')
            output_dict['cell'].append('transpiration')

        if self.surface_water_volume or self.surface_water_volume == 'init':
            output_dict['cell'].append('surface_water_volume')

        if self.surface_water_flux:
            output_dict['cell'].append('surface_water_flux')

        if self.heat_flux:
            output_dict['cell'].append('heat_flux')

        if self.three_d_flux:
            output_dict['layer'].append('volumetric_flux')

        if self.potential:
            output_dict['layer'].append('potential')

        if self.theta:
            output_dict['layer'].append('theta')

        if self.volume or self.volume == 'init':
            output_dict['layer'].append('volume')

        if self.wetness:
            output_dict['layer'].append('wetness')

        return output_dict

    def run(self):
        """
        In case all the checks have passed the component runs.
        set_outputs() are run and passed on with PassClass.
        """

        if self.checks:
            out_dict = self.set_outputs()
            self.output_dict = out_dict
            self.results = gh_misc.PassClass(out_dict, 'Outputs')


class CMFInlet(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'ConnectedCell',
                        'description': 'Cell to connect to. Default is set to first cell',
                        'access': 'item',
                        'default_value': 0},

                    1: {'name': 'ConnectedLayer',
                        'description': 'Layer of cell to connect to. 0 is surface water.\n'
                                       '1 is first layer of cell and so on.\n'
                                       'Default is set to 0 - surface water',
                        'access': 'item',
                        'default_value': 0},

                    2: {'name': 'InletFlux',
                        'description': 'If inlet, then set flux in m3/day',
                        'access': 'list',
                        'default_value': None},

                    3: {'name': 'TimeStep',
                        'description': 'Time step between each value in InletFlux. Time step is in hours -'
                                       ' e.g. 1/60 equals time steps of 1 min.\n'
                                       'Default is 1 hour.',
                        'access': 'item',
                        'default_value': 1}
                    }

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},

                    1: {'name': 'BoundaryCondition',
                        'description': 'Livestock Boundary Condition'}
                    }

        self.inputs = inputs()
        self.outputs = outputs()
        self.description = 'CMF Boundary connection'
        self.component_number = 23
        self.cell = None
        self.layer = None
        self.inlet_flux = None
        self.time_step = None
        self.checks = False
        self.results = None

    def check_inputs(self):
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        if self.inlet_flux:
            self.checks = True

    def config(self):
        """
        Generates the Grasshopper component.
        """

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, cell, layer, inlet_flux, time_step):
        """
        Gathers the inputs and checks them.

        :param cell:
        :param layer:
        :param inlet_flux:
        :param time_step:
        :return:
        """

        # Gather data
        self.cell = self.add_default_value(int(cell), 0)
        self.layer = self.add_default_value(int(layer), 1)
        self.inlet_flux = self.add_default_value(inlet_flux, 2)
        self.time_step = self.add_default_value(time_step, 3)

        # Run checks
        self.check_inputs()

    def set_inlet(self):
        """Constructs a dict with inlet information."""

        self.results = gh_misc.PassClass({'type': 'inlet',
                                          'cell': self.cell,
                                          'layer': self.layer,
                                          'inlet_flux': ','.join([str(elem)
                                                                  for elem in
                                                                  self.inlet_flux]),
                                          'time_step': self.time_step
                                          },
                                         'BoundaryCondition')

        pp = pprint.PrettyPrinter(indent=1, width=50)
        pp.pprint(self.results.c)

    def run(self):
        """
        In case all the checks have passed the component runs.
        It runs set_inlet().
        """

        if self.checks:
            self.set_inlet()


class CMFSolverSettings(GHComponent):
    """A component class that sets the solver settings for CMF Solve."""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: component.inputs('optional'),

                    1: {'name': 'AnalysisLength',
                        'description': 'Total length of the simulation.'
                                       'The input should be a list with two '
                                       'values. The first value is the '
                                       'numerical length e.g. 24.\n'
                                       'Second value is the time unit e.g. h '
                                       'for hour. The second option is '
                                       'optional and if not given'
                                       'the time unit is set to hours.\n'
                                       'The time unit has to be one of the '
                                       'following values:\n'
                                       'y - year\n'
                                       'd - day\n'
                                       'h - hour\n'
                                       'm - minute\n'
                                       's - second\n'
                                       'Default is set to 24 hours.',
                        'access': 'list',
                        'default_value': None},

                    2: {'name': 'TimeStep',
                        'description': 'Size of each simulation time step.'
                                       'The input should be a list with two '
                                       'values. The first value is the '
                                       'numerical length e.g. 24.\n'
                                       'Second value is the time unit e.g. h '
                                       'for hour. The second option is '
                                       'optional and if not given'
                                       'the time unit is set to hours.\n'
                                       'The time unit has to be one of the '
                                       'following values:\n'
                                       'y - year\n'
                                       'd - day\n'
                                       'h - hour\n'
                                       'm - minute\n'
                                       's - second\n'
                                       'Default is 1 hour',
                        'access': 'list',
                        'default_value': None},

                    3: {'name': 'StartTime',
                        'description': 'Sets the start time for the '
                                       'simulation.\n'
                                       'The input should be a list with three '
                                       'values. The first value is the day. '
                                       'Second value is the month. '
                                       'Third value is the year.\n'
                                       'All values should be integers and they '
                                       'all start from 1.\n'
                                       'Default is 01-01-[current year]',
                        'access': 'list',
                        'default_value': [1, 1, datetime.datetime.now().year]},

                    4: {'name': 'SolverTolerance',
                        'description': 'Solver tolerance\nDefault is 1e-8',
                        'access': 'item',
                        'default_value': None},
                    }

        def outputs():
            return {0: component.outputs('readme'),

                    1: {'name': 'ChosenSolverSettings',
                        'description': 'Shows the chosen solver settings'},

                    2: {'name': 'SolverSettings',
                        'description': 'Livestock Solver Settings'}}

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 21
        self.description = 'Sets the solver settings for CMF Solve'
        self.checks = [False, False, False, False]
        self.results = None

        # Data Parameters
        self.length = None
        self.time_step = None
        self.tolerance = None
        self.start_time = None
        self.settings = None
        self.settings_dict = None

    def check_inputs(self):
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, length, time_step, start_time, tolerance):
        """
        Gathers the inputs and checks them.

        :param length: Number of time steps to be taken.
        :param time_step: Size of time step.
        :param tolerance: Solver tolerance.
        :param start_time: Solver start time.
        """

        # Gather data
        self.length = self.add_default_value(length, 1)
        self.time_step = self.add_default_value(time_step, 2)
        self.start_time = self.add_default_value(start_time, 3)
        self.tolerance = self.add_default_value(tolerance, 4)
        self.modified_settings()

        # Run checks
        self.check_inputs()

    def modified_settings(self):

        if self.length:
            if len(self.length) == 1:
                self.length[0] = int(self.length[0])
                self.length.append('h')

            elif len(self.length) == 2:
                self.length[0] = int(self.length[0])

        if self.time_step:
            if len(self.time_step) == 1:
                self.time_step[0] = int(self.time_step[0])
                self.time_step.append('h')

            elif len(self.time_step) == 2:
                self.time_step[0] = int(self.time_step[0])

        self.start_time = {'day': int(self.start_time[0]),
                           'month': int(self.start_time[1]),
                           'year': int(self.start_time[2])}

        self.settings = {'analysis_length': self.length,
                         'time_step': self.time_step,
                         'start_time': self.start_time,
                         'tolerance': self.tolerance
                         }

    def run(self):
        """
        In case all the checks have passed the component runs.
        Constructs a solver settings dict, prints it and passes it on with
        PassClass.
        """

        if self.checks:
            self.settings_dict = cmf_lib.default_solver_settings(self.settings)
            self.results = gh_misc.PassClass(self.settings_dict,
                                             'SolverSettings')


class CMFSurfaceFluxResult(GHComponent):
    """A component class that visualizes the surface fluxes from a CMF case."""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'ResultFolder',
                        'description': 'Path to result folder. Accepts output from Livestock Solve',
                        'access': 'item',
                        'default_value': None},

                    1: {'name': 'Mesh',
                        'description': 'Mesh of the case',
                        'access': 'item',
                        'default_value': None},

                    2: {'name': 'IncludeRunOff',
                        'description': 'Include surface run-off into the surface flux vector? '
                                       '\nDefault is set to True',
                        'access': 'item',
                        'default_value': True},

                    3: {'name': 'IncludeRain',
                        'description': 'Include rain into the surface flux vector?'
                                       '\nDefault is False.',
                        'access': 'item',
                        'default_value': False},

                    4: {'name': 'IncludeEvapotranspiration',
                        'description': 'Include evapotranspiration into the surface flux vector? '
                                       '\nDefault is set to False',
                        'access': 'item',
                        'default_value': False},

                    5: {'name': 'IncludeInfiltration',
                        'description': 'Include infiltration into the surface flux vector? '
                                       '\nDefault is set to False',
                        'access': 'item',
                        'default_value': False},

                    6: {'name': 'SaveResult',
                        'description': 'Save the values as a text file - Default is set to False',
                        'access': 'item',
                        'default_value': False},

                    7: {'name': 'Write',
                        'description': 'Write component files',
                        'access': 'item',
                        'default_value': False},

                    8: {'name': 'Run',
                        'description': 'Run component',
                        'access': 'item',
                        'default_value': False}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},

                    1: {'name': 'Unit',
                        'description': 'Shows the units of the results'},

                    2: {'name': 'SurfaceFluxVectors',
                        'description': 'Tree with the surface flux vectors'},

                    3: {'name': 'CSVPath',
                        'description': 'Path to csv file.'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 25
        self.description = 'Visualize the surface fluxes from a CMF case.'
        self.unit = 'm3/day'
        self.mesh = None
        self.path = None
        self.run_off = None
        self.rain = None
        self.evapo = None
        self.infiltration = None
        self.save_result = None
        self.write_files = None
        self.run_component = None
        self.py_exe = gh_misc.get_python_exe()
        self.checks = False
        self.results = None
        self.result_path = None

    def check_inputs(self):
        """Checks inputs and raises a warning if an input is not the correct type."""

        if self.path:
            self.checks = True
        else:
            warning = 'Insert result path'
            self.add_warning(warning)

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, path, mesh, run_off, rain, evapo, infiltration, save,
                   write, run):
        """
        Gathers the inputs and checks them.

        :param path: Path for result file.
        :param mesh: Case mesh
        :param run_off: Whether to include run-off or not.
        :param rain: Whether to include rain or not.
        :param evapo: Whether to include evapotranspiration or not.
        :param infiltration: Whether to include infiltration or not.
        :param save: Save result to file or not
        :param write: Write component files or not
        :param run: Run component or not.
        """

        # Gather data
        self.path = path
        self.mesh = mesh
        self.run_off = self.add_default_value(run_off, 2)
        self.rain = self.add_default_value(rain, 3)
        self.evapo = self.add_default_value(evapo, 4)
        self.infiltration = self.add_default_value(infiltration, 5)
        self.save_result = self.add_default_value(save, 6)
        self.write_files = self.add_default_value(write, 7)
        self.run_component = self.add_default_value(run, 8)
        self.result_path = self.path + '/surface_flux_result.txt'

        # Run checks
        self.check_inputs()

    def run_template(self):
        """Spawns a subprocess that runs the template."""

        # Run template
        thread = subprocess.Popen(
            [self.py_exe, self.path + '/cmf_surface_results_template.py'])
        thread.wait()
        thread.kill()

    def write(self):
        """Writes the wanted information from the mesh and the flux configurations."""

        # helper functions
        def process_mesh(mesh_, path_):
            points = rs.MeshFaceCenters(mesh_)

            point_obj = open(path_ + '/center_points.txt', 'w')
            for point in points:
                point_obj.write(','.join(str(element)
                                         for element in point) + '\n'
                                )

            point_obj.close()

            return True

        def flux_config(path_, run_off, rain, evapo, infiltration):
            flux_obj = open(path_ + '/flux_config.txt', 'w')
            flux_obj.write(str(run_off) + '\n')
            flux_obj.write(str(rain) + '\n')
            flux_obj.write(str(evapo) + '\n')
            flux_obj.write(str(infiltration) + '\n')
            flux_obj.close()

            return True

        process_mesh(self.mesh, self.path)
        flux_config(self.path, self.run_off, self.rain, self.evapo,
                    self.infiltration)
        # Write template
        pick_template('cmf_surface_results', self.path)

        return True

    def load_result(self):
        """Loads the results."""

        # Helper functions
        def convert_file_to_points(file_lines):
            point_list = []
            for line_ in file_lines:
                point_list.append(convert_line_to_points(line_.strip()))

            return point_list

        def convert_line_to_points(line_):
            points_ = []
            for element in line_.split('\t'):
                x, y, z = element.split(',')
                points_.append(rg.Point3d(float(x), float(y), float(z)))

            return points_

        result_obj = open(self.result_path, 'r')
        result_lines = result_obj.readlines()
        results = convert_file_to_points(result_lines)
        result_obj.close()

        return results

    def delete_files(self):
        """Deletes the helper files."""

        if os.path.exists(self.path + '/flux_config.txt'):
            os.remove(self.path + '/flux_config.txt')

        if os.path.exists(self.path + '/center_points.txt'):
            os.remove(self.path + '/center_points.txt')

        if os.path.exists(self.path + '/cmf_surface_results_template.py'):
            os.remove(self.path + '/cmf_surface_results_template.py')

        if not self.save_result:
            os.remove(self.result_path)

    def run(self):
        """
        | In case all the checks have passed and Write is True the component writes the component files.
        | In case all the checks have passed the component runs.
        | The following functions are run:
        | write()
        | run_template()
        | load_results()
        | delete_files()
        | The results are converted into a Grasshopper Tree structure.

        """

        if self.checks and self.write_files:
            self.write()

        if self.checks and self.run_component:
            self.run_template()
            self.results = gh_misc.list_to_tree(self.load_result())
            self.delete_files()


class CMFOutlet(GHComponent):
    """A component class that creates a CMF Outlet."""

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Location',
                        'description': 'Location of the outlet in x, y and z coordinates.\n'
                                       'Default is 0,0,0',
                        'access': 'item',
                        'default_value': [0, 0, 0]},

                    1: {'name': 'ConnectedCell',
                        'description': 'Cell to connect to.\n'
                                       'Default is set to first cell',
                        'access': 'item',
                        'default_value': 0},

                    2: {'name': 'ConnectedLayer',
                        'description': 'Layer of cell to connect to.\n'
                                       '0 is surface water.\n'
                                       '1 is first layer of cell and so on.\n'
                                       'Default is set to 0 - surface water',
                        'access': 'item',
                        'default_value': 0},

                    3: {'name': 'OutletType',
                        'description': 'Set type of outlet connection.\n'
                                       '1 - Richards.\n'
                                       '2 - Kinematic wave.\n'
                                       '3 - Technical Flux.',
                        'access': 'item',
                        'default_value': None},

                    4: {'name': 'ConnectionParameter',
                        'description': 'If Richards:\n'
                                       '    Potential - Sets the potential of the outlet. The difference in potential'
                                       ' is what drives the flux.\n'
                                       'If Kinematic wave:\n'
                                       '    Residence Time - Linear flow parameter of travel time in days.\n'
                                       'If Technical Flux:\n'
                                       '    Maximum Flux - The maximum flux is in m3/day.',
                        'access': 'item',
                        'default_value': None}

                    }

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},

                    1: {'name': 'BoundaryCondition',
                        'description': 'Livestock Boundary Condition'}
                    }

        self.inputs = inputs()
        self.outputs = outputs()
        self.description = 'Create a CMF Outlet'
        self.component_number = 29
        self.location = None
        self.cell = None
        self.layer = None
        self.outlet_type = None
        self.parameter = None
        self.checks = False
        self.results = None

    def check_inputs(self):
        """Checks inputs and raises a warning if an input is not the correct type."""

        if self.outlet_type and self.parameter:
            self.checks = True

    def config(self):
        """Generates the Grasshopper component."""

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, location, cell, layer, type_, type_parameter):
        """
        Gathers the inputs and checks them.

        :param location: Location of the cell
        :param cell: Cell to connect to. Default is set to first cell
        :param layer: Layer of cell to connect to. 0 is surface water.
        :param type_: Type of connection from CMF Outlet Type
        :param type_parameter: Parameter for the connection type.
        """

        # Gather data
        self.location = self.add_default_value(location, 0)
        self.cell = self.add_default_value(int(cell), 1)
        self.layer = self.add_default_value(int(layer), 2)
        self.outlet_type = self.add_default_value(type_, 3)
        self.parameter = self.add_default_value(type_parameter, 4)

        # Run checks
        self.check_inputs()

    def location_to_string(self):
        """
        Converts the location to a string.

        :return: The location as a comma separated string
        :rtype: str
        """

        if isinstance(self.location, str):
            return self.location

        else:
            location_string = ','.join([str(v)
                                        for v in self.location])
            return location_string

    def type_to_connection(self):
        if self.outlet_type == 1:
            return 'richards'

        elif self.outlet_type == 2:
            return 'kinematic_wave'

        elif self.outlet_type == 3:
            return 'technical_flux'

    def set_outlet_connection(self):
        """Constructs a dict with outlet information."""

        return {'connection': self.type_to_connection(),
                'connection_parameter': self.parameter}

    def set_outlet(self):
        """Constructs a dict with outlet information."""

        self.results = gh_misc.PassClass({'type': 'outlet',
                                          'location': self.location_to_string(),
                                          'cell': self.cell,
                                          'layer': self.layer,
                                          'outlet_type': self.set_outlet_connection(),
                                          },
                                         'BoundaryCondition')

        pp = pprint.PrettyPrinter(indent=1, width=50)
        pp.pprint(self.results.c)

    def run(self):
        """
        | In case all the checks have passed the component runs.
        | It runs set_outlet().

        """

        if self.checks:
            self.set_outlet()
