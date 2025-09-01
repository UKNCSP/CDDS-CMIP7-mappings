"""
Script to update issues
"""

import sys
import json
import subprocess


if __name__ == '__main__':

    data = subprocess.check_output('gh issue list --json number,title,labels -L 3000'.split())
    alldata = json.loads(data)

    for filename in sys.argv[1:]:
        key = filename.split("/")[-1]

        issue_key = filename.split("/")[-1]

        issues = [i for i in alldata if '({})'.format(key) in i['title']]

        if len(issues) > 1:
            print("found more than 1 record")
            sys.exit(1)

        result = issues[0]
        number = result['number']

        #command would be 'gh issue edit N --add-label "name,name,name"'
        #existing_labels = [i['name'] for i in result['labels']]

        command = 'gh issue edit {} -F {}'.format(number, filename) 
        print(command)
        #command2 = 'gh issue edit {} --add-label approved'.format(number) 
        #print(command2)
        command3 = f'gh issue edit {number} --add-label approved --add-assignee @me'
        print(command3)

