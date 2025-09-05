"""
Script to write out text files containing body of each issue
"""
import sys
import json
import subprocess
import os
import re



if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Usage:\t{} [directory that does not exist] [comma separated list of labels to include (no spaces)]'.format(sys.argv[0]))
        print('Purpose:\tExtract content of issues which have the specified labels')
        print('Note: prefixing a label with "-" will act as a negative filter')

    output_dir = sys.argv[1]
    labels_list = sys.argv[2].split(",")
    include_labels = set([i for i in labels_list if not i.startswith("-")])
    exclude_labels = set([i[1:] for i in labels_list if i.startswith("-")])


    if os.path.exists(output_dir):
        print('Directory exists. exiting')
        sys.exit(1)

    os.mkdir(output_dir)

    results = subprocess.check_output('gh issue list -L 3000 --json title,body,state,number,labels'.split())

    data = json.loads(results)
    labels = {}
    for i in data:
        match = re.search('\(([A-Za-z0-9.]+)\)$', i['title'])
        if not match:
            print('ERROR: could not interpret "{}"'.format(i['title']))
            continue
        filename = match.groups()[0]
        issue_labels = set([j['name'] for j in i['labels']])

        if issue_labels.intersection(include_labels) == include_labels:
            if issue_labels.intersection(exclude_labels):
                continue
        
            with open(os.path.join(output_dir, filename), 'w') as fh:
                fh.write(i['body'])
        
    