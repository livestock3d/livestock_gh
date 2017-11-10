__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import os
import xml.etree.ElementTree as ET
import collections
import subprocess
from shutil import copyfile

# Livestock imports
import gh.ssh as ssh
import gh.geometry as gh_geo
import lib.csv as csv
from comp.component import GHComponent
import gh.misc as gh_misc
from win.templates import pick_template

# Grasshopper imports
import rhinoscriptsyntax as rs

# -------------------------------------------------------------------------------------------------------------------- #
# Classes


class CMFGround(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Layers',
                        'description': 'Soil layers to add to the mesh in m',
                        'access': 'list',
                        'default_value': None},
                    1: {'name': 'RetentionCurve',
                        'description': 'Retention curve',
                        'access': 'item',
                        'default_value': None},
                    2: {'name': 'SurfaceProperties',
                        'description': 'Input from Livestock CMF SurfaceProperties',
                        'access': 'item',
                        'default_value': None},
                    3: {'name': 'InitialSaturation',
                        'description': 'Initial saturation of the soil layers',
                        'access': 'item',
                        'default_value': None},
                    4: {'name': 'FaceIndices',
                        'description': 'List of face indices, on where the ground properties are applied.',
                        'access': 'list',
                        'default_value': None}}

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
        self.initial_saturation = None
        self.checks = [False, False, False, False, False]
        self.results = None

    def check_inputs(self):
        warning = []

        if self.layers:
            self.checks[1] = True
        else:
            warning.append('Layer values must be float or list of floats! Input provided was: ' + str(self.layers))

        if self.retention_curve:
            self.checks[2] = True
        else:
            warning.append('Retention curve is wrong!')

        if isinstance(self.initial_saturation, float):
            self.checks[4] = True
        else:
            warning.append('Initial saturation must be float! Input provided was: ' + str(self.initial_saturation))

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

    def run_checks(self, layers, retention_curve, surface_properties, initial_saturation, face_indices):

        # Gather data
        self.layers = self.add_default_value(layers, 0)
        self.retention_curve = self.add_default_value(retention_curve, 1)
        self.surface_properties = self.add_default_value(surface_properties, 2)
        self.initial_saturation = self.add_default_value(initial_saturation, 3)
        self.face_indices = self.add_default_value(face_indices, 4)

        # Run checks
        self.check_inputs()

    def run(self):
        if self.checks:
            ground_dict = {'face_indices': self.face_indices,
                           'layers': self.layers,
                           'retention_curve': self.retention_curve,
                           'surface_properties': self.surface_properties,
                           'initial_saturation': self.initial_saturation}

            self.results = gh_misc.PassClass(ground_dict, 'Ground')


class CMFWeather(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Temperature',
                        'description': 'Temperature in C - List of floats',
                        'access': 'list',
                        'default_value': None},
                    1: {'name': 'WindSpeed',
                        'description': 'Wind speed in m/s - List of floats',
                        'access': 'list',
                        'default_value': None},
                    2: {'name': 'RelativeHumidity',
                        'description': 'Relative humidity in % - List of floats',
                        'access': 'list',
                        'default_value': None},
                    3: {'name': 'CloudCover',
                        'description': 'Cloud cover, unitless between 0 and 1 - list of floats',
                        'access': 'list',
                        'default_value': None},
                    4: {'name': 'GlobalRadiation',
                        'description': 'Global Radiation in MJ/(m^2*h) - list of floats',
                        'access': 'list',
                        'default_value': None},
                    5: {'name': 'Rain',
                        'description': 'Horizontal precipitation in mm/h - list of floats',
                        'access': 'list',
                        'default_value': None},
                    6: {'name': 'GroundTemperature',
                        'description': 'Ground temperature in C - list of floats',
                        'access': 'list',
                        'default_value': None},
                    7: {'name': 'Location',
                        'description': 'A Ladybug Tools Location',
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
        self.checks = [False, False, False, False, False, False, False, False]
        self.results = None

    def check_inputs(self):
        if self.temp:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            self.add_warning(warning)

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, temp, wind, rel_hum, cloud_cover, global_radiation, rain, ground_temp, location):

        # Gather data
        self.temp = temp
        self.wind = wind
        self.rel_hum = rel_hum
        self.cloud_cover = cloud_cover
        self.global_radiation = global_radiation
        self.rain = rain
        self.ground_temp = ground_temp
        self.location = location

        # Run checks
        self.check_inputs()

    def convert_cloud_cover(self):

        sun_shine = []
        for cc in self.cloud_cover:
            sun_shine.append(1-float(cc))

        return sun_shine

    def convert_location(self):
        location_name, lat, long, time_zone, elevation = gh_misc.decompose_ladybug_location(self.location)
        return lat, long, time_zone

    def run(self):
        if self.checks:

            sun = self.convert_cloud_cover()
            latitude, longitude, time_zone = self.convert_location()

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


