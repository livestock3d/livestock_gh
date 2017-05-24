# Import
import sys
sys.path.insert(0, r'C:\Users\Christian\Dropbox\Arbejde\DTU BYG\Livestock\Kode - Livestock\01 Python\Classes')
import DelphinClasses as dc


# Create output text file
file = r'C:\Users\Christian\Dropbox\Arbejde\DTU BYG\Livestock\Kode - Livestock\01 Python\Templates\DelphinDiscretizationTemplate.txt'

# Execution



x = dc.Subdivision(Width,MinimumDivision, StretchFactor)

# Write in file
file_obj = open(file, 'w')
for i in x:
    file_obj.write(str(i)+'\n')
file_obj.close()
