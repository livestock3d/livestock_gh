# Import
import sys
sys.path.insert(0, "/mnt/c/Users/Christian/Dropbox/Arbejde/DTU BYG/Livestock/Kode - Livestock/01 Python/Classes/")
import RainClasses as rc

print('reached template')
poolPath = "/mnt/c/Users/Christian/Dropbox/Arbejde/DTU BYG/Livestock/Kode - Livestock/01 Python/Templates"
b = rc.drainPools(poolPath)
sys.stdout = open('out.txt','w')