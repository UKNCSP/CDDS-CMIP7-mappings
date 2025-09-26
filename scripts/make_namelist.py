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

    # List of models to consider (names in the 'Model' column of the spreadsheet).
    models = ['HadGEM3-GC31', 'HadGEM3-GC5', 'UKESM1', 'UKESM1-3']

    for model in models:

        # Count number of entries for this model, and how many are approved.
        imod = 0
        iapproved = 0

        # Want to find all approved entries for this model having unique values for (STASH,
        # domain_profile, Section, Item, time_profile, usage_profile).  Use a set to avoid
        # duplicates.
        unique = set()

        for d in data[:]:
            if d['Model'] == model:
                imod += 1
                if d['approved'].upper() == 'TRUE':
                    iapproved += 1
                    unique.add((d['STASH'], d['domain_profile'], d['Section'], d['Item'],
                        d['time_profile'], d['usage_profile']))

        print(f"Found {imod} {model} entries, of which {iapproved} are approved, and {len(unique)} are unique")
        with open(f"{model}_namelist.txt", 'w') as outfile:
            for u in sorted(unique):
                outfile.write("[namelist:umstash_streq()]\n")
                outfile.write(f"dom_name={u[1]}\n")
                outfile.write(f"isec={u[2]}\n")
                outfile.write(f"item={u[3]}\n")
                outfile.write(f"package=''\n")
                outfile.write(f"tim_name={u[4]}\n")
                outfile.write(f"use_name={u[5]}\n")
                outfile.write(f"\n")
