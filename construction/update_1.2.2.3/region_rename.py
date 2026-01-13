import json
'''
"AERmon.rsdcsaf": {
    "title": "Variable aerosol.rsdcsaf.tavg-u-hxy-u.mon.GLB (AERmon.rsdcsaf)",
    "labels": [
      "mon",
      "aerosol",
      "UKESM1",
      "HadGEM3-GC31",
      "beyond-AFT"
    ],
    "number": 1883,
    "state": "OPEN",
    "assignees": [
      "mo-benjohnson"
    ]
  },
 '''
 
with open('labels.json') as fh:
     labels = json.load(fh)
 
 
for entry in labels.values():
    title = entry['title']
    number = entry['number']
    title_space = title.split(' ')
    compound_name = title_space[1].split('.')
    region = compound_name[-1]
    if region == '30S-90S':
        continue
    if region != region.lower():
        compound_name[-1] = region.lower()
        title_space[1] = '.'.join(compound_name)
        new_title = ' '.join(title_space)
        print(f'gh issue edit {number} --title "{new_title}"')

