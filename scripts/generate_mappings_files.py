
import json
import subprocess
from collections import defaultdict


from dr_issue import DRIssue

def main():

    result = subprocess.check_output('gh issue list -L 2000 --json number,title,body,labels'.split())

    data = json.loads(result)

    check = defaultdict(lambda: defaultdict(list))
    issuecheck = defaultdict(lambda: defaultdict(list))

    for d in data:
        x = DRIssue()
        if not d['title'].startswith('Variable'): # non variable issue
            continue
        try:
            x.read_text(d['body'])
            mapping = x.cdds_mapping("UKESM1-3")
        except (RuntimeError): # no info for model
            continue
                    
        if x.dr_info['Frequency'] == 'yr':
            continue
        realm = x.dr_info['Modeling realm']
        check[realm][x.dr_info['Branded variable name']].append(mapping)
        issuecheck[realm][x.dr_info['Branded variable name']].append(d['number'])
    

    counter = 0
    for r in check:
        for v in check[r]:
            if len(set(check[r][v])) !=1:
                counter +=1
                print(counter, r,v, len(check[r][v]), len(set(check[r][v])))
                
                for c in check[r][v]:
                    print(c)
                print(issuecheck[r][v])
                print("--")
    breakpoint()



if __name__ == '__main__':
    main()
