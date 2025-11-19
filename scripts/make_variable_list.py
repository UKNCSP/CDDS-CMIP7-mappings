
import sys
import re

if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print(f"{sys.argv[0]} [list of issue files to read]")
        sys.exit(1)
    
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
                print(key)
        if not keyFound:
            print(f"Warning: No Key found in file {filename}")