class CMFSurfaceProperties(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Property',
                        'description': '0-1 grasses. 2-6 soils',
                        'access': 'item',
                        'default_value': 0}}

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
        self.data_path = r'C:\livestock\data\surfaceData.csv'
        self.property_index = None
        self.property = None
        self.checks = False
        self.results = None

    def check_inputs(self):
        if self.property_index:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            self.add_warning(warning)

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, property_):

        # Gather data
        self.property_index = self.add_default_value(int(property_), 0)

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
                                                 ('leaf_width', 0.005)
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
        self.data_path = [r'C:\livestock\data\syntheticDeciduous.csv', r'C:\livestock\data\syntheticConiferous.csv',
                          r'C:\livestock\data\syntheticShrubs.csv']
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
                        'description': 'Index for chosing soil type',
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
        self.data_path = r'C:\livestock\data\soilData.csv'
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
                        'description': 'Input from Livestock CMF_Ground',
                        'access': 'list',
                        'default_value': None},
                    2: {'name': 'Weather',
                        'description': 'Input from Livestock CMF_Weather',
                        'access': 'item',
                        'default_value': None},
                    3: {'name': 'Trees',
                        'description': 'Input from Livestock CMF_Tree',
                        'access': 'list',
                        'default_value': None},
                    4: {'name': 'Stream',
                        'description': 'Input from Livestock CMF_Stream',
                        'access': 'item',
                        'default_value': None},
                    5: {'name': 'BoundaryConditions',
                        'description': 'Input from Livestock CMF_BoundaryCondition',
                        'access': 'list',
                        'default_value': None},
                    6: {'name': 'AnalysisLength',
                        'description': 'Analysis length in hours - Default is 24 hours',
                        'access': 'item',
                        'default_value': 24},
                    7: {'name': 'Folder',
                        'description': 'Path to folder. Default is Desktop',
                        'access': 'item',
                        'default_value': r'%systemdrive%\users\%username%\Desktop'},
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
        self.analysis_length = None
        self.folder = None
        self.case_name = None
        self.case_path = None
        self.write_case = None
        self.overwrite = True
        self.output_config = None
        self.run_case = None
        self.ssh_cmd = None
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

    def run_checks(self, mesh, ground, weather, trees, stream, boundary_conditions, analysis_length, folder, name,
                   outputs, write, overwrite, run):

        # Gather data
        self.mesh = self.add_default_value(mesh, 0)
        self.ground = self.add_default_value(ground, 1)
        self.weather = self.add_default_value(weather, 2)
        self.trees = self.add_default_value(trees, 3)
        self.stream = self.add_default_value(stream, 4)
        self.boundary_conditions = self.add_default_value(boundary_conditions, 5)
        self.analysis_length = int(self.add_default_value(analysis_length, 6))
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

        # check if folder exists
        if os.path.exists(self.case_path):
            self.written = True
        else:
            os.mkdir(self.folder + '/' + self.case_name)

        files_written = []

        # Process weather
        weather_dict = self.weather.c
        weather_root = ET.Element('weather')
        weather_keys = weather_dict.keys()

        for k in weather_keys:
            data = ET.SubElement(weather_root, str(k))
            data.text = str(weather_dict[str(k)])

        weather_tree = ET.ElementTree(weather_root)
        weather_file = 'weather.xml'
        weather_tree.write(self.case_path + '/' + weather_file, xml_declaration=True)

        files_written.append(weather_file)

        # Save Mesh
        gh_geo.bake_export_delete(self.mesh, self.case_path, 'mesh', '.obj', doc)

        files_written.append('mesh.obj')

        # Process ground
        ground_dict = list(ground.c for ground in self.ground)
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
        ground_tree.write(self.case_path + '/' + ground_file, xml_declaration=True)

        files_written.append(ground_file)

        # Process trees
        tree_dict = list(tree.c for tree in self.trees)
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
        tree_tree.write(self.case_path + '/' + tree_file, xml_declaration=True)

        files_written.append(tree_file)

        # Process outputs
        output_dict = self.output_config.c
        output_root = ET.Element('output')

        for out_key in output_dict.keys():
            data = ET.SubElement(output_root, str(out_key))
            data.text = str(output_dict[out_key])

        output_tree = ET.ElementTree(output_root)
        output_file = 'outputs.xml'
        output_tree.write(self.case_path + '/' + output_file, xml_declaration=True)

        files_written.append(output_file)

        # Process stream
        # Add later

        # Process solver info
        solver_root = ET.Element('solver')
        analysis_length = ET.SubElement(solver_root, 'analysis_length')
        analysis_length.text = str(self.analysis_length)

        solver_tree = ET.ElementTree(solver_root)
        solver_file = 'solver.xml'
        solver_tree.write(self.case_path + '/' + solver_file, xml_declaration=True)

        files_written.append(solver_file)

        # Clean SSH folder
        ssh.clean_ssh_folder()

        # SSH commands
        self.ssh_cmd = ssh.get_ssh()

        file_transfer = files_written
        file_run = ['cmf_template.py']
        file_return = ['results.xml']

        self.ssh_cmd['file_transfer'] = ','.join(file_transfer)
        self.ssh_cmd['file_run'] = ','.join(file_run)
        self.ssh_cmd['file_return'] = ','.join(file_return)
        self.ssh_cmd['template'] = 'cmf'

        ssh.write_ssh_commands(self.ssh_cmd)

        self.written = True

    def do_case(self):

        ssh_template = ssh.ssh_path + '/ssh_template.py'
        transfer_files = self.ssh_cmd['file_transfer'].split(',')

        # Copy files from case folder to ssh folder
        for file in transfer_files:
            copyfile(self.case_path + '/' + file, ssh.ssh_path + '/' + file)

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
            self.write(doc)
            self.do_case()
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
                    2: {'name': 'Run',
                        'description': 'Run component',
                        'access': 'item',
                        'default_value': False}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},
                    1: {'name': 'Units',
                        'description': 'Shows the units of the results'},
                    2: {'name': 'Values',
                        'description': 'List with chosen result values'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 17
        self.unit = None
        self.path = None
        self.fetch_result = None
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

    def run_checks(self, path, fetch_result, run):

        # Gather data
        self.path = path
        self.fetch_result = int(self.add_default_value(fetch_result, 1))
        self.run_component = self.add_default_value(run, 2)

        # Run checks
        self.check_inputs()

    def process_xml(self):
        possible_results = ['Evapotranspiration', 'surface_water_volume', 'Surface_water_flux',
                            'heat_flux', 'aerodynamic_resistance', 'volumetric_flux', 'potential',
                            'theta', 'volume', 'wetness']

        # Write lookup file
        if self.fetch_result == 0 or 1 or 2 or 3 or 4:
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

        return csv.read_csv(path, False)

    def set_units(self):

        if self.fetch_result == 0:
            self.unit = 'm3'

        elif self.fetch_result == 1:
            self.unit = 'm3'

        elif self.fetch_result == 2:
            self.unit = 'm3/(m2s)'

        elif self.fetch_result == 3:
            self.unit = 'W/m2'

        elif self.fetch_result == 4:
            self.unit = 's/m'

        elif self.fetch_result == 5:
            self.unit = 'm3/(m2s)'

        elif self.fetch_result == 6:
            self.unit = 'm'

        elif self.fetch_result == 7:
            self.unit = 'm3'

        elif self.fetch_result == 8:
            self.unit = 'm3'

        elif self.fetch_result == 9:
            self.unit = '-'

    def run(self):
        if self.checks and self.run_component:
            self.set_units()

            results = self.load_result_csv(self.process_xml())

            self.results = gh_misc.list_to_tree(results)


class CMFOutputs(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Evapotranspiration',
                        'description': 'Cell evaporation - default is set to True',
                        'access': 'item',
                        'default_value': True},
                    1: {'name': 'SurfaceWater',
                        'description': 'Cell surface water. Collects both volumetric flux and volume'
                                       ' - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    2: {'name': 'HeatFlux',
                        'description': 'Cell surface heat flux - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    3: {'name': 'AerodynamicResistance',
                        'description': 'Cell aerodynamic resistance - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    4: {'name': 'VolumetricFlux',
                        'description': 'Soil layer volumetric flux vectors - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    5: {'name': 'Potential',
                        'description': 'Soil layer total potential (Psi_tot = Psi_M + Psi_G - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    6: {'name': 'Theta',
                        'description': 'Soil layer volumetric water content of the layer - default is set to False',
                        'access': 'item',
                        'default_value': False},
                    7: {'name': 'Volume',
                        'description': 'Soil layer volume of water in the layer - default is set to True',
                        'access': 'item',
                        'default_value': True},
                    8: {'name': 'Wetness',
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
        self.surface_water = None
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

    def run_checks(self, evapo_trans, surface_water, heat_flux, aero_res, three_d_flux, potential,
                   theta, volume, wetness):

        # Gather data
        self.evapo_trans = self.add_default_value(evapo_trans, 0)
        self.surface_water = self.add_default_value(surface_water, 1)
        self.heat_flux = self.add_default_value(heat_flux, 2)
        self.aero_res = self.add_default_value(aero_res, 3)
        self.three_d_flux = self.add_default_value(three_d_flux, 4)
        self.potential = self.add_default_value(potential, 5)
        self.theta = self.add_default_value(theta, 6)
        self.volume = self.add_default_value(volume, 7)
        self.wetness = self.add_default_value(wetness, 8)

        # Run checks
        self.check_inputs()

    def set_outputs(self):

        output_dict = {'cell': [], 'layer': []}

        if self.evapo_trans:
            output_dict['cell'].append('evaporation')
            output_dict['cell'].append('transpiration')

        if self.surface_water:
            output_dict['cell'].append('surface_water_volume')
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

    def __init__(self):
        GHComponent.__init__(self)