import csv
import sys

if __name__ == '__main__':

    
    if len(sys.argv) != 2:
        print(f"{sys.argv[0]} csv filename")
        sys.exit(1)
        
    filename = sys.argv[1]
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
        
    print(data[0])
    
