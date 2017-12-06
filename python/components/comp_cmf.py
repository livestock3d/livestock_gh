__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.1.0"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import os
import xml.etree.ElementTree as ET
import collections
import subprocess
from shutil import copyfile

# Livestock imports
import livestock.lib.ssh as ssh
import livestock.lib.geometry as gh_geo
import livestock.lib.livestock_csv as csv
from component import GHComponent
import livestock.lib.misc as gh_misc
from livestock.lib.templates import pick_template

# Grasshopper imports
import Rhino.Geometry as rg

# -------------------------------------------------------------------------------------------------------------------- #
# Classes


class CMFGround(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Layers',
                        'description': 'Soil layers to add to the mesh in m',
                        'access': 'list',
                        'default_value': 0},

                    1: {'name': 'RetentionCurve',
                        'description': 'Retention curve',
                        'access': 'item',
                        'default_value': None},

                    2: {'name': 'SurfaceProperties',
                        'description': 'Input from Livestock CMF SurfaceProperties',
                        'access': 'item',
                        'default_value': None},

                    3: {'name': 'SaturatedDepth',
                        'description': 'Initial saturated depth in m. It is depth where the groundwater is located'
                                       ' - Default is set to 3m',
                        'access': 'item',
                        'default_value': 3},

                    4: {'name': 'FaceIndices',
                        'description': 'List of face indices, on where the ground properties are applied.',
                        'access': 'list',
                        'default_value': None},

                    5: {'name': 'ETMethod',
                        'description': 'Set method to calculate evapotranspiration.\n'
                                       '0: Penman-Monteith\n'
                                       '1: Shuttleworth-Wallace\n'
                                       'Default is set to Shuttleworth-Wallace',
                        'access': 'item',
                        'default_value': 1}
                    }

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},
                    1: {'name': 'Ground',
                        'description': 'Livestock Ground Data Class'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 11
        self.description = 'Generates CMF ground'
        self.face_indices = None
        self.layers = None
        self.retention_curve = None
        self.surface_properties = None
        self.saturated_depth = None
        self.et_number = None
        self.checks = [False, False, False, False, False]
        self.results = None

    def check_inputs(self):
        warning = []

        if self.retention_curve:
            self.checks[2] = True
        else:
            warning.append('Retention curve is wrong!')

        if isinstance(self.saturated_depth, float):
            self.checks[4] = True
        else:
            warning.append('Initial saturation must be float! Input provided was: ' + str(self.saturated_depth))

        if self.face_indices:
            indices = []
            for index in self.face_indices:
                indices.append(int(float(index)))

            self.face_indices = indices

        if warning:
            if isinstance(warning, list):
                for w in warning:
                    print(w + '\n')
            else:
                print(warning)

            self.add_warning(warning)
        else:
            self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, layers, retention_curve, surface_properties, saturated_depth, face_indices, et_method):

        # Gather data
        self.layers = self.add_default_value(layers, 0)
        self.retention_curve = self.add_default_value(retention_curve, 1)
        self.surface_properties = self.add_default_value(surface_properties, 2)
        self.saturated_depth = self.add_default_value(saturated_depth, 3)
        self.face_indices = self.add_default_value(face_indices, 4)
        self.et_number = self.add_default_value(et_method, 5)

        # Run checks
        self.check_inputs()

    def convert_et_number_to_method(self):
        if self.et_number == 0:
            return 'penman_monteith'
        elif self.et_number == 1:
            return 'shuttleworth_wallace'
        else:
            w = 'ETMethod has to be 0 or 1. Input was: ' + str(self.et_number)
            self.add_warning(w)

    def run(self):
        if self.checks:
            ground_dict = {'face_indices': self.face_indices,
                           'layers': self.layers,
                           'retention_curve': self.retention_curve,
                           'surface_properties': self.surface_properties,
                           'saturated_depth': self.saturated_depth,
                           'et_method': self.convert_et_number_to_method()
                           }

            self.results = gh_misc.PassClass(ground_dict, 'Ground')


