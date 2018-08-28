x = 2

import subprocess

path = r'C:\Users\Christian\Dropbox\Arbejde\DTU BYG\Livestock\Kode - Livestock\01 Python\Tests'
file = path + '\\Transfer_Test2.py'

A = subprocess.Popen(file, executable='C:\Program Files\Anaconda3\python.exe', stdout=subprocess.PIPE)
out = A.stdout
print(out)