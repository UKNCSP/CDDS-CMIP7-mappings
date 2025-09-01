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
        print('Usage:\t{} [directory that does noy exist] [labels json file]'.format(sys.argv[0]))
        print('Purpose:\tExtract content of all issues and write to file')

    output_dir = sys.argv[1]
    labels_file = sys.argv[2]

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
        labels[filename] =  {
            'labels': [j['name'] for j in i['labels']],
            'number': i['number'],
            'state': i['state']
        }
        with open(os.path.join(output_dir, filename), 'w') as fh:
            fh.write(i['body'])
    
    with open(labels_file, 'w') as fh:
        json.dump(labels, fh, indent=2)
