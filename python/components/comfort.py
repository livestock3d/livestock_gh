__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import subprocess

# Rhino and Grasshopper imports
#import rhinoscriptsyntax as rs

# Livestock imports
from livestock.components.component import GHComponent
import livestock.lib.misc as gh_misc
import livestock.lib.ssh as ssh
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

                    2: {'name': 'HeatFlux',
                        'description': 'HeatFlux in MJ/m^2day. '
                                       '\nEach tree branch should represent one time unit, with all the cell values to '
                                       'that time.',
                        'access': 'tree',
                        'default_value': None},

                    3: {'name': 'AirTemperature',
                        'description': 'Air temperature in C',
                        'access': 'list',
                        'default_value': None},

                    4: {'name': 'AirRelativeHumidity',
                        'description': 'Relative Humidity in -',
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

                    8: {'name': 'ThroughSSH',
                        'description': 'Number of cpus to perform the computation on.'
                                       '\nDefault is set to False',
                        'access': 'item',
                        'default_value': False},

                    9: {'name': 'Run',
                        'description': 'Run the component',
                        'access': 'item',
                        'default_value': False}
                    }

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},
                    1: {'name': 'NewTemperature',
                        'description': 'New temperature in C.'},
                    2: {'name': 'NewRelativeHumidity',
                        'description': 'New relative humidity in -.'}
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
        self.thorugh_ssh = None
        self.run_component = None
        self.area = None
        self.py_exe = gh_misc.get_python_exe()
        self.ssh_cmd = ssh.get_ssh()
        self.checks = [False, False, False, False, False, False, False]
        self.results = {'temperature': [], 'relative_humidity': []}

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

    def run_checks(self, mesh, evapotranspiration, heat_flux, temperature, relhum, boundary_height,
                   investigation_height, cpus, ssh_, run):

        """
        Gathers the inputs and checks them.
        :param mesh: Surfacce mesh.
        :param evapotranspiration: Vapour flux
        :param heat_flux: Heat flux
        :param temperature: Outdoor temperature
        :param relhum: Relative humidity
        :param boundary_height: Height of the air columns.
        :param investigation_height: Investigation height
        :param cpus: Number of CPUs
        :param ssh_: If computation should be done over SSH.
        :param run: Whether or not to run the component.
        """

        # Gather data
        self.mesh = mesh
        self.evapotranspiration = gh_misc.tree_to_list(evapotranspiration)
        self.heat_flux = gh_misc.tree_to_list(heat_flux)
        self.air_temperature = temperature
        self.air_relhum = relhum
        self.boundary_height = self.add_default_value(boundary_height, 5)
        self.investigation_height = self.add_default_value(investigation_height, 6)
        self.cpus = self.add_default_value(cpus, 7)
        self.thorugh_ssh = self.add_default_value(ssh_, 8)
        self.run_component = self.add_default_value(run, 9)

        # Run checks
        self.check_inputs()

    def convert_units(self):
        """
        Converts heat and vapour flux to the correct units.
        """

        def convert_heat_flux(heat_list, area):

            def converter(value, area_):
                # MJ/m2day -> J/h
                # 24 h/day, 1e6 J/MJ, multiply by area
                new_value = float(value) * float(area_) * 24/10**6
                return new_value

            converted_list = [[converter(heat_row[i], area[i])
                               for i in range(0, len(heat_row))]
                              for heat_row in heat_list]

            return converted_list

        def convert_vapour_flux(vapour_list):

            def converter(value):
                # m^3/day -> kg/s
                # 24h*60min*60s = 86400 s/day, 998.2 kg/m^3 at 20C
                new_value = float(value) / 86400.0 * 998.2
                return new_value

            converted_list = [[converter(vapour)
                               for vapour in vapour_row]
                              for vapour_row in vapour_list]

            return converted_list

        self.evapotranspiration = convert_vapour_flux(self.evapotranspiration)
        self.heat_flux = convert_heat_flux(self.heat_flux, self.area)

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

        if self.thorugh_ssh:
            # Write SSH case
            write_folder = ssh.ssh_path
            ssh.clean_ssh_folder()
            files_written = []

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

            # heat_flux
            heat_file = 'heat_flux.txt'
            heat_obj = open(write_folder + '/' + heat_file, 'w')
            for row in self.heat_flux:
                heat_obj.write(','.join(str(element)
                                        for element in row)
                               + '\n'
                               )
            heat_obj.close()
            files_written.append(heat_file)

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

            # SSH
            temp_results = 'temperature_results.txt'
            relhum_results = 'relative_humidity_results.txt'

            file_run = ['new_air_conditions_template.py']
            file_transfer = files_written + file_run
            file_return = [temp_results, relhum_results]

            self.ssh_cmd['file_transfer'] = ','.join(file_transfer)
            self.ssh_cmd['file_run'] = ','.join(file_run)
            self.ssh_cmd['file_return'] = ','.join(file_return)
            self.ssh_cmd['template'] = 'new_air'

            ssh.write_ssh_commands(self.ssh_cmd)

        else:
            # Write local case
            write_folder = ssh.local_path
            ssh.clean_local_folder()
            files_written = []

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

            # heat_flux
            heat_file = 'heat_flux.txt'
            heat_obj = open(write_folder + '/' + heat_file, 'w')
            for row in self.heat_flux:
                heat_obj.write(','.join(str(element)
                                        for element in row)
                               + '\n'
                               )
            heat_obj.close()
            files_written.append(heat_file)

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

        if self.thorugh_ssh:
            template_to_run = ssh.ssh_path + '/ssh_template.py'
        else:
            template_to_run = ssh.local_path + '/new_air_conditions_template.py'

        # Run template
        thread = subprocess.Popen([self.py_exe, template_to_run])
        thread.wait()
        thread.kill()

        return True

    def load_results(self):
        """
        Loads the results from the results files and adds them to self.results.
        """

        temp_results = '/temperature_results.txt'
        relhum_results = '/relative_humidity_results.txt'

        if self.thorugh_ssh:
            folder = ssh.ssh_path
        else:
            folder = ssh.local_path

        # Temperature
        new_temp = open(folder + temp_results, 'r')
        self.results['temperature'] = gh_misc.list_to_tree([[float(element)
                                                             for element in line.strip().split(',')]
                                                            for line in new_temp.readlines()])
        new_temp.close()

        # Relative Humidity
        new_relhum = open(folder + relhum_results, 'r')
        self.results['relative_humidity'] = gh_misc.list_to_tree([[float(element)
                                                                   for element in line.strip().split(',')]
                                                                  for line in new_relhum.readlines()])
        new_relhum.close()

        if self.thorugh_ssh:
            ssh.clean_ssh_folder()
        else:
            ssh.clean_local_folder()

        return True

    def run(self):
        """
        In case all the checks have passed and run is True the component runs.
        The following functions are run - in this order.
        get_mesh_data()
        convert_units()
        write_files()
        do_case()
        load_results()
        """

        if self.checks and self.run_component:
            self.get_mesh_data()
            self.convert_units()
            self.write_files()
            self.do_case()
            self.load_results()


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
