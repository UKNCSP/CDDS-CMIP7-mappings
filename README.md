# UKNCSP CDDS-CMIP7-mappings 
**UPDATE 23/10/25: I've altered the gitub action to run as a "cron" job rather than after every update. CSV files in the data directory should be updated at the start of every hour @matthew-mizielinski**

**IMPORTANT: All issues were updated for version 1.2.2 of the Data Request at the end of August. All CSV files will have changed as part of this update**

This repository is being used for collection and review of model configuration for the UKESM1-3 and HadGEM3-GC5 based models being prepared for CMIP7 submission in 2026.

## New users

You'll need to be given access to this repository in order to interact with the issues. This can either be done by clicking on "issues", "New Issue" and selecting the "New Reviewer Request" or clicking [here](https://github.com/UKNCSP/CDDS-CMIP7-mappings/issues/new?template=new_reviewer.yml).

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

### Processors

Processors are python functions used to do more complex manipulation than simple arithmetic operations. The current set of processors can be found [here](https://github.com/MetOffice/CDDS/blob/main/mip_convert/mip_convert/plugins/base/data/processors.py)
and new ones will be added as required. If a mapping needs a processor that does not exist please construct a suitable name and we will identify processors that don't exist later.

The responsibility for developing these processors will be considered at a later date, once the amount of resource required is clearer.

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
Note: if you are happy that the mapping is correct for UKESM1-3, but is not suitable for other models please apply the `approved_UKESM` label. 
Similarly you can use `approved_HadGEM` if you can only approve an issue for HadGEM3-GC5 models

If you have questions please add the "question" label to the issue. We will attempt to answer questions and remove that label when we think we've answered them.

If you believe that it is not possible to produce a variable using any of our models (e.g. because we do not have a wave model) then please mark the variable with `do-not-produce`.

Note that comments are ignored by the automated process so can be used for queries or discussions.

### Mappings update

To update the mapping add an extra row to the mappings table for the corresponding model (`UKESM1-3` or `HadGEM3-GC5`. For example, to extend the mapping for Amon.tas ([#67](https://github.com/UKNCSP/CDDS-CMIP7-mappings/issues/67))
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

To support configuration of the UM atmosphere output each issue also tabulates the corresponding entries
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

### Usage profiles and output frequency

The usage profiles in stash should be used to collect data of similar frequencies -- mixing, for example, 
daily and monthly mean data within the same stream makes data processing difficult.  
The usage profiles from CMIP6 should be reused for CMIP7;

| Usage profile | Output Stream | frequency | notes |
| --- | --- | --- | --- |
| UP4, UP5 | ap4, ap5 | monthly | Split between streams is for load balancing |
| UPU | apu | monthly | Unpacked data only (e.g. tendencies) |
| UP6 | ap6 | daily | |
| UP7 | ap7 | 6hr | |
| UP8 | ap8 | 3hr | |
| UP9 | ap9 | 1hr | |
| UPT | apt | subhr | Generally only used for site specific (CFsubhr) variables |

Note that for a given variable there must only be one usage profile/stream used -- we cannot extract
data from multiple streams to produce a single variable.

In the past data has been retrieved from the `apm` stream (UPMEAN usage profile), but we would prefer to 
avoid this if possible in case of issues with the climate meaning system.

### Differences between HadGEM3-GC5 and UKESM1-*/HadGEM3-GC31 models

Please note that the HadGEM3-GC5 configuration uses both a new configuration of NEMO (conservative 
potential temperature and absolute salinity as prognostics) and the SI3 model rather than CICE for the sea-ice component.
Mappings will need to take this into account when adding information for HadGEM3-GC5 in particular.

### Bulk review of diagnostics

When reviewing many diagnostics the github interface may become tiresome to work with.  The following process allows 
the same work to be done within a bash session. It relies on the github command line client `gh`.

1. clone this repository: `git clone git@github.com:UKNCSP/CDDS-CMIP7-mappings.git`
2. cd into the checked out directory and authenticate with your github account: `gh auth login`
3. dump the issues to a directory (one file per issue) using one of the following commands (in each case the "issue_review" directory must not exist):
    - `python scripts/dump_all_issues.py issue_review labels.json`  (retrieves all issues and writes a json file with information about issues that cannot go in the issue files)
    - `python scripts/dump_all_issues.py issue_review labels.txt`  (retrieves all issues and writes a text file with a table showing the same information as the json file)
    - `python scripts/dump_issue_subset.py issue_review atmosChem,-approved` (retrieves all issues that include the label `atmosChem`, but do not have the `approved` labels)
4. For variables which use STASH codes in their mapping expression, the STASH entries list must be consistent with the mapping expression - that is, each of the STASH codes in the mapping expression must appear in the STASH entries, and that there must be no codes in the entries which don't appear in the mapping expression.  The check_stash script checks for this: `python scripts/check_stash.py <issue file>`  
5. either
    - Edit the text files using the editor of your choice, or
    - Use the simple_update script to copy the expression and STASH information from UKESM1 to UKESM1-3 and HadGEM3-GC31 to HadGEM3-GC5: `python scripts/simple_update.py <issue file>`
6. Construct the list of github commands to push changes back to github; `python scripts/update_issue.py <issue file> <issue file> ...`
7. If that list of commands looks correct (no python errors from the last command) run each gh command or pipe the output into bash; `python scripts/update_issue.py <issue file> <issue file> ... | bash`
8. If you are ready to approve an issue run `python scripts/approve_issue.py <issue file> <issue file> ...` and then pipe the output to bash as above if this command succeeds.

Please test the above process out with a single issue to get familiar with the process before attempting many commands.  If you are not comfortable with this approach please contact Matt Mizielinski and Jeremy Walton to discuss using the csv files under the data directory.
