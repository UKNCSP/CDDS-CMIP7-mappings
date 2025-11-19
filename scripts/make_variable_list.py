
import sys
import re

if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print(f"{sys.argv[0]} [list of issue files to read]")
        sys.exit(1)
    
    m = "UKESM1-3"
    for filename in sys.argv[1:]:
        
        # Get all the lines from the file.
        with open(filename, 'r') as fh:
            lines = fh.readlines()
        
        keyFound = False
        for line in lines:
            # Get the Key value.
            if "| Key |" in line:
                keyFound = True
                key = line.split("|")[2].strip()

                # Extract mip and var from the key.
                mip = key.split(".")[0]
                var = key.split(".")[1]
        if not keyFound:
            print(f"Warning: No Key found in file {filename}")

        realmFound = False
        for line in lines:
            # Get the Key value.
            if "| Modeling realm |" in line:
                realmFound = True
                realm = line.split("|")[2].strip()
        if not realmFound:
            print(f"Warning: No realm found in file {filename}")

        #if mip not in ["SImon", "SIday", "Omon", "Oday", "Oyr", "Odec"]:
        if realm not in ["ocean"]:
            streamFound = False
            for line in lines:
                if not streamFound:
                    if f"| {m} |" in line:
                        streamFound = True
                        stream = line.split("|")[6].strip()
                        print(f"{var}/{mip}:{stream}")