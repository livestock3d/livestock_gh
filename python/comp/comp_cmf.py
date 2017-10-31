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
import gh.misc as gh_misc
import gh.ssh as ssh
import gh.geometry as gh_geo
import lib.csv as csv
from comp.component import GHComponent
import gh.misc as gh_misc

# Grasshopper imports
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs

# -------------------------------------------------------------------------------------------------------------------- #
# Classes


class CMFGround(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['Layers', 'Soil layers to add to the mesh in m'],
                    1: ['RetentionCurve', 'Retention curve'],
                    2: ['SurfaceProperties', 'Input from Livestock CMF SurfaceProperties'],
                    3: ['InitialSaturation', 'Initial saturation of the soil layers'],
                    4: ['FaceIndices', 'List of face indices, on where the ground properties are applied.']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Ground', 'Livestock Ground Data Class']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 11
        self.face_indices = None
        self.layers = None
        self.retention_curve = None
        self.surface_properties = None
        self.initial_saturation = None
        self.checks = [False, False, False, False, False]
        self.results = None

    def check_inputs(self, ghenv):
        warning = []

        if self.layers:
            self.checks[1] = True
        else:
            warning.append('Layer values must be float or list of floats! Input provided was: ' + str(self.layers))

        if self.retention_curve:
            self.checks[2] = True
        else:
            warning.append('Retention curve is wrong!')

        if isinstance(self.initial_saturation,float):
            self.checks[4] = True
        else:
            warning.append('Initial saturation must be float! Input provided was: ' + str(self.initial_saturation))

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
        self.config_component(ghenv, self.component_number)

    def run_checks(self, ghenv, layers, retention_curve, surface_properties, initial_saturation, face_indices):

        # Gather data
        self.layers = layers
        self.retention_curve = retention_curve
        self.surface_properties = surface_properties
        self.initial_saturation = initial_saturation
        self.face_indices = face_indices

        # Run checks
        self.check_inputs(ghenv)

    def run(self):
        if self.checks:
            ground_dict = {'face_indices': self.face_indices,
                           'layers': self.layers,
                           'retention_curve': self.retention_curve,
                           'surface_properties': self.surface_properties,
                           'initial_saturation': self.initial_saturation}

            self.results = gh_misc.PassClass(ground_dict, 'Ground')


class CMFWeather(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['Temperature', 'Temperature in C - List of floats'],
                    1: ['WindSpeed', 'Wind speed in m/s - List of floats'],
                    2: ['RelativeHumidity', 'Relative humidity in % - List of floats'],
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
        self.component_number = 12
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

    def check_inputs(self, ghenv):
        if self.temp:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def config(self, ghenv):

        # Generate Component
        self.config_component(ghenv, self.component_number)

    def run_checks(self, ghenv, temp, wind, rel_hum, cloud_cover, global_radiation, rain, ground_temp, location):

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
        self.check_inputs(ghenv)

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

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['Property', '0-1 grasses. 2-6 soils']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Units', 'Shows the units of the surface values'],
                    2: ['SurfaceValues', 'Chosen surface properties values'],
                    3: ['SurfaceProperties', 'Livestock surface properties data']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 13
        self.data = None
        self.units = None
        self.data_path = r'C:\livestock\data\surfaceData.csv'
        self.property_index = None
        self.property = None
        self.checks = False
        self.results = None

    def check_inputs(self, ghenv):
        if self.property_index:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def config(self, ghenv):

        # Generate Component
        self.config_component(ghenv, self.component_number)

    def run_checks(self, ghenv, property):

        # Gather data
        self.property_index = property

        # Run checks
        self.check_inputs(ghenv)

    def load_csv(self):

        load = csv.read_csv(self.data_path)
        self.units = load[0]
        self.data = load[1]

    def pick_property(self):
        self.load_csv()
        data_list = self.data[self.property_index]
        self.property = collections.OrderedDict([('name', data_list[0]),
                                                 ('lai', data_list[1]),
                                                 ('albedo', data_list[2]),
                                                 ('canopy_closure', data_list[3]),
                                                 ('canopy_par', data_list[4]),
                                                 ('canopy_capacity', data_list[5]),
                                                 ('stomatal_res', data_list[6]),
                                                 ('root_depth', data_list[7]),
                                                 ('root_fraction', data_list[8])
                                                 ])

    def run(self):
        if self.checks:
            self.pick_property()

            self.results = gh_misc.PassClass(self.property, 'SurfaceProperty')


class CMFSyntheticTree(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['FaceIndex', 'Mesh face index where tree is placed'],
                    1: ['TreeType', 'Tree types: 0 - Deciduous, 1 - Coniferous, 2 - Shrubs'],
                    2: ['Height', 'Height of tree in meters']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Units', 'Shows the units of the tree values'],
                    2: ['TreeValues', 'Chosen tree properties values'],
                    3: ['TreeProperties', 'Livestock tree properties data']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 13
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

    def check_inputs(self, ghenv):
        if self.height:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def config(self, ghenv):

        # Generate Component
        self.config_component(ghenv, self.component_number)

    def run_checks(self, ghenv, face_index, tree_type, height):

        # Gather data
        self.face_index = face_index
        self.tree_type = tree_type
        self.height = height

        # Run checks
        self.check_inputs(ghenv)

    def load_csv(self):

        load = csv.read_csv(self.data_path[self.tree_type])
        self.units = load[0]
        self.data = load[1]

    def compute_tree(self):
        self.load_csv()
        self.property = collections.OrderedDict([('name', 'Synthetic Deciduous'),
                                                 ('height', self.height),
                                                 ('lai', float(self.data[0][2]) * self.height + float(self.data[1][2])),
                                                 ('albedo', float(self.data[0][3]) * self.height + float(self.data[1][3])),
                                                 ('canopy_closure', float(self.data[2][4])),
                                                 ('canopy_par', float(self.data[2][5])),
                                                 ('canopy_capacity', float(self.data[0][6]) * self.height + float(self.data[1][6])),
                                                 ('stomatal_res', float(self.data[0][7]) * self.height + float(self.data[1][7])),
                                                 ('root_depth', float(self.data[2][8])),
                                                 ('root_fraction', float(self.data[2][9]))
                                                 ])

    def run(self):
        if self.checks:
            self.compute_tree()
            dic = {'face_index': self.face_index,
                   'property': self.property}

            self.results = gh_misc.PassClass(dic, 'SyntheticTreeProperty')


class CMFRetentionCurve(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['SoilIndex', 'Index for chosing soil type']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Units', 'Shows the units of the curve values'],
                    2: ['CurveValues','Chosen curve properties values'],
                    3: ['RetentionCurve','Livestock Retention Curve']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 15
        self.data = None
        self.units = None
        self.data_path = r'C:\livestock\data\soilData.csv'
        self.property = None
        self.soil_index = None
        self.checks = False
        self.results = None

    def check_inputs(self, ghenv):
        if isinstance(self.soil_index, int):
            self.checks = True
        else:
            warning = 'soilIndex should be an integer'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def config(self, ghenv):

        # Generate Component
        self.config_component(ghenv, self.component_number)

    def run_checks(self, ghenv, soil_index):

        # Gather data
        self.soil_index = soil_index

        # Run checks
        self.check_inputs(ghenv)

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

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['Mesh', 'Topography as a mesh'],
                    1: ['Ground', 'Input from Livestock CMF_Ground'],
                    2: ['Weather', 'Input from Livestock CMF_Weather'],
                    3: ['Trees', 'Input from Livestock CMF_Tree'],
                    4: ['Stream', 'Input from Livestock CMF_Stream'],
                    5: ['Folder', 'Path to folder. Default is Desktop'],
                    6: ['CaseName', 'Case name as string. Default is CMF'],
                    7: ['Output', 'Connect Livestock Outputs'],
                    8: ['Write', 'Boolean to write files'],
                    9: ['Overwrite', 'If True excising case will be overwritten. Default is set to True'],
                    10: ['Run', 'Boolean to run analysis'
                                '\nAnalysis will be ran through SSH. Configure the connection with Livestock SSH']}

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['ResultPath', 'Path to result files']}

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 14
        self.mesh = None
        self.ground = None
        self.weather = None
        self.trees = None
        self.stream = None
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

    def check_inputs(self, ghenv):
        if self.ground:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def config(self, ghenv):

        # Generate Component
        self.config_component(ghenv, self.component_number)

    def run_checks(self, ghenv, mesh, ground, weather, output, trees=None, stream=None,
                   folder=r'%systemdrive%\users\%username%\Desktop', name='CMF', write=False, overwrite=True, run=False):

        # Gather data
        self.mesh = mesh
        self.ground = ground
        self.weather = weather
        self.trees = trees
        self.stream = stream
        self.folder = folder
        self.case_name = name
        self.write_case = write
        self.overwrite = overwrite
        self.output_config = output
        self.run_case = run
        self.update_case_path()

        # Run checks
        self.check_inputs(ghenv)

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
        weather_tree.write(self.case_path + '/' + 'weather.xml', xml_declaration=True)

        files_written.append('weather.xml')

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
        ground_tree.write(self.case_path + '/' + 'ground.xml', xml_declaration=True)

        files_written.append('ground.xml')

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
        tree_tree.write(self.case_path + '/' + 'trees.xml', xml_declaration=True)

        files_written.append('trees.xml')

        # Process outputs
        outfile = open(self.case_path + '/outputs.txt', 'w')

        for key in self.output_config.c.keys():
            outfile.write(str(key)+'\n')

        outfile.close()

        files_written.append('outputs.txt')

        # Process stream
        # Add later

        # Clean SSH folder
        ssh.clean_ssh_folder()

        # SSH commands
        self.ssh_cmd = ssh.get_ssh()

        file_transfer = files_written
        file_run = ['cmf_template.py']
        file_return = ['results.xml']

        self.ssh_cmd['file_transfer'] = ','.join(file_transfer)
        self.ssh_cmd['file_run'] = file_run
        self.ssh_cmd['file_return'] = file_return
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

    def check_results(self, ghenv):
        ssh_result = ssh.ssh_path + '/results.xml'
        result_path = self.case_path + '/results.xml'

        if os.path.exists(ssh_result):
            copyfile(ssh_result, result_path)
            ssh.clean_ssh_folder()
            return result_path
        else:
            warning = 'Could not find result file. Unknown error occurred'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def run(self, ghenv, doc):
        if self.checks and self.write_case:
            self.write(doc)

        elif self.checks and self.run:
            self.write(doc)
            self.do_case()
            self.results = self.check_results(ghenv)


class CMFResults(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)


class CMFOutputs(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)

        def inputs():
            return {0: ['Evapotranspiration', 'Default is set to True'],
                    1: ['MoistureContent', 'Default is set to True'],
                    2: ['Potential', 'Default is set to False'],
                    3: ['SurfaceWaterFlux', 'Default is set to False']
                    }

        def outputs():
            return {0: ['readMe!', 'In case of any errors, it will be shown here.'],
                    1: ['Outputs', 'Livestock Output Data']
                    }

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 16
        self.evapo_trans = None
        self.moisture = None
        self.potential = None
        self.surface_flux = None
        self.checks = False
        self.results = None

    def check_inputs(self, ghenv):
        if self.evapo_trans:
            self.checks = True
        else:
            warning = 'Temperature should be a float'
            print(warning)
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)

    def config(self, ghenv):

        # Generate Component
        self.config_component(ghenv, self.component_number)

    def run_checks(self, ghenv, evapotranspiration=True, moisture_content=True, potential=False, surface_water_flux=False):

        # Gather data
        self.evapo_trans = evapotranspiration
        self.moisture = moisture_content
        self.potential = potential
        self.surface_flux = surface_water_flux

        # Run checks
        self.check_inputs(ghenv)

    def set_outputs(self):

        output_dict = {}

        if self.evapo_trans:
            output_dict['evaporation'] = {}
            output_dict['transpiration'] = {}
        else:
            pass

        if self.moisture:
            output_dict['moisture_content'] = {}
        else:
            pass

        if self.potential:
            output_dict['potential'] = {}
        else:
            pass

        if self.surface_flux:
            output_dict['surface_water_flux'] = {}
        else:
            pass

        return output_dict

    def run(self):
        if self.checks:
            out_dict = self.set_outputs()

            self.results = gh_misc.PassClass(out_dict, 'Outputs')


class CMFOutlet(GHComponent):

    def __init__(self):
        GHComponent.__init__(self)