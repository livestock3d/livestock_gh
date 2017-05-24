# Import
import sys
sys.path.insert(0, r'C:\Users\Christian\Dropbox\Arbejde\DTU BYG\Livestock\Kode - Livestock\01 Python\Classes')
import DelphinClasses as dc
import os

# Create output text file
folder = r'C:\Users\Christian\Dropbox\Arbejde\DTU BYG\Livestock\Kode - Livestock\01 Python\Templates'
inTemp = '\\Temp.txt'
outTemp = '\\DelphinIndoorTemp.txt'
outRH = '\\DelphinIndoorRelhum.txt'
inData = '\\IndoorData.txt'

# Execution

# Open file
fileIn = open(folder + inTemp, 'r')
linesT = fileIn.readlines()
TempData = []
for d in linesT:
    TempData.append(float(d[:-1]))
fileIn.close()

fileData = open(folder + inData, 'r')
linesD = fileData.readlines()
IndoorClimateClass = str(linesD[0][:-1])
NameT = str(linesD[1][:-1])
NameRH = str(linesD[2][:-1])
Path = str(linesD[3])
fileData.close()

I = dc.IndoorClimate(TempData).EN13788(IndoorClimateClass)
dc.writeWeatherFile(I[0], 'TEMPER', 'C', NameT, Path)
dc.writeWeatherFile(I[1], 'RELHUM', '%', NameRH, Path)

os.remove(folder + inTemp)
os.remove(folder + inData)