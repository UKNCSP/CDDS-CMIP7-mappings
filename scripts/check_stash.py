"""
The issue file for each variable contains Expression lines containing the mapping from 
STASH codes to the variable, along with a list of STASH entries.  This script checks
that all STASH codes in the Expression lines are in the STASH entries, and vice versa.
"""
import sys
import re

if __name__ == '__main__':

    length = len('m01sxxiyyy')  # length of a STASH code.
    
    if len(sys.argv) <= 1:
        print(f"{sys.argv[0]} [list of issue files to check]")
        sys.exit(1)
    
    for filename in sys.argv[1:]:
        
        # Get all the lines from the file.
        with open(filename, 'r') as fh:
            lines = fh.readlines()
        
        # The models to check.
        model = ["UKESM1", "HadGEM3-GC31"]
        for m in model:
            print(f"Processing {m} in {filename}")
            
            # First, get the STASH codes from the Expression lines. 
            stashCodes = []
            for line in lines:
                
                # Check that it's an Expression line for this model.
                if f"Expression {m} " in line:
                    
                    # The Expression line may contain multiple STASH codes.  Get them all.
                    for match in re.finditer('m0', line):
                        istart = match.start()
                        stashCodes.append(line[istart:istart+length])
                        
            print(stashCodes)
            
            # For each STASH code, check if it is in the STASH entries.
            for code in stashCodes:
                foundCode = False
                for line in lines:
                    
                    # Check that it's a STASH entry line for this model.
                    if f"| {m} " in line:
                        
                        # Each entry line only contains one STASH code.
                        if code in line:
                            print("{} found in STASH entries".format(code))
                            foundCode = True
                            break
                        
                # Warning if not found.
                if not foundCode:
                    print("*** Warning: {} NOT FOUND in STASH entries for {} in {}".format(code, m, filename))          
            
            # Now check that all STASH codes in the STASH entries are in the Expression lines.        
            for line in lines:      
                
                # Check that it's a STASH entry line for this model.
                if f"| {m} " in line:
                    
                    # Each entry line only contains one STASH code.
                    match = re.search('m0', line)
                    if match:
                        istart = match.start()
                        code = line[istart:istart+length]
                        
                        # Warning if this code is not in the Expression lines.
                        if code not in stashCodes:
                            print("### Warning: {} NOT FOUND in Expression lines for {} in {}".format(code, m, filename))
                        continue

