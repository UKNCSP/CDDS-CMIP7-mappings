import csv
import sys

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print(f"{sys.argv[0]} csv filename")
        sys.exit(1)

    # Read spreadsheet into a dictionary.
    filename = sys.argv[1]
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    
    # Want to find all approved entries with unique (STASH, domain_profile, Section, Item,
    # time_profile, usage_profile).  Use a set to avoid duplicates.
    unique = set()

    # Count number of entries for HadGEM3-GC31 and how many are approved.
    imod = 0
    iapproved = 0

    for d in data[:]:
        if d['Model'] == 'HadGEM3-GC31':
            imod +=1
            if d['approved'].upper() == 'TRUE':
                iapproved += 1
                unique.add((d['STASH'], d['domain_profile'], d['Section'], d['Item'],
                    d['time_profile'], d['usage_profile']))

    print(f"Found {imod} HadGEM2-GC31 entries, of which {iapproved} are approved, and {len(unique)} are unique")
    for u in sorted(unique):
        print(u)
