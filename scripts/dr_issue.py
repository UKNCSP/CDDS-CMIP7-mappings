from dataclasses import dataclass, field
from collections import defaultdict
from textwrap import dedent
import re

TEMPLATE = '''
## Data Request information

| Field | Value | Notes |
| --- | --- | --- |
{dr}


## Mapping information 

| Field | Value | Notes |
| --- | --- | --- |
{mapping}


## STASH entries (relevant for UM only)

| Model | STASH | Section, item number | Time Profile | Domain Profile | Usage Profile |
| --- | --- | --- | --- | --- | --- |
{stash}

## XIOS entries (relevant for NEMO, MEDUSA, SI3)

| Model | xml entry | 
| --- | --- |
{xios}
'''

@dataclass
class DRIssue:
    """
    Data class to hold issue information
    """
    header: list = field(default_factory=list)
    dr_info: dict = field(default_factory=dict)
    dr_notes: dict = field(default_factory=dict)
    mapping_info: dict = field(default_factory=dict)
    mapping_notes: dict = field(default_factory=dict)
    stash: defaultdict(dict) = field(default_factory=lambda: defaultdict(list))
    xios_info: defaultdict(dict) = field(default_factory=lambda: defaultdict(list))
    ammended = False
    issue_number: int = field(default_factory=int)

    def write(self) -> str:
        """
        return the issue as text
        """
        dr = '\n'.join(['| {} | {} | {} |'.format(k, self.dr_info[k], self.dr_notes[k]) for k in self.dr_info])
        mapping = '\n'.join(['| {} | {} | {} |'.format(k, self.mapping_info[k], self.mapping_notes[k]) for k in sorted(self.mapping_info)])
            
        stash = ''
        for key, stashdata in sorted(self.stash.items()):
            for entry in stashdata:
                stash += '| {} | {} |\n'.format(key, ' | '.join(entry))
        xios = ''
        for key, xiosdata in sorted(self.xios_info.items()):
            for entry in xiosdata:
                xios += '| {} | {} |\n'.format(key, entry)
            
        return TEMPLATE.format(dr=dr, mapping=mapping, stash=stash, xios=xios).replace("  ", " ")

    def write_file(self, filename) -> None:
        """
        write issue to file
        """
        with open(filename, "w") as fh:
            fh.write(self.write())

    def read_file(self, filename) -> None:
        """
        read an issue into the class from a file
        """
        with open(filename) as fh:
            lines = [i.strip() for i in fh.readlines()]
        
        self._read_common(lines)

    def read_text(self, text) -> None:
        """
        read issue from text
        """
        lines = text.split("\n")
        self._read_common(lines)
    
    def _read_common(self, lines) -> None:
        skip_lines = ['| Field', '| Model |', '| ---']
        section = None

        skip_count = 0
        
        for linenum, line in enumerate(lines):
            if skip_count > 0:
                skip_count -= 1
                continue
            if not line:
                #skip blank
                continue
            elif any([line.startswith(i) for i in skip_lines]):
                # skip table headers
                continue
            elif line.startswith('## Data Request information'):
                section = 'DR'
                continue
            elif line.startswith('## Mapping information'):
                section = 'M'
                continue
            elif line.startswith('## STASH entries'):
                section = 'S'
                continue
            elif line.startswith('## XIOS entries'):
                section = 'X'
                continue
            
            line = re.sub(r"\|\|", "| |", line)
            linedata = [i.strip() for i in line.strip('|').split('|')]
            
            if section in ['DR', 'M']:
                
                # while len(linedata) < 3:
                #     self.ammended = True
                #     skip_count += 1
                #     line = line + "; " + lines[linenum + skip_count]
                #     line = re.sub(r"||", "| |", line)
                #     linedata = [i.strip() for i in line.strip('|').split('|')]
                
                if len(linedata) == 3:
                    key, value, note = linedata
                elif len(linedata) == 2: # common error -- lost notes
                    key, value = linedata
                    note = ""
                else:
                    continue
                    
                # except ValueError as err:
                    
                #     print(linedata)
                #     print(line)
                #     raise
                if section == 'DR':
                    self.dr_info[key] = value
                    self.dr_notes[key] = note
                elif section == 'M':
                    self.mapping_info[key] = value
                    self.mapping_notes[key] = note
            elif section == 'S':
                model = linedata[0]
                stashdata = linedata[1:]
                self.stash[model].append(stashdata)
            elif section == 'X':
                model = linedata[0]
                data = linedata[1:]
                self.xios_info[model] += data
        return self

    def cdds_mapping(self, model) -> str:
        """
        Construct the CDDS mapping information and return as a multiline string 
        """
        bv_name = self.dr_info['Branded variable name']
        dimensions = self.dr_info['Dimensions']
        positive = self.dr_info['Positive']
        # if positive == "":
        #     positive = "none"
        realm = self.dr_info['Modeling realm']
        
        expression = self.mapping_info.get(f'Expression {model}', None)
        if expression is not None:
            expression = expression.replace("`","")
        
        comment = ""
        # comment = self.mapping_notes.get(f'Expression {model}', None)
        #if comment == "---":
        #    comment = ""
        units = self.mapping_info.get('Model units', 'MISSING_MODEL_UNITS')

        if match := re.match(r'(\d+)[Ee]([+-])(\d+)', units):
            groups = list(match.groups())
            groups[2] = int(groups[2])
            units = '{0}e{1}{2}'.format(*groups)
        
        if expression is not None:
            result = dedent(f"""
            [{bv_name}]
            comment = {comment}
            component = {realm}
            dimension = {dimensions}
            expression = {expression}
            mip_table_id = {realm}
            positive = {positive}
            reviewer = none
            status = embargoed
            units = {units}""")
        else:
            raise RuntimeError(f'No information for model "{model}"')
        return result
    
    def cdds_stream(self, model) -> str:
        if model in self.stash:
            collected_stash = []
            for entry in self.stash[model]:
                try:
                    stream = "ap" + entry[4][-1].lower()
                except:
                    stream='UNKNOWN'
                collected_stash.append(stream)
            if len(set(collected_stash)) != 1:
                breakpoint()
                raise RuntimeError('Multiple possible streams')
            return collected_stash[0]
        elif model in self.xios_info:
            for entry in self.xios_info[model]:
                match = re.search(r'([oi]n[md]/[a-zA-Z-]{5,6})', entry)
                if match:
                    return match.groups()[0]
        else:
            return "UNKNOWN"

