# Read in a CSV file containing a spreadsheet of UM stash requests, and produce
# namelist files for each of a set of models, containing all the approved requests
# for that model.  There may be duplicates in the spreadsheet (because each stash
# could contribute to multiple variables), so only unique requests are included
# in the namelist files.

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

                # Is this entry approved?  Note that some entries have 'TRUE' in lower case.
                if d['approved'].upper() == 'TRUE':
                    iapproved += 1

                    # Add the variables we're interested in to the set of unique entries.
                    # Note that the order of the items in the tuple is important, as it
                    # determines the sort order when we write out the namelist file.
                    unique.add((d['STASH'], d['domain_profile'], d['Section'], d['Item'],
                        d['time_profile'], d['usage_profile']))

        # Summarise what we've found, and write out the namelist file for this model.
        print(f"Found {imod} {model} entries, of which {iapproved} are approved, and {len(unique)} are unique")
        with open(f"{model}_namelist.txt", 'w') as outfile:

            # We'll sort the unique entries into order of increasing STASH (because that's
            # the first element in the list for each entry).
            for u in sorted(unique):

                # Some of these values - such as the name of the namelist and the package -
                # are currently blank.
                outfile.write("[namelist:umstash_streq()]\n")
                outfile.write(f"dom_name={u[1]}\n")
                outfile.write(f"isec={u[2]}\n")
                outfile.write(f"item={u[3]}\n")
                outfile.write(f"package=''\n")
                outfile.write(f"tim_name={u[4]}\n")
                outfile.write(f"use_name={u[5]}\n")
                outfile.write(f"\n")
