# Imports
import shutil

# Paths
rhino_script_folder = r'C:\Users\Christian\AppData\Roaming\McNeel\Rhinoceros\5.0\scripts\livestock'
livestock_gh_folder = r'C:\Users\Christian\Dropbox\Arbejde\DTU BYG\Livestock\livestock_gh\python'

# Files
f1 = r'/__init__.py'

files = [f1]

# Folders
folder1 = r'/components'
folder2 = r'/lib'

folders = [folder1, folder2]

# Copy files
for file in files:
    shutil.copy(livestock_gh_folder + file, rhino_script_folder + file)

# copy folders
for folder in folders:
    shutil.rmtree(rhino_script_folder + folder)
    shutil.copytree(livestock_gh_folder + folder, rhino_script_folder + folder)