class CMFWeather(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Temperature',
                        'description': 'Temperature in C. Either a list or a tree where the number of branches is equal'
                                       ' to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},
                    1: {'name': 'WindSpeed',
                        'description': 'Wind speed in m/s. Either a list or a tree where the number of branches is'
                                       ' equal to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},
                    2: {'name': 'RelativeHumidity',
                        'description': 'Relative humidity in %. Either a list or a tree where the number of branches is'
                                       ' equal to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},
                    3: {'name': 'CloudCover',
                        'description': 'Cloud cover, unitless between 0 and 1. Either a list or a tree where the number'
                                       ' of branches is equal to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},
                    4: {'name': 'GlobalRadiation',
                        'description': 'Global Radiation in W/m2. Either a list or a tree where the number of branches'
                                       ' is equal to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},
                    5: {'name': 'Rain',
                        'description': 'Horizontal precipitation in mm/h. Either a list or a tree where the number of'
                                       ' branches is equal to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},
                    6: {'name': 'GroundTemperature',
                        'description': 'Ground temperature in C. Either a list or a tree where the number of branches'
                                       ' is equal to the number of mesh faces.',
                        'access': 'tree',
                        'default_value': None},
                    7: {'name': 'Location',
                        'description': 'A Ladybug Tools Location',
                        'access': 'item',
                        'default_value': None},
                    8: {'name': 'MeshFaceCount',
                        'description': 'Number of faces in the ground mesh',
                        'access': 'item',
                        'default_value': None}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},
                    1: {'name': 'Weather',
                        'description': 'Livestock Weather Data Class'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 12
        self.description = 'Generates CMF weather'
        self.temp = None
        self.wind = None
        self.rel_hum = None
        self.cloud_cover = None
        self.global_radiation = None
        self.rain = None
        self.ground_temp = None
        self.location = None
        self.face_count = None
        self.checks = [False, False, False, False, False, False, False, False]
        self.results = None

    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, temp, wind, rel_hum, cloud_cover, global_radiation, rain, ground_temp, location, face_count):

        # Gather data
        self.face_count = int(face_count)
        self.temp = self.match_cell_count(temp)
        self.wind = self.match_cell_count(wind)
        self.rel_hum = self.match_cell_count(rel_hum)
        self.cloud_cover = self.match_cell_count(cloud_cover)
        self.global_radiation = self.match_cell_count(global_radiation)
        self.rain = self.match_cell_count(rain)
        self.ground_temp = self.match_cell_count(ground_temp)
        self.location = location

        # Run checks
        self.check_inputs()

    def convert_cloud_cover(self):
        # Converts cloud cover to sun shine

        sun_shine = {}

        for cloud_key in self.cloud_cover.keys():
            sun_shine[cloud_key] = []
            for cc in self.cloud_cover[cloud_key]:
                sun_shine[cloud_key].append(1-float(cc))

        return sun_shine

    def convert_radiation_unit(self):
        # converts W/m2 to MJ/(m2*day)
        # 1 W/m2 => 60s*60min*24hours/10^6 => MJ/(m2*day)
        # 1 W/m2 = 0.0864 MJ/(m2*day)

        converted_radiation = {}

        for radiation_key in self.global_radiation.keys():
            converted_radiation[radiation_key] = []
            for rad in self.global_radiation[radiation_key]:
                converted_radiation[radiation_key].append(float(rad)*0.0864)

        self.global_radiation = converted_radiation

    def convert_rain_unit(self):
        # Converts rain from mm/h to mm/day
        # 1 mm/h = 24 mm/day

        converted_rain = {}

        for rain_key in self.rain.keys():
            converted_rain[rain_key] = []
            for rain in self.rain[rain_key]:
                converted_rain[rain_key].append(float(rain) * 24)

        self.rain = converted_rain

    def convert_location(self):
        location_name, lat, long_, time_zone, elevation = gh_misc.decompose_ladybug_location(self.location)
        return lat, long_, time_zone

    def match_cell_count(self, weather_parameter):

        def find_list(weather_list_):
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

        weather_list = gh_misc.tree_to_list(weather_parameter)
        clean_weather_list = find_list(weather_list)
        weather_dict = {}

        if len(clean_weather_list) == 1:
            weather_dict['all'] = clean_weather_list[0]

        elif len(weather_list) == self.face_count:
            for i in range(0, len(weather_list)):
                cell_number = 'cell_' + str(i)
                weather_dict[cell_number] = weather_list[i]

        return weather_dict

    def print_weather_lengths(self):

        def printer(parameter_name, parameter):
            print(str(parameter_name) + ' includes: ' + str(len(parameter.keys())) + ' lists')

        printer('Temperature', self.temp)
        printer('Wind Speed', self.wind)
        printer('Relative Humidity', self.rel_hum)
        printer('Sun Shine', self.cloud_cover)  # are converted from cloud cover to sun later, but have same length.
        printer('Global Radiation', self.global_radiation)
        printer('Rain', self.rain)
        printer('Ground Temperature', self.ground_temp)

    def run(self):
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


"""
class CMFStream(GHComponent):

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
        self.component_number = 13
        self.mid_curve = None
        self.cross_sections = None
        self.shape = []
        self.x = None
        self.y = None
        self.z = None
        self.lengths = None
        self.width = None
        self.slope_bank = None
        self.water_depth = None
        self.checks = [False, False]
        self.results = None

    def check_inputs(self, ghenv):
        warning = []

        if self.mid_curve:
            self.checks = True

    def config(self, ghenv):

        # Generate Component
        self.config_component(ghenv, self.component_number)

    def run_checks(self, ghenv, mid_curve, cross_sections):
        # Gather data
        self.mid_curve = mid_curve
        self.cross_sections = cross_sections

        # Run checks
        self.check_inputs(ghenv)

    def process_curves(self):

        def intersection_mid_cross_section_curves(cross_sections, mid_curve):

            # get cross section vertices and mid point and cross section intersections
            intersection_points = []
            cross_section_verts = []

            for crv in cross_sections:
                intersection_points.append(rs.CurveCurveIntersection(mid_curve, crv)[0][1])
                cross_section_verts.append(rs.PolylineVertices(crv))

            if len(cross_section_verts[0]) == 3:
                shape = 0 # triangular reach
                return intersection_points, cross_section_verts, shape
            elif len(cross_section_verts[0]) == 4:
                shape = 1 # rectangular reach
                return intersection_points, cross_section_verts, shape
            else:
                print('Error in shape')
                return None, None, None

        def get_mid_points(intersection_points):
            mid_points = []
            x = []
            y = []
            z = []

            for i in range(len(intersection_points)):
                pt = intersection_points[i] - intersection_points[i + 1]
                mid_points.append(pt)
                x.append(pt.X)
                y.append(pt.Y)
                z.append(pt.Z)

            return mid_points, x, y, z

        def sort_cross_section_verts(cross_section_verts, shape):
            if shape == 0:
                left = []
                right = []
                bottom = []
                for i in range(len(cross_section_verts)):
                    pass
            elif shape == 1:
                return
            else:
                print('Shape with value:', str(shape), 'not defined!')
                return None

        intersection_points, cross_section_verts, self.shape = intersection_mid_cross_section_curves(self.cross_sections, self.mid_curve)

        return None

    def run(self):
        if self.checks:
            ground_dict = {'mesh': self.mesh,
                           'layers': self.layers,
                           'retention_curve': self.retention_curve,
                           'grass': self.grass,
                           'initial_saturation': self.initial_saturation}

            self.results = gh_misc.PassClass(ground_dict, 'CMF_Ground')
"""


class CMFSurfaceProperties(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Property',
                        'description': '0-1 grasses. 2-6 soils',
                        'access': 'item',
                        'default_value': 0},

                    1: {'name': 'Manning',
                        'description': 'Set Manning roughness. '
                                       '\nIf not set CMF calculates it from the above given values.',
                        'access': 'item',
                        'default_value': None},

                    2: {'name': 'PuddleDepth',
                        'description': 'Set puddle depth. Puddle depth is the height were run-off begins.',
                        'access': 'item',
                        'default_value': 0.01}
                    }

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},

                    1: {'name': 'Units',
                        'description': 'Shows the units of the surface values'},

                    2: {'name': 'SurfaceValues',
                        'description': 'Chosen surface properties values'},

                    3: {'name': 'SurfaceProperties',
                        'description': 'Livestock surface properties data'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 13
        self.description = 'Generates CMF Surface Properties'
        self.data = None
        self.units = None
        self.data_path = os.getenv('APPDATA') + r'\McNeel\Rhinoceros\5.0\scripts\livestock\data\surfaceData.csv'
        self.property_index = None
        self.manning = None
        self.puddle = None
        self.property = None
        self.checks = False
        self.results = None

    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, property_, manning_, puddle):

        # Gather data
        self.property_index = self.add_default_value(int(property_), 0)
        self.manning = self.add_default_value(manning_, 1)
        self.puddle = self.add_default_value(puddle, 2)

        # Run checks
        self.check_inputs()

    def load_csv(self):

        load = csv.read_csv(self.data_path)
        self.units = load[0]
        self.data = load[1]

    def pick_property(self):
        self.load_csv()
        data_list = self.data[self.property_index]
        self.property = collections.OrderedDict([('name', data_list[0]),
                                                 ('height', data_list[1]),
                                                 ('lai', data_list[2]),
                                                 ('albedo', data_list[3]),
                                                 ('canopy_closure', data_list[4]),
                                                 ('canopy_par', data_list[5]),
                                                 ('canopy_capacity', data_list[6]),
                                                 ('stomatal_res', data_list[7]),
                                                 ('root_depth', data_list[8]),
                                                 ('root_fraction', data_list[9]),
                                                 ('leaf_width', 0.005),
                                                 ('manning', self.manning),
                                                 ('puddle_depth', self.puddle)
                                                 ])

    def run(self):
        if self.checks:
            self.pick_property()

            self.results = gh_misc.PassClass(self.property, 'SurfaceProperty')


class CMFSyntheticTree(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'FaceIndex',
                        'description': 'Mesh face index where tree is placed',
                        'access': 'item',
                        'default_value': None},
                    1: {'name': 'TreeType',
                        'description': 'Tree types: 0 - Deciduous, 1 - Coniferous, 2 - Shrubs. Default is deciduous',
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
        if self.height:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            self.add_warning(warning)

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, face_index, tree_type, height):

        # Gather data
        self.face_index = self.add_default_value(int(face_index), 0)
        self.tree_type = self.add_default_value(int(tree_type), 1)
        self.height = self.add_default_value(height, 2)

        # Run checks
        self.check_inputs()

    def load_csv(self):

        load = csv.read_csv(self.data_path[self.tree_type])
        self.units = load[0]
        self.data = load[1]

    def compute_tree(self):
        self.load_csv()
        self.property = collections.OrderedDict([('name', 'Synthetic Deciduous'),
                                                 ('height', self.height),
                                                 ('lai', float(self.data[0][2]) * self.height + float(self.data[1][2])),
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
        if self.checks:
            self.compute_tree()
            dic = {'face_index': self.face_index,
                   'property': self.property}

            self.results = gh_misc.PassClass(dic, 'SyntheticTreeProperty')


class CMFRetentionCurve(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'SoilIndex',
                        'description': 'Index for choosing soil type. Index from 0-4',
                        'access': 'item',
                        'default_value': 0}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},
                    1: {'name': 'Units',
                        'description': 'Shows the units of the curve values'},
                    2: {'name': 'CurveValues',
                        'description': 'Chosen curve properties values'},
                    3: {'name': 'RetentionCurve',
                        'description': 'Livestock Retention Curve'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 15
        self.description = 'Generates retention curve'
        self.data = None
        self.units = None
        self.data_path = os.getenv('APPDATA') + r'\McNeel\Rhinoceros\5.0\scripts\livestock\data\soilData.csv'
        self.property = None
        self.soil_index = None
        self.checks = False
        self.results = None

    def check_inputs(self):
        if isinstance(self.soil_index, int):
            self.checks = True
        else:
            warning = 'soilIndex should be an integer'
            self.add_warning(warning)

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, soil_index):

        # Gather data
        self.soil_index = self.add_default_value(int(soil_index), 0)

        # Run checks
        self.check_inputs()

    def load_csv(self):

        load = csv.read_csv(self.data_path)
        self.units = load[0]
        self.data = load[1]

    def load_retention_curve(self):
        self.load_csv()
        self.property = collections.OrderedDict([('type', str(self.data[self.soil_index][0])),
                                                 ('K_sat', float(self.data[self.soil_index][1])),
                                                 ('phi', float(self.data[self.soil_index][2])),
                                                 ('alpha', float(self.data[self.soil_index][3])),
                                                 ('n', float(self.data[self.soil_index][4])),
                                                 ('m', float(self.data[self.soil_index][5])),
                                                 ('l', float(self.data[self.soil_index][6]))
                                                 ])

    def run(self):
        if self.checks:
            self.load_retention_curve()
            self.results = gh_misc.PassClass(self.property, 'RetentionCurve')


class CMFSolve(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Mesh',
                        'description': 'Topography as a mesh',
                        'access': 'item',
                        'default_value': None},

                    1: {'name': 'Ground',
                        'description': 'Input from Livestock CMF Ground',
                        'access': 'list',
                        'default_value': None},

                    2: {'name': 'Weather',
                        'description': 'Input from Livestock CMF Weather',
                        'access': 'item',
                        'default_value': None},

                    3: {'name': 'Trees',
                        'description': 'Input from Livestock CMF Tree',
                        'access': 'list',
                        'default_value': None},

                    4: {'name': 'Stream',
                        'description': 'Input from Livestock CMF Stream',
                        'access': 'item',
                        'default_value': None},

                    5: {'name': 'BoundaryConditions',
                        'description': 'Input from Livestock CMF Boundary Condition',
                        'access': 'list',
                        'default_value': None},

                    6: {'name': 'SolverSettings',
                        'description': 'Input from Livestock CMF Solver Settings',
                        'access': 'item',
                        'default_value': None},

                    7: {'name': 'Folder',
                        'description': 'Path to folder. Default is Desktop',
                        'access': 'item',
                        'default_value': os.path.join(os.environ["HOMEPATH"], "Desktop")},

                    8: {'name': 'CaseName',
                        'description': 'Case name as string. Default is CMF',
                        'access': 'item',
                        'default_value': 'CMF'},

                    9: {'name': 'Outputs',
                        'description': 'Connect Livestock Outputs',
                        'access': 'item',
                        'default_value': None},

                    10: {'name': 'Write',
                         'description': 'Boolean to write files',
                         'access': 'item',
                         'default_value': False},

                    11: {'name': 'Overwrite',
                         'description': 'If True excising case will be overwritten. Default is set to True',
                         'access': 'item',
                         'default_value': True},

                    12: {'name': 'Run',
                         'description': 'Boolean to run analysis'
                         '\nAnalysis will be ran through SSH. Configure the connection with Livestock SSH',
                         'access': 'item',
                         'default_value': False}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},

                    1: {'name': 'ResultPath',
                        'description': 'Path to result files'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 14
        self.description = 'Solves CMF Case'
        self.mesh = None
        self.ground = None
        self.weather = None
        self.trees = None
        self.stream = None
        self.boundary_conditions = None
        self.solver_settings = None
        self.folder = None
        self.case_name = None
        self.case_path = None
        self.write_case = None
        self.overwrite = True
        self.output_config = None
        self.run_case = None
        self.py_exe = gh_misc.get_python_exe()
        self.written = False
        self.checks = False
        self.results = None

    def check_inputs(self):
        if self.ground:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            self.add_warning(warning)

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, mesh, ground, weather, trees, stream, boundary_conditions, solver_settings, folder, name,
                   outputs, write, overwrite, run):

        # Gather data
        self.mesh = self.add_default_value(mesh, 0)
        self.ground = self.add_default_value(ground, 1)
        self.weather = self.add_default_value(weather, 2)
        self.trees = self.add_default_value(trees, 3)
        self.stream = self.add_default_value(stream, 4)
        self.boundary_conditions = self.add_default_value(boundary_conditions, 5)
        self.solver_settings = self.add_default_value(solver_settings, 6)
        self.folder = self.add_default_value(folder, 7)
        self.case_name = self.add_default_value(name, 8)
        self.output_config = self.add_default_value(outputs, 9)
        self.write_case = self.add_default_value(write, 10)
        self.overwrite = self.add_default_value(overwrite, 11)
        self.run_case = self.add_default_value(run, 12)
        self.update_case_path()

        # Run checks
        self.check_inputs()

    def update_case_path(self):
        self.case_path = self.folder + '\\' + self.case_name

    def write(self, doc):

        # Helper functions
        def write_weather(weather_dict_, folder):
            weather_dict = weather_dict_.c
            weather_root = ET.Element('weather')
            weather_keys = weather_dict.keys()

            for k in weather_keys:
                data = ET.SubElement(weather_root, str(k))
                data.text = str(weather_dict[str(k)])

            weather_tree = ET.ElementTree(weather_root)
            weather_file = 'weather.xml'
            weather_tree.write(folder + '/' + weather_file, xml_declaration=True)

            return weather_file

        def write_ground(ground_dict_, folder):
            # Process ground
            ground_dict = list(ground.c for ground in ground_dict_)
            ground_root = ET.Element('ground')

            for i in range(0, len(ground_dict)):
                ground = ET.SubElement(ground_root, 'ground_%i' % i)
                g_keys = ground_dict[i].keys()

                for g in g_keys:
                    data = ET.SubElement(ground, str(g))
                    try:
                        data_to_write = ground_dict[i][str(g)].c
                        data.text = str(dict(data_to_write))
                    except:
                        data.text = str(ground_dict[i][str(g)])

            ground_tree = ET.ElementTree(ground_root)
            ground_file = 'ground.xml'
            ground_tree.write(folder + '/' + ground_file, xml_declaration=True)

            return ground_file

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

            files_written.append(tree_file)

        def write_outputs(output_dict_, folder):
            # Process outputs
            output_dict = output_dict_.c
            output_root = ET.Element('output')

            for out_key in output_dict.keys():
                data = ET.SubElement(output_root, str(out_key))
                data.text = str(output_dict[out_key])

            output_tree = ET.ElementTree(output_root)
            output_file = 'outputs.xml'
            output_tree.write(folder + '/' + output_file, xml_declaration=True)

            return output_file

        def write_stream(stream_dict_, folder):
            pass

        def write_boundary_conditions(boundary_dict_, folder):
            # Process boundary conditions
            boundary_conditions_dict = list(bc.c for bc in boundary_dict_)
            boundary_conditions_root = ET.Element('boundary_conditions')

            for i in range(0, len(boundary_conditions_dict)):
                boundary_condition = ET.SubElement(boundary_conditions_root, 'boundary_condition_%i' % i)

                bc_type = ET.SubElement(boundary_condition, 'type')
                bc_type.text = str(boundary_conditions_dict[i]['type'])

                bc_cell = ET.SubElement(boundary_condition, 'cell')
                bc_cell.text = str(boundary_conditions_dict[i]['cell'])

                bc_layer = ET.SubElement(boundary_condition, 'layer')
                bc_layer.text = str(boundary_conditions_dict[i]['layer'])

                if boundary_conditions_dict[i]['type'] == 'inlet':
                    bc_flux = ET.SubElement(boundary_condition, 'flux')
                    bc_flux.text = str(boundary_conditions_dict[i]['flux'])

                elif boundary_conditions_dict[i]['type'] == 'outlet':
                    bc_flux = ET.SubElement(boundary_condition, 'flow_width')
                    bc_flux.text = str(boundary_conditions_dict[i]['flow_width'])

                    bc_flux = ET.SubElement(boundary_condition, 'location')
                    bc_flux.text = str(boundary_conditions_dict[i]['location'])

            boundary_conditions_tree = ET.ElementTree(boundary_conditions_root)
            boundary_condition_file = 'boundary_condition.xml'
            boundary_conditions_tree.write(folder + '/' + boundary_condition_file, xml_declaration=True)

            return boundary_condition_file

        def write_solver_info(solver_dict_, folder):
            # Process solver info
            solver_root = ET.Element('solver')
            solver_dict = solver_dict_.c

            for solver_key in solver_dict.keys():
                data = ET.SubElement(solver_root, str(solver_key))
                data.text = str(solver_dict[solver_key])

            solver_tree = ET.ElementTree(solver_root)
            solver_file = 'solver.xml'
            solver_tree.write(folder + '/' + solver_file, xml_declaration=True)

            return solver_file

        def write_ssh_files(files_written_):
            # Clean SSH folder
            ssh.clean_ssh_folder()

            # SSH commands
            ssh_command = ssh.get_ssh()

            file_transfer = files_written_
            file_run = ['cmf_template.py']
            file_return = ['results.xml']

            ssh_command['file_transfer'] = ','.join(file_transfer) + ',cmf_template.py'
            ssh_command['file_run'] = ','.join(file_run)
            ssh_command['file_return'] = ','.join(file_return)
            ssh_command['template'] = 'cmf'

            ssh.write_ssh_commands(ssh_command)

            return ssh_command

        # check if folder exists
        if os.path.exists(self.case_path):
            self.written = True
        else:
            os.mkdir(self.folder + '/' + self.case_name)

        files_written = []

        # Save Mesh
        gh_geo.bake_export_delete(self.mesh, self.case_path, 'mesh', '.obj', doc)

        # Append to files written
        files_written.append('mesh.obj')
        files_written.append(write_weather(self.weather, self.case_path))
        files_written.append(write_ground(self.ground, self.case_path))
        files_written.append(write_outputs(self.output_config, self.case_path))
        files_written.append(write_solver_info(self.solver_settings, self.case_path))

        if self.trees:
            files_written.append(write_trees(self.trees, self.case_path))

        if self.boundary_conditions:
            files_written.append(write_boundary_conditions(self.boundary_conditions, self.case_path))

        if self.stream:
            files_written.append(write_stream(self.stream, self.case_path))

        # template
        pick_template('cmf', self.case_path)

        # ssh
        ssh_cmd = write_ssh_files(files_written)
        self.written = True

        return ssh_cmd

    def do_case(self, ssh_cmd_):

        ssh_template = ssh.ssh_path + '/ssh_template.py'
        transfer_files = ssh_cmd_['file_transfer'].split(',')

        # Copy files from case folder to ssh folder
        for file_ in transfer_files:
            copyfile(self.case_path + '/' + file_, ssh.ssh_path + '/' + file_)

        # Run template
        thread = subprocess.Popen([self.py_exe, ssh_template])
        thread.wait()
        thread.kill()

    def check_results(self):
        ssh_result = ssh.ssh_path + '/results.xml'
        result_path = self.case_path + '/results.xml'

        if os.path.exists(ssh_result):
            copyfile(ssh_result, result_path)
            ssh.clean_ssh_folder()
            return result_path

        else:
            warning = 'Could not find result file. Unknown error occurred'
            self.add_warning(warning)

    def run(self, doc):
        if self.checks and self.run_case:
            ssh_cmd = self.write(doc)
            self.do_case(ssh_cmd)
            self.results = self.check_results()

        elif self.checks and self.write_case:
            self.write(doc)


class CMFResults(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'ResultFilePath',
                        'description': 'Path to result file. Accepts output from Livestock Solve',
                        'access': 'item',
                        'default_value': None},
                    1: {'name': 'FetchResult',
                        'description': 'Choose which result should be loaded:'
                                       '\n0 - Evapotranspiration'
                                       '\n1 - Surface water volume'
                                       '\n2 - Surface water flux'
                                       '\n3 - Heat flux'
                                       '\n4 - Aerodynamic resistance'
                                       '\n5 - Soil layer water flux'
                                       '\n6 - Soil layer potential'
                                       '\n7 - Soil layer theta'
                                       '\n8 - Soil layer volume'
                                       '\n9 - Soil layer wetness',
                        'access': 'item',
                        'default_value': 0},
                    2: {'name': 'SaveCSV',
                        'description': 'Save the values as a csv file - Default is set to False',
                        'access': 'item',
                        'default_value': False},
                    3: {'name': 'Run',
                        'description': 'Run component',
                        'access': 'item',
                        'default_value': False}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},
                    1: {'name': 'Units',
                        'description': 'Shows the units of the results'},
                    2: {'name': 'Values',
                        'description': 'List with chosen result values'},
                    3: {'name': 'CSVPath',
                        'description': 'Path to csv file.'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 17
        self.unit = None
        self.path = None
        self.fetch_result = None
        self.save_csv = None
        self.run_component = None
        self.py_exe = gh_misc.get_python_exe()
        self.checks = False
        self.results = None

    def check_inputs(self):
        if self.path:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            self.add_warning(warning)

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, path, fetch_result, save, run):

        # Gather data
        self.path = path
        self.fetch_result = int(self.add_default_value(fetch_result, 1))
        self.save_csv = self.add_default_value(save, 2)
        self.run_component = self.add_default_value(run, 3)

        # Run checks
        self.check_inputs()

    def process_xml(self):
        possible_results = ['evapotranspiration', 'surface_water_volume', 'surface_water_flux',
                            'heat_flux', 'aerodynamic_resistance', 'volumetric_flux', 'potential',
                            'theta', 'volume', 'wetness']

        # Write lookup file
        if 0 <= self.fetch_result <= 4:
            out = {'cell': possible_results[self.fetch_result]}
            gh_misc.write_file(str(out), self.path, 'result_lookup')
        else:
            out = {'layer': possible_results[self.fetch_result]}
            gh_misc.write_file(str(out), self.path, 'result_lookup')

        # Write template
        pick_template('cmf_results', self.path)

        # Run template
        thread = subprocess.Popen([self.py_exe, self.path + '/cmf_results_template.py'])
        thread.wait()
        thread.kill()

        # Construct csv path
        csv_path = self.path + '/' + str(possible_results[self.fetch_result]) + '.csv'

        return csv_path

    def load_result_csv(self, path):

        def convert_file_to_points(csv_file):
            point_list = []
            for line_ in csv_file:
                point_list.append(convert_line_to_points(line_))

            return point_list

        def convert_line_to_points(line_):
            points_ = []
            for element in line_:
                x, y, z = element.split(' ')
                points_.append(rg.Point3d(float(x), float(y), float(z)))

            return points_

        if self.fetch_result == 2:
                # fetch_result 2 contains points
                csv_obj = csv.read_csv(path, False)
                return convert_file_to_points(csv_obj)

        elif 0 <= self.fetch_result <= 4:
            return csv.read_csv(path, False)

        elif self.fetch_result == 5:
            # fetch 5 contains points
            csv_obj = csv.read_csv(path, False)
            results = []
            cell_result = []
            for line in csv_obj:
                if line[0].startswith('cell'):
                    results.append(cell_result)
                    cell_result = []
                else:
                    cell_result.append(convert_line_to_points(line))

            return results

        else:
            csv_obj = csv.read_csv(path, False)
            results = []
            cell_result = []
            for line in csv_obj:
                if line[0].startswith('cell'):
                    results.append(cell_result)
                    cell_result = []
                else:
                    cell_result.append(line)

            return results

    def delete_files(self, csv_path):
        os.remove(self.path + '/cmf_results_template.py')
        os.remove(self.path + '/result_lookup.txt')

        if not self.save_csv:
            os.remove(csv_path)

    def set_units(self):

        if self.fetch_result == 0:
            # evapotranspiration
            self.unit = 'm3/day'

        elif self.fetch_result == 1:
            # surface_water_volume
            self.unit = 'm3'

        elif self.fetch_result == 2:
            # surface_water_flux
            self.unit = 'm3/day'

        elif self.fetch_result == 3:
            # heat_flux
            self.unit = 'W/m2'

        elif self.fetch_result == 4:
            # aerodynamic_resistance
            self.unit = 's/m'

        elif self.fetch_result == 5:
            # volumetric_flux
            self.unit = 'm3/day'

        elif self.fetch_result == 6:
            # potential
            self.unit = 'm'

        elif self.fetch_result == 7:
            # theta
            self.unit = 'm3'

        elif self.fetch_result == 8:
            # volume
            self.unit = 'm3'

        elif self.fetch_result == 9:
            # wetness
            self.unit = '-'

    def run(self):
        if self.checks and self.run_component:

            self.set_units()
            csv_file_path = self.process_xml()
            results = self.load_result_csv(csv_file_path)
            self.delete_files(csv_file_path)

            self.results = gh_misc.list_to_tree(results)


class CMFOutputs(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Evapotranspiration',
                        'description': 'Cell evaporation - default is set to True',
                        'access': 'item',
                        'default_value': True},
                    1: {'name': 'SurfaceWaterVolume',
                        'description': 'Cell surface water - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    2: {'name': 'SurfaceWaterFlux',
                        'description': 'Cell surface water flux - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    3: {'name': 'HeatFlux',
                        'description': 'Cell surface heat flux - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    4: {'name': 'AerodynamicResistance',
                        'description': 'Cell aerodynamic resistance - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    5: {'name': 'VolumetricFlux',
                        'description': 'Soil layer volumetric flux vectors - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    6: {'name': 'Potential',
                        'description': 'Soil layer total potential (Psi_tot = Psi_M + Psi_G - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    7: {'name': 'Theta',
                        'description': 'Soil layer volumetric water content of the layer - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    8: {'name': 'Volume',
                        'description': 'Soil layer volume of water in the layer - default is set to True',
                        'access': 'item',
                        'default_value': True},
                    9: {'name': 'Wetness',
                        'description': 'Soil layer wetness of the soil (V_volume/V_pores) - default is set to False',
                        'access': 'item',
                        'default_value': False}
                    }

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},
                    1: {'name': 'ChosenOutputs',
                        'description': 'Shows the chosen outputs'},
                    2: {'name': 'Outputs',
                        'description': 'Livestock Output Data'}
                    }

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 16
        self.evapo_trans = None
        self.surface_water_volume = None
        self.surface_water_flux = None
        self.heat_flux = None
        self.aero_res = None
        self.three_d_flux = None
        self.potential = None
        self.theta = None
        self.volume = None
        self.wetness = None
        self.checks = False
        self.output_dict = None
        self.results = None

    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, evapo_trans, surface_water_volume, surface_water_flux, heat_flux, aero_res, three_d_flux,
                   potential, theta, volume, wetness):

        # Gather data
        self.evapo_trans = self.add_default_value(evapo_trans, 0)
        self.surface_water_volume = self.add_default_value(surface_water_volume, 1)
        self.surface_water_flux = self.add_default_value(surface_water_flux, 2)
        self.heat_flux = self.add_default_value(heat_flux, 3)
        self.aero_res = self.add_default_value(aero_res, 4)
        self.three_d_flux = self.add_default_value(three_d_flux, 5)
        self.potential = self.add_default_value(potential, 6)
        self.theta = self.add_default_value(theta, 7)
        self.volume = self.add_default_value(volume, 8)
        self.wetness = self.add_default_value(wetness, 9)

        # Run checks
        self.check_inputs()

    def set_outputs(self):

        output_dict = {'cell': [], 'layer': []}

        if self.evapo_trans:
            output_dict['cell'].append('evaporation')
            output_dict['cell'].append('transpiration')

        if self.surface_water_volume:
            output_dict['cell'].append('surface_water_volume')

        if self.surface_water_flux:
            output_dict['cell'].append('surface_water_flux')

        if self.heat_flux:
            output_dict['cell'].append('heat_flux')

        if self.aero_res:
            output_dict['cell'].append('aerodynamic_resistance')

        if self.three_d_flux:
            output_dict['layer'].append('volumetric_flux')

        if self.potential:
            output_dict['layer'].append('potential')

        if self.theta:
            output_dict['layer'].append('theta')

        if self.volume:
            output_dict['layer'].append('volume')

        if self.wetness:
            output_dict['layer'].append('wetness')

        return output_dict

    def run(self):
        if self.checks:
            out_dict = self.set_outputs()
            self.output_dict = out_dict
            self.results = gh_misc.PassClass(out_dict, 'Outputs')


