import clr
clr.AddReference("RhinoCommon")
import Rhino as rc
import sys
#sys.path.insert(0, r'C:\Users\Christian\Dropbox\Arbejde\DTU BYG\Livestock\Kode - Livestock\01 Python\Classes')
#import LivestockGH as ls

file = 'C:\\Users\\Christian\\Desktop\\drainMesh.3dm'
a = rc.FileIO.File3dm.Read(file)
b = a.Objects
print(b.Item)
