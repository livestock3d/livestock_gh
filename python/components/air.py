__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import subprocess
import os

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


class NewAirConditions(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Mesh',
                        'description': 'Ground Mesh',
                        'access': 'item',
                        'default_value': None},

                    1: {'name': 'Evapotranspiration',
                        'description': 'Evapotranspiration in m^3/day. '
                                       '\nEach tree branch should represent one time unit, with all the cell values to '
                                       'that time.',
                        'access': 'tree',
                        'default_value': None},


                    2: {'name': 'AirTemperature',
                        'description': 'Air temperature in C',
                        'access': 'list',
                        'default_value': None},

                    3: {'name': 'AirRelativeHumidity',
                        'description': 'Relative Humidity in %',
                        'access': 'list',
                        'default_value': None},

                    4: {'name': 'WindSpeed',
                        'description': 'Wind speed in m/s',
                        'access': 'list',
                        'default_value': None},

                    5: {'name': 'AirBoundaryHeight',
                        'description': 'Top of the air column in m. '
                                       '\nDefault is set to 10m',
                        'access': 'item',
                        'default_value': 10},

                    6: {'name': 'InvestigationHeight',
                        'description': 'Height at which the new air temperature and relative humidity should be '
                                       'calculated. '
                                       '\nDefault is set to 1.1m',
                        'access': 'item',
                        'default_value': 1.1},

                    7: {'name': 'CPUs',
                        'description': 'Number of cpus to perform the computation on.'
                                       '\nDefault is set to 2',
                        'access': 'item',
                        'default_value': 2},

                    8: {'name': 'ResultFolder',
                        'description': 'Folder where the result files should be saved',
                        'access': 'item',
                        'default_value': None},

                    9: {'name': 'Run',
                        'description': 'Run the component',
                        'access': 'item',
                        'default_value': None}
                    }

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},

                    1: {'name': 'NewTemperature',
                        'description': 'New temperature in C.'},

                    2: {'name': 'NewRelativeHumidity',
                        'description': 'New relative humidity in %.'},

                    3: {'name': 'LatentHeatFlux',
                        'description': 'Computed latent heat flux in J/h.'},

                    4: {'name': 'UsedVapourFlux',
                        'description': 'Vapour flux used to alter the temperature and relative humidity in kg/h.'},
                    }

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 24
        self.mesh = None
        self.evapotranspiration = None
        self.heat_flux = None
        self.air_temperature = None
        self.air_relhum = None
        self.boundary_height = None
        self.investigation_height = None
        self.cpus = None
        self.folder = None
        self.run_component = None
        self.area = None
        self.py_exe = gh_misc.get_python_exe()
        self.checks = [False, False, False, False, False, False, False]
        self.results = {'temperature': [],
                        'relative_humidity': [],
                        'heat_flux': [],
                        'vapour_flux': []}

    def check_inputs(self):
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        self.checks = True

    def config(self):
        """
        Generates the Grasshopper component.
        """

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, mesh, evapotranspiration, temperature, relhum, wind_speed, boundary_height,
                   investigation_height, cpus, folder, run):

        """
        Gathers the inputs and checks them.

        :param mesh: Surface mesh.
        :param evapotranspiration: Vapour flux
        :param temperature: Outdoor temperature
        :param relhum: Relative humidity
        :param wind_speed: Wind speed
        :param boundary_height: Height of the air columns.
        :param investigation_height: Investigation height
        :param cpus: Number of CPUs
        :param folder: Folder where the result files should be saved.
        :param run: Whether or not to run the component.
        """

        # Gather data
        self.mesh = mesh
        self.evapotranspiration = gh_misc.tree_to_list(evapotranspiration)
        self.air_temperature = temperature
        self.air_relhum = relhum
        self.wind_speed = wind_speed
        self.boundary_height = self.add_default_value(boundary_height, 5)
        self.investigation_height = self.add_default_value(investigation_height, 6)
        self.cpus = self.add_default_value(cpus, 7)
        self.folder = self.add_default_value(folder, 8) + '/NewAir'
        self.run_component = self.add_default_value(run, 9)

        # Run checks
        self.check_inputs()


    def get_mesh_data(self):
        """
        Extracts the data needed from the mesh.
        """

        mesh_faces = gh_geo.get_mesh_faces(self.mesh)

        self.area = [rs.MeshArea(face)[1]
                     for face in mesh_faces]

    def write_files(self):
        """
        Write the files.
        """

        write_folder = self.folder
        files_written = []

        if not os.path.exists(write_folder):
            os.mkdir(write_folder)

        # evapotranspiration
        vapour_file = 'vapour_flux.txt'
        vapour_obj = open(write_folder + '/' + vapour_file, 'w')
        for row in self.evapotranspiration:
            vapour_obj.write(','.join(str(element)
                                      for element in row)
                             + '\n'
                             )
        vapour_obj.close()
        files_written.append(vapour_file)


        # temperature
        temp_file = 'temperature.txt'
        temp_obj = open(write_folder + '/' + temp_file, 'w')
        temp_obj.write(','.join(str(elem)
                                for elem in self.air_temperature))
        temp_obj.close()
        files_written.append(temp_file)

        # relhum
        relhum_file = 'relative_humidity.txt'
        relhum_obj = open(write_folder + '/' + relhum_file, 'w')
        relhum_obj.write(','.join(str(elem)
                                  for elem in self.air_relhum))
        relhum_obj.close()
        files_written.append(relhum_file)

        # relhum
        wind_file = 'wind_speed.txt'
        wind_obj = open(write_folder + '/' + wind_file, 'w')
        wind_obj.write(','.join(str(elem)
                                  for elem in self.wind_speed))
        wind_obj.close()
        files_written.append(wind_file)

        # boundary_height and investigation_height
        height_file = 'heights.txt'
        height_obj = open(write_folder + '/' + height_file, 'w')
        height_obj.write(str(self.boundary_height) + '\n'
                         + str(self.investigation_height))
        height_obj.close()
        files_written.append(height_file)

        # area
        area_file = 'area.txt'
        area_obj = open(write_folder + '/' + area_file, 'w')
        area_obj.write(','.join(str(elem)
                                for elem in self.area))
        area_obj.close()
        files_written.append(area_file)

        # cpu
        cpu_file = 'cpu.txt'
        cpu_obj = open(write_folder + '/' + cpu_file, 'w')
        cpu_obj.write(str(self.cpus))
        cpu_obj.close()
        files_written.append(cpu_file)

        # Template
        files_written.append(template.pick_template('new_air', write_folder))

        return True

    def do_case(self):
        """
        Runs the case. Spawns a subprocess to run either the local or ssh template.
        """

        template_to_run = self.folder + '/new_air_conditions_template.py'

        # Run template
        thread = subprocess.Popen([self.py_exe, template_to_run])
        thread.wait()
        thread.kill()

        return True

    def load_results(self):
        """
        Loads the results from the results files and adds them to self.results.
        """

        self.results['temperature'], \
        self.results['relative_humidity'], \
        self.results['heat_flux'] = load_new_air_results(self.folder)

        return True

    def run(self):
        """
        In case all the checks have passed and run is True the component runs.
        The following functions are run - in this order.
        get_mesh_data()
        write_files()
        do_case()
        load_results()
        """

        if self.checks and self.run_component:
            self.get_mesh_data()
            self.write_files()
            self.do_case()
            self.load_results()


