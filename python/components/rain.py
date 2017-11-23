__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.1.0"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import subprocess

# Livestock imports
import livestock.lib.ssh as ssh
import livestock.lib.geometry as gh_geo
from component import GHComponent
import livestock.lib.misc as gh_misc

# Grasshopper imports


# -------------------------------------------------------------------------------------------------------------------- #
# Livestock Rain & Flow Functions and Classes

class MeshDrainPaths(GHComponent):

    def __init__(self, ghenv):
        GHComponent.__init__(self, ghenv)

        def inputs():
            return {0: {'name': 'Mesh',
                        'description': 'Mesh to preform computation on.',
                        'access': 'item',
                        'default_value': None},
                    1: {'name': 'CPUs',
                        'description': "Number of cpu's to run the component on - Default is set to 1.",
                        'access': 'item',
                        'default_value': 1},
                    2: {'name': 'Run',
                        'description': 'Activates the component',
                        'access': 'item',
                        'default_value': False}}

        def outputs():
            return {0: {'name': 'readMe!',
                        'description': 'In case of any errors, it will be shown here.'},
                    1: {'name': 'NewMesh',
                        'description': 'New mesh as processed by PyMesh.'},
                    2: {'name': 'DrainCurves',
                        'description': 'Curves constructed through the drain positions of each particle.'},
                    3: {'name': 'EndPoints',
                        'description': 'The final position of the particles.'},
                    4: {'name': 'DrainFaces',
                        'description': 'Faces where the drain paths go through.'}
                    }

        self.inputs = inputs()
        self.outputs = outputs()
        self.description = 'Simulates drainage paths on a surface mesh. The paths are based on a geometric computation'
        self.component_number = 2
        self.mesh = None
        self.cpus = None
        self.run_component = None
        self.ssh_path = ssh.ssh_path
        self.checks = False
        self.results = {'new_mesh': None, 'drain_curves': None, 'end_points': None, 'drain_faces': None}

    def check_inputs(self):
        self.checks = True

    def config(self):

        # Generate Component
        self.config_component(self.component_number)

    def run_checks(self, mesh, cpus, run):

        # Gather data
        self.mesh = mesh
        self.cpus = self.add_default_value(cpus, 1)
        self.run_component = self.add_default_value(run, 2)

        # Run checks
        self.check_inputs()

    def write(self, doc_):

        # Initialize
        ssh.clean_ssh_folder()
        files_written = []
        file_run = ['drain_mesh_template.py']
        files_written.append('drain_mesh_template.py')

        # Export mesh
        gh_geo.bake_export_delete(self.mesh, self.ssh_path, 'drain_mesh', '.obj', doc_)
        files_written.append('drain_mesh.obj')

        # Write cpu file
        gh_misc.write_file(int(self.cpus), self.ssh_path, 'cpu')
        files_written.append('cpu.txt')

        # SSH commands
        ssh_cmd = ssh.get_ssh()
        ssh_cmd['file_transfer'] = ','.join(files_written)
        ssh_cmd['file_run'] = ','.join(file_run)
        ssh_cmd['file_return'] = 'new_drain_mesh.obj,drain_points.txt,drain_faces.txt'
        ssh_cmd['template'] = 'drain_mesh'
        ssh.write_ssh_commands(ssh_cmd)

        return True

    def do_case(self):

        # Python executor
        py_exe = gh_misc.get_python_exe()

        # SSH template path
        ssh_template = ssh.ssh_path + '/ssh_template.py'

        # Run template
        thread = subprocess.Popen([py_exe, ssh_template])
        thread.wait()
        thread.kill()

    def load_results(self):
        """Loads the results"""

        # Helper function
        def drain_faces():

            file_obj = open(self.ssh_path + "\\drain_faces.txt", 'r')
            lines = file_obj.readlines()
            faces = []
            for l in lines:
                v = []
                for a in l.split('\t')[:-1]:
                    v.append(int(a))
                faces.append(v)
            file_obj.close()

            return faces

        # Get the results
        self.results['new_mesh'] = gh_geo.import_obj(self.ssh_path + '\\new_drain_mesh.obj')
        pts = gh_geo.load_points(self.ssh_path + '\\drain_points.txt')
        self.results['drain_curves'], self.results['end_points'] = gh_geo.make_curves_from_points(pts)
        self.results['drain_faces'] = gh_misc.list_to_tree(drain_faces())

    def run(self, doc):
        if self.checks and self.run_component:

            # Write files and run template
            self.write(doc)
            self.do_case()

            # Load result files and delete files afterwards
            self.load_results()
            ssh.clean_ssh_folder()
