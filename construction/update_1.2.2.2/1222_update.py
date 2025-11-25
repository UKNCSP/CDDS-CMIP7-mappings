
import json
import re
from dr_issue import DRIssue

labels_file = 'labels.json'

with open(labels_file) as fh:
    labels = json.load(fh)

title_pattern = r"Variable (.*) \(.*\)"

with open('renames.json') as fh:
    renames = json.load(fh)


cmip6name_to_cmip7name = {}
cmip7name_to_cmip6name = {}
cmip6name_to_issue = {}
for cmip6name, entry in labels.items():
    match = re.search(title_pattern, entry['title'])
    cmip7name = match.groups()[0]
    cmip6name_to_cmip7name[cmip6name] = cmip7name
    cmip7name_to_cmip6name[cmip7name] = cmip6name
    cmip6name_to_issue[cmip6name] = entry['number']

rename_count = 0
for cmip6name, entry in labels.items():
    match = re.search(title_pattern, entry['title'])
    cmip7name = match.groups()[0]
    if cmip7name in renames:
        newname = renames[cmip7name]['new']
        if newname == "":
            newname = "REMOVED"
        issue = renames[cmip7name]['issue']
        title = entry['title']
        newtitle = f'Variable {newname} ({cmip6name})'
        rename_count += 1
        # print(f"{issue}: '{title}' -> {newtitle}")
        print(f'gh issue edit {issue} --title "{newtitle}"')
        print(f"gh issue comment {issue} --body 'Renamed from \"{title}\" to \"{newtitle}\" as part of update to data request v1.2.2.2'")

print(rename_count)

diffs = json.load(open("diffs_by_attribute.json"))


from collections import defaultdict

important = ['cell_methods', 'dimensions']

for attribute, changes in diffs['Attribute'].items():
    inverse_dict = defaultdict(list)
    for change_var, change_dict in changes.items():
        key = "'{0}' -> '{1}'".format(change_dict['1220.json'], change_dict['1222.json'])
        inverse_dict[key].append(change_var)
    #if attribute in important:
    print(json.dumps(inverse_dict, indent=2))


attribute_titles = {
    'cell_measures': 'Cell measures',
    'cell_methods': 'Cell methods',
    'comment':'Comment',
    'dimensions':'Dimensions',
    'long_name': 'Long name',
    'positive':'Positive',
    'standard_name':'CF standard name',
    'units':'Units',
}
skips = []
asserts = []
counter = 0

for attribute, changes in diffs['Attribute'].items():
    for change_var, change_dict in changes.items():
        counter +=1
        if change_var not in cmip7name_to_cmip6name:
            skips.append(change_var)
            continue
        cmip6name = cmip7name_to_cmip6name[change_var]
        filename = f"issues/{cmip6name}"
        dr_issue = DRIssue()
        dr_issue.read_file(filename)
        issue_field = attribute_titles[attribute]
        
        if dr_issue.dr_info[issue_field] != change_dict['1220.json']:
            # not bothered about whitespace
            if dr_issue.dr_info[issue_field] == change_dict['1220.json'].replace("  ", " "):
                continue
            asserts.append((
                change_var,
                dr_issue.dr_info[issue_field],
                change_dict['1220.json']
            ))
        dr_issue.dr_info[issue_field] = change_dict['1222.json']
        
        notes = dr_issue.dr_notes[issue_field]
        if notes:
            notes += "; updated DR v1.2.2.2"
        else:
            notes = "updated DR v1.2.2.2"
        dr_issue.dr_notes[issue_field] = notes

        dr_issue.write_file(filename)
        

        

print(counter)    

