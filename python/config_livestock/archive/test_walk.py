from os import walk
import os
import shutil

mypath = r'C:\ODS\simpleExternalCFD\foam'

f = []
for (dirpath, dirnames, filenames) in walk(mypath):
    f.extend(filenames)
    break

print(f)

print(os.listdir(mypath))

output_filename = r'C:\Users\Christian\Desktop\test_cmf\test_zip'
shutil.make_archive(output_filename, 'zip', mypath)

shutil.unpack_archive(output_filename + '.zip', r'C:\Users\Christian\Desktop\test_cmf')
#os.remove(output_filename + '.zip')