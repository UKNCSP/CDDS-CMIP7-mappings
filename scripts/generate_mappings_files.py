
import sys
import json
import subprocess
from collections import defaultdict


from dr_issue import DRIssue

def main():

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} [model] [location]")
    model = sys.argv[1]
    location = sys.argv[2]


    model = 'UKESM1-3'
    result = subprocess.check_output('gh issue list -L 2000 --json number,title,body,labels'.split())

    data = json.loads(result)

    check = defaultdict(lambda: defaultdict(list))
    issuecheck = defaultdict(lambda: defaultdict(list))

    for d in data:
        if 'do-not-produce' in [i['name'] for i in d['labels']]:
            continue
        x = DRIssue()
        if not d['title'].startswith('Variable'): # non variable issue
            continue
        try:
            x.read_text(d['body'])
            mapping = x.cdds_mapping(model)
        except (RuntimeError): # no info for model
            continue
                    
        if x.dr_info['Frequency'] == 'yr':
            continue
        realm = x.dr_info['Modeling realm']
        check[realm][x.dr_info['Branded variable name']].append(mapping)
        issuecheck[realm][x.dr_info['Branded variable name']].append(d['number'])
    

    counter = 0

    mappings_by_realm = defaultdict(list)
    with open(f'{location}/issues.txt', 'w') as fh:
        for r in check:
            for v in check[r]:
                if len(set(check[r][v])) !=1:
                    counter +=1
                    fh.write(f'{counter} {r} {v}  {len(check[r][v])}  {len(set(check[r][v]))}\n')
                    
                    for c in check[r][v]:
                        fh.write(c)
                        fh.write("\n")

                    fh.write(' '.join([str(i) for i in issuecheck[r][v]])+"\n")
                    fh.write("--\n")
                else:
                    mappings_by_realm[r].append(check[r][v][0])

    for realm in mappings_by_realm:
        with open(f"{location}/{model}_{realm}_mappings.cfg", "w") as fh:
            for entry in sorted(mappings_by_realm[realm]):
                fh.write(entry)
                fh.write("\n")
            



if __name__ == '__main__':
    main()
