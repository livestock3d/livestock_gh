__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import os

# Livestock imports
from comp.component import GHComponent
from win.templates import pick_template
import gh.misc as gh_misc

# Grasshopper imports
import scriptcontext as sc

# -------------------------------------------------------------------------------------------------------------------- #
# Livestock Miscellaneous Components


class PythonExecutor(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'PythonPath',
                        'description': 'Path to python.exe',
                        'access': 'item',
                        'default_value': None}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.description = 'Path to python executor'
        self.component_number = 0
        self.py_exe = None
        self.checks = False
        self.results = None

    def check_inputs(self):
        if isinstance(self.py_exe, str):
            self.checks = True
        else:
            warning = 'Path should be a string'
            self.add_warning(warning)

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, py_exe):

        # Gather data
        self.py_exe = py_exe

        # Run checks
        self.check_inputs()

    def run(self):
        if self.checks:
            print('Python Executor is set to: ' + self.py_exe)

            sc.sticky['PythonExe'] = self.py_exe


class SSHConnection(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'IP',
                        'description': 'IP Address to connection',
                        'access': 'item',
                        'default_value': None},
                    1: {'name': 'Port',
                        'description': 'Port for connection',
                        'access': 'item',
                        'default_value': None},
                    2: {'name': 'Username',
                        'description': 'Username for connection',
                        'access': 'item',
                        'default_value': None},
                    3: {'name': 'Password',
                        'description': 'Password for connection',
                        'access': 'item',
                        'default_value': None}
                    }

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.description = 'Setup SSH connection.\n' \
                           'Icon based on art from Arthur Shlain from the Noun Project.'
        self.component_number = 1
        self.ip = None
        self.port = None
        self.user = None
        self.password = None
        self.checks = [False, False, False, False]
        self.results = None

    def check_inputs(self):
        warnings = []

        if isinstance(self.ip, str):
            self.checks[0] = True
        else:
            warnings.append('IP should be a string')

        if isinstance(self.port, str):
            self.checks[1] = True
        else:
            warnings.append('Port should be a string')

        if isinstance(self.user, str):
            self.checks[2] = True
        else:
            warnings.append('Username should be a string')

        if isinstance(self.password, str):
            self.checks[3] = True
        else:
            warnings.append('Password should be a string')

        if warnings:
            for warn in warnings:
                self.add_warning(warn)
        else:
            self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, ip, port, user, pw):

        # Gather data
        self.ip = ip
        self.port = port
        self.user = user
        self.password = pw

        # Run checks
        self.check_inputs()

    def run(self):
        if self.checks:
            print('SSH connection is set to:'
                  '\nIP: ' + str(self.ip) +
                  '\nPort: ' + str(self.port) +
                  '\nUser: ' + str(self.user))
            print('')
            print('Open Bash and run:'
                  '\nsudo service ssh --full-restart')

            sc.sticky['SSH'] = {'ip': self.ip, 'port': self.port, 'user': self.user, 'password': self.password}


class CFDonSSH(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Directory',
                        'description': 'Directory where the OpenFoam files are located',
                        'access': 'item',
                        'default_value': None},
                    1: {'name': 'Commands',
                        'description': 'OpenFoam Commands to run',
                        'access': 'item',
                        'default_value': None},
                    2: {'name': 'Run',
                        'description': 'Runs the component',
                        'access': 'item',
                        'default_value': False}
                    }

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'}}

        self.inputs = inputs()
        self.outputs = outputs()
        self.description = 'Setup SSH connection'
        self.component_number = 22
        self.directory = None
        self.commands = None
        self.run_component = None
        self.checks = [False, False]
        self.results = None

    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, directory, commands, run):

        # Gather data
        self.directory = directory
        self.commands = commands
        self.run_component = self.add_default_values(run, 2)

        # Run checks
        self.check_inputs()


    def collect_directory_contents(self):
        os.listdir(self.directory)


    def run_template(self):

        data = []
        livestock_ssh_path = r'C:\livestock\python\ssh'

        gh_misc.write_file(data, livestock_ssh_path, 'cfd_data')

        pick_template('cfd', livestock_ssh_path)


    def run(self):
        if self.checks and self.run_component:
            self.run_template()
