__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.1.0"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import shutil
import os

# Livestock imports
import misc as gh_misc
import templates

# Grasshopper imports
import scriptcontext as sc


# -------------------------------------------------------------------------------------------------------------------- #
# Grasshopper SSH functions

ssh_path = r'C:\livestock\python\ssh'


def get_ssh():
    ip = str(sc.sticky["SSH"]['ip'])
    port = str(sc.sticky["SSH"]['port'])
    user = str(sc.sticky["SSH"]['user'])
    pw = str(sc.sticky["SSH"]['password'])

    ssh_dict = {'ip': ip, 'port': port, 'user': user, 'password': pw}

    return ssh_dict


def clean_ssh_folder():

    if os.path.isdir(ssh_path):
        for file in os.listdir(ssh_path):
            os.remove(ssh_path + '/' + file)
    else:
        os.mkdir(ssh_path)


def write_ssh_commands(ssh_dict):
    """
    Write the files need for Livestock SSH connection to work.
    :param ssh_dict: Dictionary with all SSH information. Needs to be on the following form:
    {'ip': string, 'user': string, 'port': string, 'password': 'string', 'file_transfer': list of strings,
    'file_run': list of strings, 'file_return': list of strings, 'template': string}
    :return:
    """

    # Write SSH commands
    gh_misc.write_file([ssh_dict['ip'],
                        ssh_dict['port'],
                        ssh_dict['user'],
                        ssh_dict['password'],
                        ssh_dict['file_transfer'],
                        ssh_dict['file_run'],
                        ssh_dict['file_return']
                        ],
                        ssh_path,
                        'in_data')

    # Write templates
    templates.ssh_template(ssh_path)
    templates.pick_template(ssh_dict['template'], ssh_path)

    return True