class CMFBoundaryCondition(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'InletOrOutlet',
                        'description': '0 is inlet. 1 is outlet - default is set to 0',
                        'access': 'item',
                        'default_value': 0},

                    1: {'name': 'ConnectedCell',
                        'description': 'Cell to connect to. Default is set to first cell',
                        'access': 'item',
                        'default_value': 0},

                    2: {'name': 'ConnectedLayer',
                        'description': 'Layer of cell to connect to. 0 is surface water. '
                                       '1 is first layer of cell and so on. Default is set to 0 - surface water',
                        'access': 'item',
                        'default_value': 0},

                    3: {'name': 'InletFlux',
                        'description': 'If inlet, then set flux in m3/day',
                        'access': 'list',
                        'default_value': False},

                    4: {'name': 'FlowWidth',
                        'description': 'Width of the connection from cell to outlet in meters.',
                        'access': 'item',
                        'default_value': None},

                    5: {'name': 'OutletLocation',
                        'description': 'Location of the outlet in x, y and z coordinates.',
                        'access': 'list',
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
        self.description = 'CMF Boundary connection'
        self.component_number = 23
        self.inlet_or_outlet = None
        self.cell = None
        self.layer = None
        self.inlet_flux = None
        self.width = None
        self.location = None
        self.checks = False
        self.results = None

    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, inlet_outlet, cell, layer, inlet_flux, width, location):

        # Gather data
        self.inlet_or_outlet = self.add_default_value(int(inlet_outlet), 0)
        self.cell = self.add_default_value(int(cell), 1)
        self.layer = self.add_default_value(int(layer), 2)
        self.inlet_flux = self.add_default_value(inlet_flux, 3)
        self.width = width
        self.location = location

        # Run checks
        self.check_inputs()

    def set_inlet(self):
        self.results = gh_misc.PassClass({'type': 'inlet',
                                          'cell': self.cell,
                                          'layer': self.layer,
                                          'flux': ','.join(str(elem)
                                                           for elem in self.inlet_flux)
                                          },
                                         'BoundaryCondition')

    def set_outlet(self):
        self.results = gh_misc.PassClass({'type': 'outlet',
                                          'cell': self.cell,
                                          'layer': self.layer,
                                          'flow_width': self.width,
                                          'location': ','.join(str(elem)
                                                               for elem in self.location)
                                          },
                                         'BoundaryCondition')

    def run(self):
        if self.checks:
            if self.inlet_or_outlet == 0:
                self.set_inlet()
            elif self.inlet_or_outlet == 1:
                self.set_outlet()
            else:
                raise ValueError('InletOrOutlet has to be either 0 or 1. Value given was: ' + str(self.inlet_or_outlet))


