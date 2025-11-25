import json
import re
from dr_issue import DRIssue
from collections import defaultdict


labels_file = 'labels.json'

with open(labels_file) as fh:
    labels = json.load(fh)

dr_file = '1222.json'
with open(dr_file) as fh:
    dr_data = json.load(fh)['Compound Name']


attribute_titles = {
    'cell_measures': 'Cell measures',
    'cell_methods': 'Cell methods',
    'comment':'Comment',
    'dimensions':'Dimensions',
    'long_name': 'Long name',
    'positive':'Positive',
    'standard_name':'CF standard name',
    'units':'Units',
    'branded_variable_name': 'Branded variable name',
    'standard_name':'CF standard name',
    'long_name': 'Long name',
    'processing_note': 'Processing notes',
    'modeling_realm': 'Modeling realm'
}

faults = defaultdict(dict)

for key, entry in labels.items():
    facets = entry['title'].split(" ")[1:]
    bvname = facets[0]
    dnp = 'do-not-produce' in entry['labels']
    drissue = DRIssue()
    drissue.read_file(f'issues/{key}')
    if bvname not in dr_data:
        print(f"variable not found: {bvname}")
        continue
    dr_dict = dr_data[bvname]
    
    for d, i in attribute_titles.items():
        dr_value = dr_dict[d]
        dr_value = re.sub(r"\s+", " ", dr_value)
        if dr_value != drissue.dr_info[i]:
            faults[key][d] = ( dr_dict[d] , drissue.dr_info[i])
            drissue.dr_info[i] = dr_value
            if drissue.dr_notes[i]:
                drissue.dr_notes[i] += "; Updated DR v1.2.2.2"
            else:
                drissue.dr_notes[i] = "Updated DR v1.2.2.2"
            drissue.ammended=True
    if key in faults:
        faults[key]['status'] = dnp
    
    if drissue.ammended:
        drissue.write_file(f'issues/{key}')
    


with open('inconsistencies.json', 'w') as fh:
    json.dump( dict(faults),fh, indent=2, sort_keys=True, default=str)
    
