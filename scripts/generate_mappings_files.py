
import sys
import json
import subprocess
from collections import defaultdict
from textwrap import dedent

from dr_issue import DRIssue


def map_variable_to_issue_num(data) -> dict:
    """Generates a dictionary mapping the branded variable name to the corresponding issue number(s). There will be
    multiple issue numbers if a variable has multiple issues for different frequencies."""
    issue_numbers = {}
    for d in data:
        # Skip any non variable issues or variables labelled as do-not-produce.
        if not d['title'].startswith('Variable') or 'do-not-produce' in [i['name'] for i in d['labels']]:
            continue

        branded_var = "_".join(d['title'].split(".")[1:3])
        if branded_var in issue_numbers:
            issue_numbers[branded_var].append(d['number'])
        else:
            issue_numbers[branded_var] = [d['number']]

    return issue_numbers


def main():
    # Check that all required command line argument have been given
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} [model] [location]")
    model = sys.argv[1]
    location = sys.argv[2]

    # List the 2000 most recent issues, returning their issue number, title, body content and labels
    result = subprocess.check_output('gh issue list -L 2000 --json number,title,body,labels'.split())
    data = json.loads(result)
    issue_numbers = map_variable_to_issue_num(data)

    check = defaultdict(lambda: defaultdict(list))
    issuecheck = defaultdict(lambda: defaultdict(list))
    stream = defaultdict(dict)

    for d in data:
        # Skip any non variable issues or those with the "do-not-produce" label
        if not d['title'].startswith('Variable'):
            continue
        if 'do-not-produce' in [i['name'] for i in d['labels']]:
            continue

        # Build the mapping entry and note the correspondng issue number(s) as a comment at the end of each entry, skip
        # the issue if there is no model information.
        x = DRIssue()
        try:
            x.read_text(d['body'])
            mapping = x.cdds_mapping(model) + f"\n# Issue number(s):{issue_numbers[x.dr_info['Branded variable name']]}"
        except (RuntimeError):
            continue

        frequency = x.dr_info['Frequency']
        if frequency == 'yr':
            continue
        realm = x.dr_info['Modeling realm'].split()[0]
        bv = x.dr_info['Branded variable name']
        check[realm][bv].append(mapping)
        issuecheck[realm][bv].append(d['number'])

        stream[realm][f'{bv}@{frequency}'] = x.cdds_stream(model)

    with open(f'{location}/streams.json', 'w') as fh:
        json.dump({'default': {}, 'overrides': stream}, fh, indent=4, sort_keys=True)

    counter = 0

    mappings_by_realm = defaultdict(list)
    with open(f'{location}/issues.txt', 'w') as fh:
        for r in check:
            for v in check[r]:
                # If there are multiple different mappings for a single branded variable note it in issues txt, this
                # variable mapping will be skipped
                if len(set(check[r][v])) != 1:
                    counter += 1
                    fh.write(f'{counter} {r} {v}  {len(check[r][v])}  {len(set(check[r][v]))}\n')

                    for c in check[r][v]:
                        fh.write(c)
                        fh.write("\n")

                    fh.write(' '.join([str(i) for i in issuecheck[r][v]]) + "\n")
                    fh.write("--\n")
                else:
                    mappings_by_realm[r].append(check[r][v][0])

    for realm in mappings_by_realm:
        with open(f"{location}/{model}_{realm}_mappings.cfg", "w") as fh:
            fh.write(dedent(f'''
                # (C) British Crown Copyright 2026, Met Office.
                # Please see LICENSE.md for license details.
                #
                # This 'model to MIP mappings' configuration file contains sections
                # for each 'MIP requested variable name' for the {realm} realm
                ''').lstrip()
            )
            for entry in sorted(mappings_by_realm[realm]):
                fh.write(entry)
                fh.write("\n")


if __name__ == '__main__':
    main()
