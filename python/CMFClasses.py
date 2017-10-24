__author__ = "Christian Kongsgaard"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Christian Kongsgaard"
__email__ = "ocni@dtu.dk"
__status__ = "Work in Progress"

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
from pprint import pprint

# -------------------------------------------------------------------------------------------------------------------- #
# Functions and Classes

class CMFModel():

    def __init__(self, mesh_path, weather_path, analysis_length=760):
        self.project = cmf.project
        self.mesh = mesh_path
        self.weather_path = weather_path
        self.weather = {}
        self.rain_station = None
        self.meteo = None
        self.analysis_length = analysis_length
        self.solved = False
        self.results = {}

    def mesh_to_cells(self, mesh_path, project):
        """
        Takes a mesh and converts it into CMF cells
        :param mesh_path: Path to mesh file
        :param project: CMF project object
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
            :return: 
            """

            # Get vertices
            v00, v01, v02 = face_vertices(int(face0))
            v10, v11, v12 = face_vertices(int(face1))

            # Find out which edge is shared
            com0 = np.equal(v00, [v10, v11, v12])
            com1 = np.equal(v01, [v10, v11, v12])
            com2 = np.equal(v02, [v10, v11, v12])

            if np.sum(com0) > 0:
                V = list(compress([v10, v11, v12], com0)).append(v00)

            elif np.sum(com1) > 0:
                V = list(compress([v10, v11, v12], com1)).append(v01)

            elif np.sum(com2) > 0:
                V = list(compress([v10, v11, v12], com2)).append(v02)

            else:
                # No shared edge
                return None

            # Compute the width of the edge
            dx = abs(V[0][0]-V[1][0])
            dy = abs(V[0][1]-V[1][1])
            dz = abs(V[0][2]-V[1][2])
            width = np.sqrt(dx**2+dy**2+dz**2)

            return width

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
            a = face_area[i]
            project.NewCell(x, y, z, a, True)

        # Connect cells
        for face in face_index:
            adjacent_faces = mesh.get_face_adjacent_faces(int(face))

            for adj in adjacent_faces:
                width = face_face_edge(face,adj)
                if width:
                    project[face].topology.AddNeighbor(project[adj], width)
                else:
                    pass

        return True

    def add_tree(self, cell_index, property_dict):
        """Adds a tree to the model"""

        self.set_surface_properties(self.project.cells[int(cell_index)], property_dict)

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
        cell.vegetation.RootContent = property_dict['root_content']

    def add_surface_properties(self, property_dict, cell_indices):

        for c_i in cell_indices:
            self.set_surface_properties(self.project.cells[int(c_i)], property_dict)

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

    def add_layers_to_cells(self, depth_of_layers, r_curve, initial_saturation, cell_indices):
        """Adds 'depth' to the cells"""

        # Convert retention curve parameters into CMF retention curve
        r_curve = self.retention_curve(r_curve)

        for c_i in cell_indices:

            # Add layers
            for i in range(0, len(depth_of_layers)):
                self.project.cells[int(c_i)].add_layer((i + 1) * depth_of_layers, r_curve)

            # Install connections
            self.project.cells[int(c_i)].install_connection(cmf.Richards)
            self.project.cells[int(c_i)].install_connection(cmf.GreenAmptInfiltration)

            # Set initial saturation
            self.project.cells[int(c_i)].saturated_depth = initial_saturation

        # Connect fluxes
        cmf.connect_cells_with_flux(self.project, cmf.Darcy)
        cmf.connect_cells_with_flux(self.project, cmf.KinematicSurfaceRunoff)

        return True

    def create_stream(self, shape, shape_param, outlet):
        """Create a stream"""
        # ShapeParam(Tri) = [length, bankSlope, x, y, z, intialWaterDepth]
        # ShapeParam(Rec) = [length, width, x, y, z, intialWaterDepth]
        reaches = []

        # Create stream
        if shape == 0:
            for i in range(len(shapeParam)):
                reachShape = cmf.TriangularReach(shapeParam[i][0],shapeParam[i][1])
                reaches.append([self.project.NewReach(shapeParam[i][2], shapeParam[i][3], shapeParam[i][4], reachShape, False)])
                reaches[-1].depth(shapeParam[5])

                # Connect reaches
                if not reaches:
                    pass
                elif len(reaches) == len(shapeParam):
                    channelOut = self.project.NewOutlet(outlet[0], outlet[1], outlet[2])
                    reaches[-1].set_downstream(channelOut)
                else:
                    reaches[-2].set_downstream(reaches[-1])

        elif shape == 1:
            for i in range(len(shapeParam)):
                reachShape = cmf.RectangularReach(shapeParam[i][0],shapeParam[i][1])
                reaches.append([self.project.NewReach(shapeParam[i][2], shapeParam[i][3], shapeParam[i][4], reachShape, False)])
                reaches[-1].depth(shapeParam[5])

                # Connect reaches
                if not reaches:
                    pass
                elif len(reaches) == len(shapeParam):
                    channelOut = self.project.NewOutlet(outlet[0], outlet[1], outlet[2])
                    reaches[-1].set_downstream(channelOut)
                else:
                    reaches[-2].set_downstream(reaches[-1])
        else:
            return None

    def create_weather(self):
        """Creates weather for the project"""

        def read_weather(path):
            """Reads a epw file and convert it into something usefull"""

            weather_dict = {'temp': temp, 'wind': wind, 'relHum': rh, 'sun': sun, 'rad':rad, 'rain': rain, 'latitude': lat, 'longitude': long, 'timeZone': timeZone}

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

            # Create timeseries
            return cmf.timeseries(begin=start, step=step, interpolation=interpolation)

        def convert_weather(weather, time_series):
            # Create time series
            t_series = time_series
            w_series = time_series
            rh_series = time_series
            sun_series = time_series
            rad_series = time_series
            rain_series = time_series

            # add data
            for i in range(len(weather['temp'])):
                t_series.add(weather['temp'][i])
                w_series.add(weather['wind'][i])
                rh_series.add(weather['relHum'][i])
                sun_series.add(weather['sun'][i])
                rad_series.add(weather['rad'][i])
                rain_series.add(weather['rain'][i])

            return {'temp': t_series, 'wind': w_series, 'relHum': rh_series, 'sun': sun_series, 'rad':rad_series,
                    'rain': rain_series}

        def create_weather_stations(weather_series, lat, long, timeZone):

            # Add a rainfall station to the project
            self.rain_station = self.project.rainfall_stations.add(Name='Rain Station', Data=weather_series['rain'],
                                                             Position=(0, 0, 0))

            # Add a meteo station to the project
            self.meteo = self.project.meteo_stations.add_station(Name='Meteo Station', position=(0, 0, 0), latitude=lat,
                                                            longitude=long, timezone=timeZone)
            self.meteo.T = weather_series['temp']
            self.meteo.Tmax = self.meteo.T.reduce_max(self.meteo.T.begin, cmf.day)
            self.meteo.Tmin = self.meteo.T.reduce_min(self.meteo.T.begin, cmf.day)
            self.meteo.Windspeed = weather_series['wind']
            self.meteo.rHmean = weather_series['relHum']
            self.meteo.Sunshine = weather_series['sun']
            self.meteo.Rs = weather_series['rad']

            # Load some data
            self.meteo.Tmax = cmf.timeseries.from_file('Tmax.timeseries')
            self.meteo.Tmin = cmf.timeseries.from_file('Tmin.timeseries')
            self.meteo.Rs = cmf.timeseries.from_file('Rs.timeseries')

        def connect_weather_to_cells():
            for c in self.project.cells:
                self.rain_station.use_for_cell(c)
                self.meteo.use_for_cell(c)

        weather = read_weather(self.weather_path)
        time = create_time_series()
        weather_weries = convert_weather(weather, time)
        create_weather_stations(weather_series, weather['lat'], weather['long'], weather['timeZone'])

    def solve(self, tolerance = 1e-9):
        """Solves the model"""
        # Create solver and set time
        solver = cmf.CVodeIntegrator(self.project, tolerance)
        solver.t = cmf.Time(1,1,2017)

        # Save potential and soil moisture for each layer, start with initial conditions
        potential = []
        moisture = []
        potentialHourly = []
        moistureHourly = []

        for c in self.project.cells:
            potentialHourly.append(c.layers.potential)
            moistureHourly.append(c.layers.theta)
        potential.append(potentialHourly)
        moisture.append(moistureHourly)

        # Run solver
        for t in solver.run(solver.t, solver.t + timedelta(hours = self.analysisLenght), timedelta(hours=1)):
            potentialHourly = []
            moistureHourly = []

            for c in self.project.cells:
                potential.append(c.layers.potential)
                moisture.append(c.layers.theta)
            potential.append(potentialHourly)
            moisture.append(moistureHourly)

        # Save results
        self.results['potential'] = potential
        self.results['moisture'] = moisture

        self.solved = True
        return True

    def save_results(self, file_path):
        """Saves the computed results to a numpy file"""

        if not self.solved:
            print('Project not solved!')
            return None

        else:
            paths = []

            for res in self.results.keys():
                filePathExtention = filePath + '\\' + res
                np.save(filePathExtention, self.results[res])
                paths.append(filePathExtention + '.npy')

            return paths


def ground_temperature():
    return None


def load_cmf_files(folder):

    def load_weather():
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

    def load_tree():
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
                #print(t)
                tree_dict[str(tree_key)][str(t)] = eval(trees['tree'][str(tree_key)][str(t)])

        return tree_dict

    def load_ground():
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

    def load_mesh():
        mesh_path = None

        for f in files:
            if f.endswith('.obj'):
                mesh_path = folder + '/' + f
            else:
                pass

        return mesh_path

    files = os.listdir(folder)

    weather = load_weather()
    trees = load_tree()
    ground = load_ground()
    mesh = load_mesh()

    return weather, trees, ground, mesh
