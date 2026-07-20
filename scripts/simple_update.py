"""
Simple update an issue on disk (copy mapping and STASH entry lines 
from UKESM1 -> UKESM1-3 and HadGEM-GC31 -> HadGEM3-GC5)
"""
import sys


if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print(f"{sys.argv[0]} [list of files to update]")
        sys.exit(1)
    
    for filename in sys.argv[1:]:
        with open(filename, 'r') as fh:
            lines = fh.readlines()
    
        newlines = []

        for line in lines:
            newlines.append(line)
            
            if "UKESM1 " in line:
                line2 = line.replace("UKESM1 ", "UKESM1-3 ")
                newlines.append(line2)
            
            if 'HadGEM3-GC31' in line:
                line2 = line.replace("HadGEM3-GC31", "HadGEM3-GC5")  # Update to UKCM2?
                newlines.append(line2)
            
        with open(filename, 'w') as fh:
            for line in newlines:
                fh.write(line)
