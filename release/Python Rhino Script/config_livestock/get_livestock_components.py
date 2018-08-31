import shutil
import os

path = r'C:\Users\Christian\AppData\Roaming\Grasshopper\UserObjects'
livestock_path = r'C:\Users\Christian\Dropbox\Arbejde\DTU BYG\Livestock\livestock_gh\grasshopper\components'
copied_files = []

for file in os.listdir(path):
    if file.startswith('Livestock'):
        shutil.copyfile(path + '/' + file, livestock_path + '/' + file)
        copied_files.append(file)

print('Copied ' + str(len(copied_files)) + ' files')
print('Files copied:')
for f in copied_files:
    print('\t' + f)
