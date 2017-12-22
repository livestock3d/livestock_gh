__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.1.0"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import os
import shutil
import subprocess

# Livestock imports
from component import GHComponent
import livestock.lib.ssh as ssh
import livestock.lib.misc as gh_misc

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
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

        if isinstance(self.py_exe, str):
            self.checks = True
        else:
            warning = 'Path should be a string'
            self.add_warning(warning)

    def config(self):
        """
        Generates the Grasshopper component.
        """

        self.config_component(self.component_number)

    def run_checks(self, py_exe):
        """
        Gathers the inputs and checks them.
        :param py_exe: Path to python.exe
        """

        # Gather data
        self.py_exe = py_exe

        # Run checks
        self.check_inputs()

    def run(self):
        """
        In case all the checks have passed the component runs.
        It prints the python.exe path and creates a scriptcontext.sticky with the path.
        """

        if self.checks:
            print('Python Executor is set to: ' + self.py_exe)

            sc.sticky['PythonExe'] = self.py_exe


class SSHConnection(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'IP',
                        'description': 'IP Address for SSH connection',
                        'access': 'item',
                        'default_value': None},
                    1: {'name': 'Port',
                        'description': 'Port for SSH connection',
                        'access': 'item',
                        'default_value': None},
                    2: {'name': 'Username',
                        'description': 'Username for SSH connection',
                        'access': 'item',
                        'default_value': None},
                    3: {'name': 'Password',
                        'description': 'Password for SSH connection',
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
        """
        Checks inputs and raises a warning if an input is not the correct type.
        """

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
        """
        Generates the Grasshopper component.
        """

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, ip, port, user, pw):
        """
        Gathers the inputs and checks them.
        :param ip: IP for SSH connection
        :param port: Port for SSH connection
        :param user: Username for SSH connection
        :param pw: Password for SSH connection
        """

        # Gather data
        self.ip = ip
        self.port = port
        self.user = user
        self.password = pw

        # Run checks
        self.check_inputs()

    def run(self):
        """
        In case all the checks have passed the component runs.
        It prints out the IP, Port and Username and creates a
        scriptcontext.sticky all four inputs.
        """

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
                        'access': 'list',
                        'default_value': None},
                    2: {'name': 'CPUs',
                        'description': 'Number of CPUs to perform each command on',
                        'access': 'list',
                        'default_value': None},
                    3: {'name': 'Run',
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
        self.cpus = None
        self.run_component = None
        self.ssh_path = ssh.ssh_path
        self.checks = [False, False, False]
        self.results = None

    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, directory, commands, cpus, run):

        # Gather data
        self.directory = directory
        self.commands = commands
        self.cpus = cpus
        self.run_component = self.add_default_values(run, 2)

        # Run checks
        self.check_inputs()

    def write(self):

        # Initialize
        ssh.clean_ssh_folder()
        files_written = []
        file_run = ['cfd_ssh_template.py']
        files_written.append('cfd_ssh_template.py')

        # Write commands file
        gh_misc.write_file([self.commands, self.cpus], self.ssh_path, 'cfd_commands')
        files_written.append('cfd_commands.txt')

        # Zip and move case files
        shutil.make_archive(self.ssh_path + '/cfd_case', 'zip', self.directory)

        # SSH commands
        ssh_cmd = ssh.get_ssh()
        ssh_cmd['file_transfer'] = ','.join(files_written)
        ssh_cmd['file_run'] = ','.join(file_run)
        ssh_cmd['file_return'] = 'solved_cfd_case.zip'
        ssh_cmd['template'] = 'cfd_ssh'
        ssh.write_ssh_commands(ssh_cmd)

        return True

    def run_template(self):

        # Python executor
        py_exe = gh_misc.get_python_exe()

        # SSH template path
        ssh_template = ssh.ssh_path + '/ssh_template.py'

        # Run template
        thread = subprocess.Popen([py_exe, ssh_template])
        thread.wait()
        thread.kill()

    def run(self):
        if self.checks and self.run_component:
            self.write()
            self.run_template()
