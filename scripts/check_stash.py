"""
The issue file for each variable contains Expression lines containing the mapping from 
STASH codes to the variable, along with a list of STASH entries.  This script checks
that all STASH codes in the Expression lines are in the STASH entries, and vice versa.
"""
import sys
import re
UKESM_only_variables = ['fco2antt', 'fco2fos', 'fco2nat']

if __name__ == '__main__':

    length = len('m01sxxiyyy')  # length of a STASH code.
    
    if len(sys.argv) <= 1:
        print(f"{sys.argv[0]} [list of issue files to check]")
        sys.exit(1)
    
    for filename in sys.argv[1:]:
        
        # Get all the lines from the file.
        with open(filename, 'r') as fh:
            lines = fh.readlines()
        
        # Does this variable use alev levels?
        for line in lines:
            if "Dimensions" in line:
                usesAlev = "alev" in line

        foundSTASH = True
        foundExpression = True

        # The models to check.
        if any(var in filename for var in UKESM_only_variables):
            model = ["UKESM1"]
        else:
            model = ["UKESM1", "HadGEM3-GC31"]
        for m in model:
            print(f"Processing {m} in {filename}")
            
            # First, get the STASH codes from the Expression lines. 
            expressionStashCodes = []
            for line in lines:
                
                # Check that it's an Expression line for this model.
                if f"Expression {m} " in line:
                    
                    # The Expression line may contain multiple STASH codes.  Get them all.
                    for match in re.finditer('m0', line):
                        istart = match.start()
                        expressionStashCodes.append(line[istart:istart+length])

            # Check that we found some STASH codes.
            if len(expressionStashCodes) == 0:
                print(f"*** Warning: No STASH codes found in Expression lines for {m} in {filename}")
                foundExpression = False
                continue
            else:
                print(expressionStashCodes)
            
            # For each STASH code in the Expression lines, check if it is in the STASH entries.
            # Record which codes are found; we'll warn if none are found.
            # Note that this doesn't check for duplicates in the STASH entries, because we're working
            # with from the list of codes in the Expression lines.
            stashEntriesCodes = []
            for code in expressionStashCodes:
                foundCode = False
                for line in lines:
                    
                    # Check that it's a STASH entry line for this model.
                    if f"| {m} " in line:
                        
                        # Each entry line only contains one STASH code.
                        if code in line:
                            print(f"{code} found in STASH entries for {m}")
                            stashEntriesCodes.append(code)
                            foundCode = True
                            break
                        
                # Warning if this code was not found.
                if not foundCode:
                    print(f"*** Warning: {code} NOT FOUND in STASH entries for {m} in {filename}")
                    foundSTASH = False
            
            # Check that we found some STASH entries.
            if len(stashEntriesCodes) > 0:

                # Check that all STASH codes in the STASH entries are in the Expression lines.
                for line in lines:
                    
                    # Check that it's a STASH entry line for this model.
                    if f"| {m} " in line:
                        
                        # Each entry line only contains one STASH code.
                        match = re.search('m0', line)
                        if match:
                            istart = match.start()
                            code = line[istart:istart+length]

                            if code == 'm01s00i033' and usesAlev:
                                # This is a special case.  This STASH code is used for both
                                # 3D and 2D versions of the variable, so may not appear in
                                # the Expression lines if the variable uses alev levels.
                                print(f"{code} special case for alev variable {m} in {filename}")
                            else:
                                if code not in expressionStashCodes:
                                    # Warning if this code is not in the Expression lines.
                                    print(f"### Warning: {code} NOT FOUND in Expression lines for {m} in {filename}")
                                    foundExpression = False
                            continue
            else:
                # There aren't any STASH entries, so there aren't any matches with
                # the Expression lines.
                print(f"*** Warning: No STASH entries found for {m} in {filename}")
                foundExpression = False

        # Summary of results for this variable.
        if foundSTASH:
            print(f"Codes in Expression all found in STASH list ", end='')
            if foundExpression:
                print(f"and codes in STASH list all found in Expression for {filename} +++")
            else:
                print(f"but codes in STASH list NOT all found in Expression for {filename} ---")
        else:
            print(f"Codes in Expression NOT all found in STASH list ", end='')
            if foundExpression:
                print(f"but codes in STASH list all found in Expression for {filename} ===")
            else:
                print(f"and STASH codes NOT all found in Expression for {filename} XXX")
        print("\n")

