__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# ---------------------------------------------------------------------------- #
# Imports

# Module imports
import subprocess

# Livestock imports
import livestock.lib.ssh as ssh
import livestock.lib.geometry as gh_geo
from component import GHComponent
import livestock.lib.misc as gh_misc
from livestock.lib.templates import pick_template

# Grasshopper imports


# ---------------------------------------------------------------------------- #
# Livestock Rain & Flow Functions and Classes

class MeshDrainPaths(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: component.inputs('required'),

                    1: {'name': 'Mesh',
                        'description': 'Mesh to preform computation on.',
                        'access': 'item',
                        'default_value': None},

                    2: {'name': 'Run',
                        'description': 'Activates the component',
                        'access': 'item',
                        'default_value': False},

                    3: component.inputs('optional'),

                    4: {'name': 'CPUs',
                        'description': "Number of cpu's to run the component "
                                       "on.\nDefault is set to 1.",
                        'access': 'item',
                        'default_value': 1},

                    5: {'name': 'SSH',
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

                    1: {'name': 'DrainCurves',
                        'description': 'Curves constructed through the drain '
                                       'positions of each particle.'},

                    2: {'name': 'EndPoints',
                        'description': 'The final position of the particles.'}
                    }

        # Component Config
        self.inputs = inputs()
        self.outputs = outputs()
        self.description = 'Simulates drainage paths on a surface mesh. ' \
                           'The paths are based on a geometric computation, ' \
                           'which looks for the lowest neighbouring mesh face' \
                           ' as the location for where to the water will run.'
        self.component_number = 2
        self.checks = False
        self.results = {'drain_curves': None, 'end_points': None, }

        # Data Parameters
        self.mesh = None
        self.cpus = None
        self.run_component = None
        self.ssh = None
        self.case_path = None

        # Additional Parameters
        self.py_exe = gh_misc.get_python_exe()
        self.written = False


    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, mesh, run, cpus, ssh):

        # Gather data
        self.mesh = mesh
        self.run_component = self.add_default_value(run, 2)
        self.cpus = self.add_default_value(cpus, 4)
        self.ssh = self.add_default_value(ssh, 5)
        self.case_path = self.update_case_path()

        # Run checks
        self.check_inputs()

    def update_case_path(self):
        if self.ssh:
            ssh.clean_ssh_folder()
            return ssh.ssh_path

        else:
            ssh.clean_local_folder()
            return ssh.local_path

    def write(self, doc_):

        # Initialize
        ssh.clean_ssh_folder()
        files_written = []
        file_run = ['drain_mesh_template.py']
        files_written.append('drain_mesh_template.py')

        # Export mesh
        gh_geo.bake_export_delete(self.mesh, self.case_path,
                                  'drain_mesh', '.obj', doc_)
        files_written.append('drain_mesh.obj')

        # Write cpu file
        gh_misc.write_file(int(self.cpus), self.case_path, 'cpu')
        files_written.append('cpu.txt')

        # SSH commands
        if self.ssh:
            ssh_cmd = write_ssh_files(files_written)
            ssh.write_ssh_commands(ssh_cmd)
        else:
            pick_template('cmf', self.case_path)

        self.written = True

    @staticmethod
    def write_ssh_files(files_written_):

        # SSH commands
        ssh_command = ssh.get_ssh()

        file_transfer = files_written_
        file_run = ['drain_mesh_template.py']
        file_return = ['results.json']

        ssh_command['file_transfer'] = ','.join(file_transfer) + \
                                       ',drain_mesh_template.py'
        ssh_command['file_run'] = ','.join(file_run)
        ssh_command['file_return'] = ','.join(file_return)
        ssh_command['template'] = 'drain_mesh'

        ssh.write_ssh_commands(ssh_command)

        return ssh_command

    def do_case(self):
        """Spawns a new subprocess, that runs the ssh template."""

        if self.ssh:
            template = ssh.ssh_path + '/ssh_template.py'
        else:
            template = self.case_path + '/drain_mesh_template.py'

        # Run template
        thread = subprocess.Popen([self.py_exe, template])
        thread.wait()
        thread.kill()

        return True

    def load_results(self):
        """Loads the results"""

        ssh_result = ssh.ssh_path + '/results.json'
        result_path = self.case_path + '/results.json'

        if os.path.exists(ssh_result):
            copyfile(ssh_result, result_path)
            ssh.clean_ssh_folder()

        # Get the results
        pts = gh_geo.load_points(result_path)
        (self.results['drain_curves'],
         self.results['end_points']) = gh_geo.make_curves_from_points(pts)

    def run(self, doc):
        if self.checks and self.run_component:

            # Write files and run template
            self.write(doc)
            self.do_case()

            # Load result files and delete files afterwards
            self.load_results()
