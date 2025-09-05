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
        print('Usage:\t{} [directory that does not exist] [labels file]'.format(sys.argv[0]))
        print('Purpose:\tExtract content of all issues and write to file')
        print('Note: if labels_file ends in json a JSON file will be written otherwise a text file will be output')

    output_dir = sys.argv[1]
    labels_file = sys.argv[2]

    if os.path.exists(output_dir):
        print('Directory exists. exiting')
        sys.exit(1)

    os.mkdir(output_dir)

    results = subprocess.check_output('gh issue list -L 3000 --json title,body,state,number,labels,assignees'.split())

    data = json.loads(results)
    labels = {}
    for i in data:
        match = re.search('\(([A-Za-z0-9.]+)\)$', i['title'])
        if not match:
            print('ERROR: could not interpret "{}"'.format(i['title']))
            continue
        filename = match.groups()[0]
        labels[filename] =  {
            'title': i['title'],
            'labels': [j['name'] for j in i['labels']],
            'number': i['number'],
            'state': i['state'],
            'assignees': [j['login'] for j in i['assignees']],
        }
        with open(os.path.join(output_dir, filename), 'w') as fh:
            # fh.write('# Title: "{}"\n'.format(i['title']))
            # fh.write('# Labels:{}\n'.format(", ".join([j['name'] for j in i['labels']])))
            # fh.write('# Issue Number: {}\n'.format(i['number']))
            # fh.write('# Issue State: {}\n'.format(i['state']))
            # fh.write('\n')
            fh.write(i['body'])
    #breakpoint()
    with open(labels_file, 'w') as fh:
        if labels_file.endswith('json'):
            json.dump(labels, fh, indent=2)
        else:
            for filename, entry in labels.items():
                line = [filename] + [str(entry[i]) for i in ['title', 'number', 'state']] + [','.join(entry['labels'])]+ [','.join(entry['assignees'])]
                fh.write("\t".join(line) + "\n")
        
