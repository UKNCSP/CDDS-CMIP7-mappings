# UKNCSP CDDS-CMIP7-mappings 

This repository is being used for collection and review of model configuration for the UKESM1-3 and HadGEM3-GC5 based models being prepared for CMIP7 submission in 2026.

## Mapping and STASH information 

Information is being held for each mapping in the body of github issues, e.g. [#67](https://github.com/UKNCSP/CDDS-CMIP7-mappings/issues/67) contains the information for 
monthly mean surface air temperature (Amon.tas). Within each issue there are three tables; 
the first for Data Request information, second for mapping information and the third for STASH setup.

The information in the issues is also presented in the following files;
* [data/mappings.json](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/mappings.json) (JSON representation of the data in each issue)
* [data/mappings.csv](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/mappings.csv) (Excel CSV representation of Data Request and Mapping information)
* [data/stash.csv](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/stash.csv) (Excel CSV representation of STASH information)

Github will provide an interface to search CSV files, but the mappings.csv file is above the size limit on this service (512 K) so the mappings are also presented in a set of files organised by realm;

  **[aerosol](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/aerosol_mappings.csv)**
  **[atmosChem](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/atmosChem_mappings.csv)**
  **[atmos](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/atmos_mappings.csv)**
  **[landIce](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/landIce_mappings.csv)**
  **[land](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/land_mappings.csv)**
  **[ocean](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/ocean_mappings.csv)**
  **[ocnBgchem](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/ocnBgchem_mappings.csv)**
  **[seaIce](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/seaIce_mappings.csv)**

Note that there are separate files for variables which were present in CMIP6 and those that appear to be new in the [data subdirectory](https://github.com/UKNCSP/CDDS-CMIP7-mappings/blob/main/data/).

Automatic processes (github actions) regenerate these files as issues are added or updated (see [here](https://github.com/UKNCSP/CDDS-CMIP7-mappings/actions/workflows/update_data_csv_json.yml)).

## Prerequisites for the Review process

Anyone with a github account can comment on issues, but to edit the body of the github issues and contribute 
to the mappings/STASH setup review process users will need to be registered. To do this please fill 
out [this form](https://github.com/UKNCSP/CDDS-CMIP7-mappings/issues/new?template=new_reviewer.yml).

## Review process 

Information is extracted from the "body" of each issue and updates should be made by editing its content 
(see image below for pointer to button)

![image](https://github.com/user-attachments/assets/3b907a1a-e3a3-4ea4-948d-ca3163b71389)

This will trigger actions to update the information in the data files linked to above.

Once your review is complete please add the "approved" label to the issue and add a comment confirming that you are happy with the mapping and STASH entries.

If you have questions please add the "question" label to the issue. We will attempt to answer questions and remove that label when we think we've answered them.

Note that comments are ignored by the automated process so can be used for queries or discussions

### Mappings update

To update the mapping add an extra row to the mappings table for the corresponding model (`UKESM1-3` or `HadGEM3-GC5`. For example to extend the mapping for Amon.tas ([#67](https://github.com/UKNCSP/CDDS-CMIP7-mappings/issues/67))
change the mappings table from 

| Field | Value | Notes |
| --- | --- | --- |
| Expression UKESM1 | `m01s03i236[lbproc=128]` | |
| Expression HadGEM3-GC31 | `m01s03i236[lbproc=128]` | |
| Model units | K | |

to 

| Field | Value | Notes |
| --- | --- | --- |
| Expression UKESM1 | `m01s03i236[lbproc=128]` | |
| Expression HadGEM3-GC31 | `m01s03i236[lbproc=128]` | |
| Expression UKESM1-3 | `m01s03i236[lbproc=128]` | |
| Expression HadGEM3-GC5 | `m01s03i236[lbproc=128]` | |
| Model units | K | |

More complex mappings, i.e. those which require some post processing, use python functions to produce the required data. 
One example of this is Amon.tasmax ([#68](https://github.com/UKNCSP/CDDS-CMIP7-mappings/issues/68)) which uses a `mon_mean_from_day` in order to perform the necessary calculation.
These "processor" functions are all written in python, take multiple [iris cubes](https://scitools-iris.readthedocs.io/en/stable/userguide/iris_cubes.html#cube) 
as arguments and return an iris cube which is then passed on to CMOR for writing. The set of processor functions used in 
CMIP6 can current be found [here](https://github.com/MetOffice/CDDS/blob/main/mip_convert/mip_convert/plugins/hadgem3/data/processors.py).

If post-processing of data is required for a variable and a processor does not already exist please add the `processor` label to the issue. 
Additional information on processors should be added as a comment to the issue.

### STASH entries update

To support configuration of the UM atmoshpere output each issue also tabulates the corresponding entries
to be included in the STASH setup. If possible this table should be extended in a similar fashion to the
one for the mappings, but with a row for each STASH code required.

For example Amon.zg (geopotential height on pressure levels) in [#78](https://github.com/UKNCSP/CDDS-CMIP7-mappings/issues/78) has the expression 
`m01s30i297[blev=PLEV19, lbproc=128] / m01s30i304[blev=PLEV19, lbproc=128]` for both models so requires *two* lines 
in the STASH table for each model;

| Model | STASH | Section, item number | Time Profile | Domain Profile | Usage Profile |
| --- | --- | --- | --- | --- | --- |
| UKESM1 | m01s30i297 | 30,297 | TMONMN | PLEV19 | UP5 |
| UKESM1 | m01s30i304 | 30,304 | TMONMN | PLEV19 | UP5 |
| HadGEM3-GC31 | m01s30i297 | 30,297 | TMONMN | PLEV19 | UP5 |
| HadGEM3-GC31 | m01s30i304 | 30,304 | TMONMN | PLEV19 | UP5 |

To extend the same STASH requirements to the HadGEM3-GC5 and UKESM1-3 models extend the table to

| Model | STASH | Section, item number | Time Profile | Domain Profile | Usage Profile |
| --- | --- | --- | --- | --- | --- |
| UKESM1 | m01s30i297 | 30,297 | TMONMN | PLEV19 | UP5 |
| UKESM1 | m01s30i304 | 30,304 | TMONMN | PLEV19 | UP5 |
| HadGEM3-GC31 | m01s30i297 | 30,297 | TMONMN | PLEV19 | UP5 |
| HadGEM3-GC31 | m01s30i304 | 30,304 | TMONMN | PLEV19 | UP5 |
| UKESM1-3 | m01s30i297 | 30,297 | TMONMN | PLEV19 | UP5 |
| UKESM1-3 | m01s30i304 | 30,304 | TMONMN | PLEV19 | UP5 |
| HadGEM3-GC5 | m01s30i297 | 30,297 | TMONMN | PLEV19 | UP5 |
| HadGEM3-GC5 | m01s30i304 | 30,304 | TMONMN | PLEV19 | UP5 |

### Diagnostic review

Where mappings and STASH requirements have not materially changed from CMIP6 definitions we do not 
intend to produce sample data for Science QA review as these mappings have already been heavily tested.

Variables that are very similar to existing ones, e.g. where they only differ in frequency, will likely 
not require Science QA review.  

All new variables will need to go through a Science QA review process  to ensure that we have the
capability to produce the data correctly.

### Differences between HadGEM3-GC5 and UKESM1-*/HadGEM3-GC31 models

Please note that the HadGEM3-GC5 configuration uses both a new configuration of NEMO (conservative 
potential temperature and absolute salinity as prognostics) and the SI3 model rather than CICE for the sea-ice component.
Mappings will need to take this into account when adding information for HadGEM3-GC5 in particular.

### Bulk review of diagnostics

When reviewing many diagnostics there the github interface may become tiresome to work with.  The following process allows 
the same work to be done within a bash session. It relies on the github command line client `gh`.

1. clone this repository: `git clone git@github.com:UKNCSP/CDDS-CMIP7-mappings.git`
2. cd into the checked out directory and authenticate with your github account: `gh auth login`
3. dump the issues to a directory (one file per issue): `python scripts/dump_issues.py issue_review`
4. either
   a. Edit the text files using the editor of your choice or
   b. Use the simple_update script to copy the expression and STASH information from UKESM1 to UKESM1-3 and HadGEM3-GC31 to HadGEM3-GC5: `python scripts/simple_update.py <issue file>`
5. Construct the list of github commands to push changes back to github; `python scripts/update_issue.py <issue file> <issue file> ...`
6. If that list of commands looks correct (no python errors from the last command) run each gh command or pipe the output into bash; `python scripts/update_issue.py <issue file> <issue file> ... | bash`

Test the above process out with a single issue to get familiar with the process before attempting many commands.