class LoadAirResult(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'ResultFolder',
                        'description': 'Path to result folder.',
                        'access': 'item',
                        'default_value': None},

                    1: {'name': 'LoadResult',
                        'description': 'Run component',
                        'access': 'item',
                        'default_value': False}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},

                    1: {'name': 'NewTemperature',
                        'description': 'New temperature in C.'},

                    2: {'name': 'NewRelativeHumidity',
                        'description': 'New relative humidity in %.'},

                    3: {'name': 'Latent Heat Flux',
                        'description': 'Latent Heat Flux in J/h'}
                    }

        self.inputs = inputs()
        self.outputs = outputs()
        self.component_number = 26
        self.folder = None
        self.load = None
        self.checks = False
        self.results = {'temperature': [],
                        'relative_humidity': [],
                        'heat_flux': [],
                        'vapour_flux': []}
        self.result_path = None

    def check_inputs(self):
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        if self.folder:
            self.checks = True
        else:
            warning = 'Insert result path'
            self.add_warning(warning)

    def config(self):
        """
        Generates the Grasshopper component.
        """

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, path, load):
        """
        Gathers the inputs and checks them.
        :param path: Path for result folder.
        :param load: Load results files.
        """

        # Gather data
        self.folder = path
        self.load = self.add_default_value(load, 1)

        # Run checks
        self.check_inputs()

    def load_result(self):
        """
        Loads the results from the results files and adds them to self.results.
        """

        self.results['temperature'], self.results['relative_humidity'], self.results[
            'heat_flux'] = load_new_air_results(self.folder)

        return True

    def run(self):
        """
        In case all the checks have passed the component runs.
        The following functions are run:
        load_results()
        The results are converted into a Grasshopper Tree structure.
        """

        if self.checks and self.load:
            self.load_result()


def load_new_air_results(folder):
    """
    Loads the results from the results files and adds them to self.results.
    """

    temp_results = '/temperature_results.txt'
    relhum_results = '/relative_humidity_results.txt'
    heat_results = '/latent_heat_flux_results.txt'

    # Temperature
    new_temp = open(folder + temp_results, 'r')
    new_temperature = gh_misc.list_to_tree([[float(element)
                                             for element in line.strip().split(',')]
                                            for line in new_temp.readlines()])
    new_temp.close()

    # Relative Humidity
    new_relhum = open(folder + relhum_results, 'r')
    new_relative_humidity = gh_misc.list_to_tree([[float(element)
                                                   for element in line.strip().split(',')]
                                                  for line in new_relhum.readlines()])
    new_relhum.close()

    # Relative Humidity
    new_heat = open(folder + heat_results, 'r')
    new_heat_flux = gh_misc.list_to_tree([[float(element)
                                           for element in line.strip().split(',')]
                                          for line in new_heat.readlines()])
    new_relhum.close()

    return (new_temperature, new_relative_humidity, new_heat_flux)