class CMFSolverSettings(GHComponent):

        def __init__(self, ghenv):
            GHComponent.__init__(self, ghenv)

            def inputs():
                return {0: {'name': 'AnalysisLength',
                            'description': 'Number of time steps to be taken - Default is 24',
                            'access': 'item',
                            'default_value': 24},

                        1: {'name': 'TimeStep',
                            'description': 'Size of each time step in hours - e.g. 1/60 equals time steps of 1 min and'
                                           '\n24 is a time step of one day. '
                                           '\nDefault is 1 hour',
                            'access': 'item',
                            'default_value': 1},

                        2: {'name': 'SolverTolerance',
                            'description': 'Solver tolerance - Default is 1e-8',
                            'access': 'item',
                            'default_value': 10**-8},

                        3: {'name': 'Verbosity',
                            'description': 'Sets the verbosity of the print statement during runtime - Default is 1.\n'
                                           '0 - Prints only at start and end of simulation.\n'
                                           '1 - Prints at every time step.',
                            'access': 'item',
                            'default_value': 1}}

            def outputs():
                return {0: {'name': 'readMe!',
                            'description': 'In case of any errors, it will be shown here.'},

                        1: {'name': 'SolverSettings',
                            'description': 'Livestock Solver Settings'}}

            self.inputs = inputs()
            self.outputs = outputs()
            self.component_number = 21
            self.description = 'Sets the solver settings for CMF Solve'
            self.length = None
            self.time_step = None
            self.tolerance = None
            self.verbosity = None
            self.checks = [False, False, False, False]
            self.results = None

        def check_inputs(self):
            self.checks = True

        def config(self):
            # Generate Component
            self.config_component(self.component_number)

        def run_checks(self, length, time_step, tolerance, verbosity):
            # Gather data
            self.length = self.add_default_value(length, 0)
            self.time_step = self.add_default_value(time_step, 1)
            self.tolerance = self.add_default_value(tolerance, 2)
            self.verbosity = self.add_default_value(verbosity, 3)

            # Run checks
            self.check_inputs()

        def run(self):
            if self.checks:
                settings_dict = {'analysis_length': int(self.length),
                                 'time_step': float(self.time_step),
                                 'tolerance': self.tolerance,
                                 'verbosity': int(self.verbosity)}

                print(settings_dict.items())
                self.results = gh_misc.PassClass(settings_dict, 'SolverSettings')
