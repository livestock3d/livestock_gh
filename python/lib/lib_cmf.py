__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

import cmf
from datetime import datetime,timedelta
import numpy as np
import xml.etree.ElementTree as ET
import os
import xmltodict
import pymesh as pm
from itertools import compress

# -------------------------------------------------------------------------------------------------------------------- #
# Functions and Classes


class CMFModel:

    def __init__(self, folder, analysis_length=8760):
        self.folder = folder
        self.mesh_path = None
        self.weather_dict = {}
        self.trees_dict = {}
        self.ground_dict = {}
        self.rain_station = None
        self.meteo = None
        self.analysis_length = analysis_length
        self.outputs = None
        self.solved = False
        self.results = {}

    def load_cmf_files(self):

        def load_weather(folder, files):
            weather_path = None

            for f in files:
                if f.startswith('weather'):
                    weather_path = folder + '/' + f
                else:
                    pass

            weather_tree = ET.tostring(ET.parse(weather_path).getroot())
            weather = xmltodict.parse(weather_tree)
            weather_dict = {}

            for w_key in weather['weather'].keys():
                lst0 = eval(weather['weather'][str(w_key)])
                try:
                    lst1 = [float(i) for i in lst0]
                except TypeError:
                    lst1 = lst0

                weather_dict[str(w_key)] = lst1

            return weather_dict

        def load_tree(folder, files):
            tree_path = None

            for f in files:
                if f.startswith('trees'):
                    tree_path = folder + '/' + f
                else:
                    pass

            tree_tree = ET.tostring(ET.parse(tree_path).getroot())
            trees = xmltodict.parse(tree_tree)
            tree_dict = {}

            for tree_key in trees['tree'].keys():
                tree_dict[str(tree_key)] = {}

                for t in trees['tree'][str(tree_key)].keys():
                    tree_dict[str(tree_key)][str(t)] = eval(trees['tree'][str(tree_key)][str(t)])

            return tree_dict

        def load_ground(folder, files):
            ground_path = None

            for f in files:
                if f.startswith('ground'):
                    ground_path = folder + '/' + f
                else:
                    pass

            ground_tree = ET.tostring(ET.parse(ground_path).getroot())
            grounds = xmltodict.parse(ground_tree)
            ground_dict = {}

            for ground in grounds['ground'].keys():
                ground_dict[str(ground)] = {}

                for g in grounds['ground'][ground]:
                    ground_dict[str(ground)][str(g)] = eval(grounds['ground'][ground][g])
            return ground_dict

        def load_mesh(folder, files):
            mesh_path = None

            for f in files:
                if f.endswith('.obj'):
                    mesh_path = folder + '/' + f
                else:
                    pass

            return mesh_path

        def load_outputs(folder, files):
            output_path = None

            for f in files:
                if f.startswith('outputs'):
                    output_path = folder + '/' + f
                else:
                    pass

            out_list = []

            out_file = open(output_path, 'r')
            out_data = out_file.readlines()

            for line in out_data:
                out_list.append(line[:-1])

            return out_list

        cmf_files = os.listdir(self.folder)

        # Load files and assign data to variables
        self.weather_dict = load_weather(self.folder, cmf_files)
        self.trees_dict = load_tree(self.folder, cmf_files)
        self.ground_dict = load_ground(self.folder, cmf_files)
        self.mesh_path = load_mesh(self.folder, cmf_files)
        self.outputs = load_outputs(self.folder, cmf_files)

        return True

    def mesh_to_cells(self, cmf_project, mesh_path):
        """
        Takes a mesh and converts it into CMF cells
        :param mesh_path: Path to mesh file
        :param cmf_project: CMF project object
        :return: True
        """

        # Load mesh
        mesh = pm.load_mesh(mesh_path)
        mesh.enable_connectivity()

        # Initialize mesh data
        mesh.add_attribute('face_centroid')
        mesh.add_attribute('face_index')
        mesh.add_attribute('face_area')
        cen_pts = mesh.get_attribute('face_centroid')
        face_index = mesh.get_attribute('face_index')
        face_area = mesh.get_attribute('face_area')
        faces = mesh.faces
        vertices = mesh.vertices

        # Helper functions
        def face_vertices(face_index):
            """
            Returns the vertices of a face
            :param face_index: Face index (int)
            :return: v0, v1, v2
            """

            face = faces[int(face_index)]
            v0 = vertices[face[0]]
            v1 = vertices[face[1]]
            v2 = vertices[face[2]]

            return v0, v1, v2

        def face_face_edge(face0, face1):
            """
            Returns the width of the edge between to faces
            :param face0: Face index
            :param face1: Face index
            :return: float value with the edge with
            """

            # Get vertices
            v = []
            v0 = face_vertices(int(face0))
            v1 = face_vertices(int(face1))

            # Find out which edge is shared
            for vertex in v0:
                equal = np.equal(vertex, v1)
                if np.sum(equal) > 0:
                    v.append(vertex)
                else:
                    pass

            # Compute the width of the edge
            dx = abs(v[0][0] - v[1][0])
            dy = abs(v[0][1] - v[1][1])
            dz = abs(v[0][2] - v[1][2])
            edge_width = np.sqrt(dx**2 + dy**2 + dz**2)

            return edge_width

        # Construct centroid list
        centroids = []
        i = 0
        while i < len(cen_pts):
            for j in range(0, len(face_index)):
                centroids.append([face_index[j], np.array([cen_pts[i], cen_pts[i+1], cen_pts[i+2]])])
                i += 3

        # Create cells
        for i in range(0, len(centroids)):
            x, y, z = centroids[i][1]
            a = float(face_area[i])
            cmf_project.NewCell(x=float(x), y=float(y), z=float(z), area=a, with_surfacewater=True)

        # Connect cells
        for face in face_index:
            adjacent_faces = mesh.get_face_adjacent_faces(int(face))

            for adj in adjacent_faces:
                width = face_face_edge(face,adj)
                if width:
                    cmf_project[face].topology.AddNeighbor(cmf_project[adj], width)
                else:
                    pass

        return True

    def add_tree(self, cmf_project, cell_index, property_dict):
        """Adds a tree to the model"""

        cell = cmf_project.cells[int(cell_index)]
        self.set_surface_properties(cell, property_dict)
        cell.add_storage('Canopy_%cell_index' % str(cell_index), 'C')

        cmf.Rainfall(cell.canopy, cell, False, True)
        cmf.Rainfall(cell.surfacewater, cell, True, False)
        cmf.RutterInterception(cell.canopy, cell.surfacewater, cell)
        cmf.CanopyStorageEvaporation(cell.canopy, cell.evaporation, cell)

        return True

    def set_surface_properties(self, cell, property_dict):
        cell.vegetation.Height = property_dict['height']
        cell.vegetation.LAI = property_dict['lai']
        cell.vegetation.albedo = property_dict['albedo']
        cell.vegetation.CanopyClosure = property_dict['canopy_closure']
        cell.vegetation.CanopyParExtinction = property_dict['canopy_par']
        cell.vegetation.CanopyCapacityPerLAI = property_dict['canopy_capacity']
        cell.vegetation.StomatalResistance = property_dict['stomatal_res']
        cell.vegetation.RootDepth = property_dict['root_depth']
        cell.vegetation.fraction_at_rootdepth = property_dict['root_fraction']

    def add_surface_properties(self, cmf_project, property_dict, cell_indices):

        for c_i in cell_indices:
            cell = cmf_project.cells[int(c_i)]

            self.set_surface_properties(cell, property_dict)

            # Install Penman & Monteith method to calculate EvapoTranspiration_potential
            cell.install_connection(cmf.PenmanMonteithET)

        return True

    def retention_curve(self, r_curve):
        """
        Converts a dict of retention curve parameters into a CMF van Genuchten-Mualem retention curve.
        :param r_curve: dict
        :return: CMF retention curve
        """

        r = cmf.VanGenuchtenMualem(r_curve['K_sat'], r_curve['phi'], r_curve['alpha'], r_curve['n'], r_curve['m'])
        r.l = r_curve['l']

        return r

    def add_layers_to_cells(self, cmf_project, depth_of_layers, r_curve, initial_saturation, cell_indices):
        """Adds 'depth' to the cells"""

        # Convert retention curve parameters into CMF retention curve
        r_curve = self.retention_curve(r_curve)

        for c_i in cell_indices:

            # Add layers
            for i in range(0, len(depth_of_layers)):
                #print('retention curve:', r_curve)
                #print('depth', depth_of_layers)
                cmf_project.cells[int(c_i)].add_layer(float(depth_of_layers[i]), r_curve)

            # Install connections
            cmf_project.cells[int(c_i)].install_connection(cmf.Richards)
            cmf_project.cells[int(c_i)].install_connection(cmf.GreenAmptInfiltration)

            # Set initial saturation
            cmf_project.cells[int(c_i)].saturated_depth = initial_saturation

        # Connect fluxes
        cmf.connect_cells_with_flux(cmf_project, cmf.Darcy)
        cmf.connect_cells_with_flux(cmf_project, cmf.KinematicSurfaceRunoff)

        return True

    def create_stream(self, shape, shape_param, outlet):
        """Create a stream"""
        # ShapeParam(Tri) = [length, bankSlope, x, y, z, intialWaterDepth]
        # ShapeParam(Rec) = [length, width, x, y, z, intialWaterDepth]
        reaches = []

        # Create stream
        if shape == 0:
            for i in range(len(shape_param)):
                reach_shape = cmf.TriangularReach(shape_param[i][0],shape_param[i][1])
                reaches.append([self.project.NewReach(shape_param[i][2], shape_param[i][3], shape_param[i][4], reach_shape, False)])
                reaches[-1].depth(shape_param[5])

                # Connect reaches
                if not reaches:
                    pass
                elif len(reaches) == len(shape_param):
                    channel_out = self.project.NewOutlet(outlet[0], outlet[1], outlet[2])
                    reaches[-1].set_downstream(channel_out)
                else:
                    reaches[-2].set_downstream(reaches[-1])

        elif shape == 1:
            for i in range(len(shape_param)):
                reach_shape = cmf.RectangularReach(shape_param[i][0],shape_param[i][1])
                reaches.append([self.project.NewReach(shape_param[i][2], shape_param[i][3], shape_param[i][4], reach_shape, False)])
                reaches[-1].depth(shape_param[5])

                # Connect reaches
                if not reaches:
                    pass
                elif len(reaches) == len(shape_param):
                    channel_out = self.project.NewOutlet(outlet[0], outlet[1], outlet[2])
                    reaches[-1].set_downstream(channel_out)
                else:
                    reaches[-2].set_downstream(reaches[-1])
        else:
            return None

    def create_weather_stations(self, cmf_project, weather_series, lat, long, time_zone):

        # Add a rainfall station to the project
        rain_station = cmf_project.rainfall_stations.add(Name='Rain Station',
                                                         Data=weather_series['rain'],
                                                        Position=(0, 0, 0))

        # Add a meteo station to the project
        self.meteo = cmf_project.meteo_stations.add_station(Name='Meteo Station',
                                                            position=(0, 0, 0),
                                                            latitude=lat,
                                                            longitude=long,
                                                            timezone=time_zone)
        self.meteo.T = weather_series['temp']
        self.meteo.Tmax = self.meteo.T.reduce_max(self.meteo.T.begin, cmf.day)
        self.meteo.Tmin = self.meteo.T.reduce_min(self.meteo.T.begin, cmf.day)
        self.meteo.Windspeed = weather_series['wind']
        self.meteo.rHmean = weather_series['rel_hum']
        self.meteo.Sunshine = weather_series['sun']
        self.meteo.Rs = weather_series['rad']
        self.meteo.Tground = weather_series['ground_temp']

    def connect_weather_to_cells(self, cmf_project):
        for c in cmf_project.cells:
            self.rain_station.use_for_cell(c)
            self.meteo.use_for_cell(c)

    def create_weather(self, cmf_project):
        """Creates weather for the project"""

        def convert_weather_units(weather_dict):

            # covert rain from mm/h to mm/day,
            converted_rain = [val * 24 for val in weather_dict['rain']]
            weather_dict['rain'] = converted_rain

            # convert global radiation from w/m2 to MJ/(m2*day)
            con = 3600*24/10**6
            converted_rad = [val*con for val in weather_dict['rad']]
            weather_dict['rad'] = converted_rad

            return weather_dict

        def create_time_series(timeStep=1.0):

            # Start date is the 1st of January 2010 at 00:00
            start = cmf.Time(1, 1, 2010, 0, 0)
            step = cmf.h * timeStep

            # Type of interpolation between values
            # 0 - Nearest neighbor,
            # 1 - Linear,
            # 2 - Squared,
            # 3 - Cubic, etc.
            interpolation = 1

            # Create time series
            return cmf.timeseries(begin=start, step=step)

        def weather_to_time_series(weather, time_series):

            # Create time series
            t_series = time_series
            w_series = time_series
            rh_series = time_series
            sun_series = time_series
            rad_series = time_series
            rain_series = time_series
            ground_temp_series = time_series

            # add data
            for i in range(len(weather['temp'])):
                t_series.add(weather['temp'][i])
                w_series.add(weather['wind'][i])
                rh_series.add(weather['rel_hum'][i])
                sun_series.add(weather['sun'][i])
                rad_series.add(weather['rad'][i])
                rain_series.add(weather['rain'][i])
                ground_temp_series.add(weather['ground_temp'][i])

            return {'temp': t_series, 'wind': w_series, 'rel_hum': rh_series, 'sun': sun_series, 'rad': rad_series,
                    'rain': rain_series, 'ground_temp': ground_temp_series}

        time = create_time_series()
        weather_series = weather_to_time_series(self.weather_dict, time)
        self.create_weather_stations(cmf_project,
                                     weather_series,
                                     self.weather_dict['latitude'],
                                     self.weather_dict['longitude'],
                                     self.weather_dict['time_zone'])
        self.connect_weather_to_cells(cmf_project)

    def config_outputs(self, cmf_project):
        """Function to set up result gathering dictionary"""

        out_dict = {}

        for cell_index in range(0, len(cmf_project.cells)):
            cell_name = 'cell_%cell_index' % str(cell_index)
            out_dict[cell_name] = {}

            for layer_index in range(0, len(cmf_project.cells[cell_index].layers)):
                layer_name = 'layer_%layer_index' % str(layer_index)
                out_dict[cell_name][layer_name] = {}

                for output in self.outputs:
                    out_dict[cell_name][layer_name][str(output)] = []

        self.results = out_dict

    def gather_results(self, cmf_project):

        for cell_index in range(0, len(cmf_project.cells)):
            cell_name = 'cell_%cell_index' % str(cell_index)

            for layer_index in range(0, len(cmf_project.cells[cell_index].layers)):
                layer_name = 'layer_%layer_index' % str(layer_index)

                for out_key in self.results[cell_name][layer_name].keys():

                    if out_key == 'potential':
                        self.results[cell_name][layer_name][out_key].append(
                            cmf_project.cells[cell_index][layer_index].potential)

                    elif out_key == 'moisture':
                        self.results[cell_name][layer_name][out_key].append(
                            cmf_project.cells[cell_index][layer_index].theta)

                    elif out_key == 'transpiration':
                        self.results[cell_name][layer_name][out_key].append(
                            cmf_project.cells[cell_index][layer_index].transpiration)

                    elif out_key == 'evaporation':
                        self.results[cell_name][layer_name][out_key].append(
                            cmf_project.cells[cell_index][layer_index].evaporation)

                    elif out_key == 'surface_water':
                        self.results[cell_name][layer_name][out_key].append(
                            cmf_project.cells[cell_index][layer_index].surfacewater)

                    else:
                        print('Unknown result to collect')
                        pass

    def solve(self, cmf_project, tolerance=1e-8):
        """Solves the model"""

        # Create solver, set time and set up results
        solver = cmf.CVodeIntegrator(cmf_project, tolerance)
        solver.t = cmf.Time(1, 1, 2017)
        self.config_outputs(cmf_project)

        # Save initial conditions to results
        self.gather_results(cmf_project)

        # Run solver and save results at each time step
        for t in solver.run(solver.t, solver.t + timedelta(hours=self.analysis_length), timedelta(hours=1)):
            self.gather_results(cmf_project)

        self.solved = True
        return True

    def save_results(self, file_path):
        """Saves the computed results to a xml file"""

        if not self.solved:
            print('Project not solved!')
            return None

        else:
            result_root = ET.Element('result')

            for cell in self.results.keys():
                cell_tree = ET.SubElement(result_root, str(cell))

                for layer in cell.keys():
                    layer_tree = ET.SubElement(cell_tree, str(layer))

                    for result_key in layer.keys():
                        data = ET.SubElement(layer_tree, str(result_key))
                        data.text = str(self.results[cell][layer][result_key])

            result_tree = ET.ElementTree(result_root)
            result_tree.write(file_path, xml_declaration=True)

            return True

    def run_model(self, result_path):
        """Runs the model with everything"""

        # Initialize project
        project = cmf.project()
        self.load_cmf_files()

        # Add cells and properties to them
        self.mesh_to_cells(project, self.mesh_path)

        for key in self.ground_dict.keys():
            self.add_layers_to_cells(project,
                                     self.ground_dict[str(key)]['layers'],
                                     self.ground_dict[str(key)]['retention_curve'],
                                     self.ground_dict[str(key)]['initial_saturation'],
                                     self.ground_dict[str(key)]['face_indices'])

            self.add_surface_properties(project,
                                        self.ground_dict[str(key)]['surface_properties'],
                                        self.ground_dict[str(key)]['face_indices'])

        for key in self.trees_dict.keys():
            self.add_tree(project,
                          self.trees_dict[str(key)]['face_index'],
                          self.trees_dict[str(key)]['property'])

        # Create the weather
        self.create_weather(project)

        # Run solver
        self.solve(project)

        # Save the results
        self.save_results(result_path)


def ground_temperature():
    return None



