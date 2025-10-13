"""
This script is used to update the json and csv files and is triggered by github actions
"""
import json
import subprocess
import re
import csv
import sys
import os
from collections import defaultdict

REMOVED_LABELS = ['removed v1.2.2']


def tables_to_dict(text):
    """
    Extract information from tables and return as a dictionary
    """
    
    section = None
    key = None
    
    results = {}
    
    for line in text.split("\n"):
        match = re.search('## (.*)', line)
        if match:
            section = match.group(1).strip()
            if 'STASH' in section:
                section = "STASH entries"
                results[section] = []
            elif 'XIOS' in section:
                section = "XIOS entries"
                results[section] = {}
            else:
                results[section] = {}
            continue
        if line.startswith("|"):
            linedata = [i.strip().strip("`") for i in line.split("|")]
            if linedata[1] in ['Key', '---', 'Field', 'Model']:
                continue
            if any([section.startswith(i) for i in ["Data", "Mapping", "XIOS"]]):
                key = linedata[1]
                value = linedata[2]
                results[section][key] = value
            if section.startswith('STASH'):
                try:
                    model, stash, stash_num, time, dom, usage = linedata[1:7]
                except ValueError:
                    bv_name = results['Data Request information']['Branded variable name']
                    freq = results['Data Request information']['Frequency']
                    print(f'Could not interpret line "{line}" for branded variable "{bv_name}" at frequency "{freq}"')
                    continue
                if stash != "":
                    results[section].append({
                        'model': model,
                        'STASH': stash,
                        'stash_number': stash_num,
                        'time_profile': time,
                        'domain_profile': dom,
                        'usage_profile': usage
                        })
    return results
                

def write_csv(output_dir, title_list, per_realm_csv, suffix):
    for realm, realm_csv in per_realm_csv.items():
        with open(os.path.join(output_dir, '{}_{}.csv'.format(realm, suffix)), 'w') as fh:
            writer = csv.writer(fh, dialect='excel')
            writer.writerow(title_list)
            for row in realm_csv:
                writer.writerow(row)


if __name__ == '__main__':

    # location for result files
    output_dir = sys.argv[1]
    
    # obtain results NOTE LIMIT TO 2000
    result = subprocess.check_output('gh issue list -L 2000 --json number,title,body,labels'.split())

    # parse json data
    data = json.loads(result)

    # prepare mappings.json
    results = []
    # breakpoint()
    for entry in data:
        if not entry['title'].startswith('Variable'):
            continue
        result = tables_to_dict(entry['body'])
        result['title'] = entry['title']
        result['issue_number'] = entry['number']
        result['labels'] = [i['name'] for i in entry['labels']]
        # only append to results if not marked as removed
        if not any([i in result['labels'] for i in REMOVED_LABELS]):
            results.append(result)

    with open(os.path.join(output_dir, 'mappings.json'), 'w') as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    # prepare mappings.csv
    all_mapping_keys = set()
    for entry in results:
        for i in entry['Mapping information']:
            all_mapping_keys.add(i)

    order_first = ['title', 'issue_number']
    order_link = ['link']
    order_labels = ['labels']
    order_dr = sorted(list(results[0]['Data Request information'].keys()))
    order_mapping = [i for i in sorted(list(all_mapping_keys)) if ('Expression' in i or 'units' in i)]
    title_list = order_first + order_link + order_labels + order_dr + order_mapping
    csv_output = []
    for entry in results:
        record = [entry[i] for i in order_first]
        record += ['https://github.com/UKNCSP/CDDS-CMIP7-mappings/issues/{}'.format(entry['issue_number'])]
        record += [' '.join(entry['labels'])]
        record += [entry['Data Request information'].get(i, "") for i in order_dr]
        record += [entry['Mapping information'].get(i, "") for i in order_mapping]
        #record.append(','.join(entry['labels']))
        csv_output.append(record)

    with open(os.path.join(output_dir, 'mappings.csv'), 'w') as fh:
        writer = csv.writer(fh, dialect='excel')
        writer.writerow(title_list)
        for row in csv_output:
            writer.writerow(row)

    # per realm csvs
    per_realm_csv = defaultdict(list)
    per_realm_csv_cmip6 = defaultdict(list)
    per_realm_csv_new = defaultdict(list)
    for entry in csv_output:
        realm = entry[0].split(" ")[1].split(".")[0]
        per_realm_csv[realm].append(entry)
        labels = entry[3]
        if 'CMIP6' in labels:
            per_realm_csv_cmip6[realm].append(entry)
        else:
            per_realm_csv_new[realm].append(entry)

    
    write_csv(output_dir, title_list, per_realm_csv, 'mappings')
    write_csv(output_dir, title_list, per_realm_csv_cmip6, 'mappings_CMIP6')
    write_csv(output_dir, title_list, per_realm_csv_new, 'mappings_new')


    # prepare stash csv
    stash_headings = [
        'Model',
        'Branded variable name',
        'Frequency',
        'STASH',
        'Section',
        'Item',
        'time_profile',
        'domain_profile',
        'usage_profile',
        'approved',
        'approved_UKESM',
        'approved_HadGEM'
    ]
    stash_csv = [stash_headings]
    for entry in results:
        stash_data = entry["STASH entries"] # (relevant for UM only)"]
        if not stash_data:
            continue
        for i in stash_data:
            line = [
                i['model'],
                entry['Data Request information']['Branded variable name'],
                entry['Data Request information']['Frequency'],
                i['STASH'],
                ]
            if ',' in i['stash_number']:
                line += i['stash_number'].split(',')
            else:
                line += [0, i['stash_number']]
            line += [i[j] for j in stash_headings[-6:-3]]
            line += [
                'approved' in entry['labels'], 
                'approved_UKESM' in entry['labels'], 
                'approved_HadGEM' in entry['labels']]
            stash_csv.append(line)
     
    with open(os.path.join(output_dir, 'stash.csv'), 'w') as fh:
        writer = csv.writer(fh, dialect='excel')
        for row in stash_csv:
            writer.writerow(row)  
    
    
    xios_data = {}
    for entry in results:
        xios_entry = entry.get("XIOS entries", [])
        if xios_entry:
            xios_data[entry['title']] = xios_entry
    
    with open(os.path.join(output_dir, "xios.json"), 'w') as fh:
        json.dump(xios_data, fh, indent=2, sort_keys=True)


