# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""This script is designed to generate a diagnostic review data table based off of data produced in the testing of new
CMIP7 models and processed via review_diagnostic_data.py.

Example command line usage:
python diagnostic_review/review_diagnostic_table.py <model>
"""

import argparse
import pandas as pd
import os
import json

from IPython.core.display import HTML

MAPPINGS_FILE_LOCATION = "data/mappings.json"
TEMPLATE_HTML = """
<!DOCTYPE html>
<html>
<head>

<link rel="stylesheet" type="text/css" charset="UTF-8"
href="https://cdn.datatables.net/2.3.2/css/dataTables.dataTables.min.css"/>
<script type="text/javascript" charset="UTF-8" src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script type="text/javascript" charset="UTF-8" src="https://cdn.datatables.net/2.3.2/js/dataTables.min.js"></script>
<script type="text/javascript">
$(document).ready(function () {
var table = $('#table_id').DataTable({
    orderCellsTop: true,
    fixedHeader: true,
    pageLength: 100,
    initComplete: function () {
    var api = this.api();

    // Show the tables once DataTables has initialized
    $('#table_id').css('visibility', 'visible');

    // For each column, add a select filter to the second row
    api.columns().eq(0).each(function (colIdx) {
        var cell = $('.filters th').eq(colIdx);
        if (cell.length) {
        var select = $('<select><option value="">All</option></select>')
            .appendTo(cell.empty())
            .on('change', function () {
            api.column(colIdx)
                .search(this.value ? '^' + this.value + '$' : '', true, false)
                .draw();
            });

        api.column(colIdx).data().unique().sort().each(function (d) {
            if (d) select.append('<option value="' + d + '">' + d + '</option>');
        });
        }
    });
    }
});
});
</script>
<style>
table, th, td {
border: 1px solid black;
border-collapse: collapse;
}

tr:nth-child(even) {
background-color: rgba(150, 212, 212, 0.2);
}

th:nth-child(even),td:nth-child(even) {
background-color: rgba(150, 212, 212, 0.2);
}
/* Hide table until DataTables has fully initialized */
    #table_id {
    visibility: hidden;
}

/* Format the datatables */
table.dataTable {
    table-layout: fixed;
    width: 100%;
}

table.dataTable td {
    max-width: 300px;
    white-space: normal;
    word-wrap: break-word;
}

pre, code {
    white-space: pre-wrap;
    word-break: break-word;
}

table.dataTable thead select {
    width: 100%;
    box-sizing: border-box;
    padding: 4px;
    font-size: 0.9em;
}

/* Tooltip container */
.tooltip {
    position: relative;
    display: inline-block;
    border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
}

/* Tooltip text */
.tooltip .tooltiptext {
    visibility: hidden;
    bottom: 100%;
    left: 50%;
    width: 600px;
    background-color: #FFFFFF;
    color: black;
    text-align: left;
    padding: 18px;
    border-radius: 4px;
    border: 1px solid #000;

    /* Position the tooltip text - see examples below! */
    position: absolute;
    z-index: 1;
}

/* Show the tooltip text when you mouse over the tooltip container */
.tooltip:hover .tooltiptext {
    visibility: visible;
}


</style>
</head>
<body>
<h1>Diagnostic review summary data</h1>
Please note that this summary data is only for the first level in multilevel diagnostics.
For more complete information please look at the complete file specified.
The title of each column denotes the order in which calculations were made.
<p>
Files can be found either under the data directory of the cdds account within the Met Office or the mohc_shared
workspace on JASMIN.
<p>
Images under the plot column require you to know the access username and password, contact the UKCMIP7 project team if
you need this.

"""


def set_arg_parser() -> argparse.Namespace:
    """Creates an argument parser to take arguments from the command line.

    Returns
    -------
    argparse.Namespace
        The argument parser to handle command line arguments.
    """
    parser = argparse.ArgumentParser(description=("Reviews existing diagnostic data and generates a summary with links "
                                                  "to example plots summary information about the data."))
    parser.add_argument("model", help="The model to perform diagnostic review on.")

    return parser.parse_args()


def float_formatter(x) -> str:
    """Formats float values within the dataframe.

    Parameters
    ----------
    x:
        Numerical input value.

    Returns
    -------
    str
        Formatted numerical value.
    """
    if x < 1e-3:
        return f'{x:.3e}'
    else:
        return f'{x:.3f}'


def create_dataframe_from_csv(filepath: str) -> pd.DataFrame:
    """Reads the input summary CSV and creates a pandas dataframe using the content.

    Parameters
    ----------
    filepath: str
        The path to the summary csv file.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe containing the input csv file content.
    """
    pd.set_option('display.float_format', float_formatter)
    df = pd.read_csv(filepath,
                     names=[
                         'filename',
                         'variable',
                         'time: mean area: mean',
                         'time: mean area: max',
                         'time: mean area: min',
                         'time: max area: mean',
                         'time: max area: max',
                         'time: max area: min',
                         'time: min area: mean',
                         'time: min area: max',
                         'time: min area: min',
                         ])

    return df


def read_mappings_file(mapping_filepath: str) -> dict:
    """Reads the mappings file and returns its content as a dictionary.

    Parameters
    ----------
    mapping_filepath: str
        The path to the mappings file.

    Returns
    -------
    dict
        The mapping file content as a dictionary.
    """
    with open(mapping_filepath) as fh:
        mappings = json.load(fh)

    return mappings


def generate_mappings_dicts(mappings: dict) -> tuple[dict, dict, dict]:
    """Creates individual dictionaries using the mappings file content. Each dictionary contains the variable name as a
    key and then its assocaited information. 3 dictionaries are created, one holding label information, one holding the
    assocaited issue number and one holding the associated units.

    Parameters
    ----------
    mappings: dict
        The complete mappings dictionary read by read_mappings_file().

    Returns
    -------
    tuple[dict, dict, dict]
        A tuple of 3 dictionaries. One containing varaible name and associated labels, one containing variable name and
        the associated issue number and the last containing the variable name and the associated units.
    """
    labels = {}
    issues = {}
    units = {}

    for i in mappings:
        key = i['title'].split(" ")[1]
        labels[key] = " ".join(i['labels'])
        issues[key] = i['issue_number']
        units[key] = i['Data Request information']['Units']

    return labels, issues, units


def generate_df_variable_lists(mappings: dict, df: pd.DataFrame) -> tuple[list, list, list]:
    """Creates individual lists using the individual dictionaries created by generate_mappings_dicts(). 3 lists are
    created, one holding a list of labels as each item, one holding an issue number as each item and one holding units
    as each item.
model
    Parameters
    ----------
    mappings: dict
        The complete mappings dictionary read by read_mappings_file().
    df: pd.DataFrame
        Pandas dataframe containing the input csv file content.

    Returns
    -------
    tuple[list, list, list]
        A tuple of 3 lists. One containing labels, one containing issue numbers and the last containing units.
    """
    label_list = []
    issue_list = []
    units_list = []

    labels, issues, units = generate_mappings_dicts(mappings)
    for i in df['variable']:
        label_list.append(labels[i])
        issue_list.append('<a href="https://github.com/UKNCSP/CDDS-CMIP7-mappings/issues/{0}">{0}</a>'.format(issues[i]))
        units_list.append(units[i])

    return label_list, issue_list, units_list


def process_dataframe_parameters(mappings: dict, df: pd.DataFrame, model: str) -> pd.DataFrame:
    """Creates new and processes existing datarame parameters ready to format the html template. This funciton adds to
    the original dataframe created by create_dataframe_from_csv().

    Parameters
    ----------
    mappings: dict
        The complete mappings dictionary read by read_mappings_file().
    df: pd.DataFrame
        Pandas dataframe containing the input csv file content.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe containing the processed csv file content and additional fields.
    """
    df['variable'] = [i.replace('_', '.') for i in df['variable']]
    label_list, issue_list, units_list = generate_df_variable_lists(mappings, df)

    links_list = [(f'<a href="https://gws-access.ceda.ac.uk/public/mohc_shared/cmip7_diagnostic_review/{model.strip()}/'  # THIS MAY NEED TO BE UPDATED ALONG WITH IMAGE DIR WWHEN MORE INFO IS AVAILABLE
                   '{0}">{0}</a>'.format(os.path.basename(i).replace('.nc', '.png'))) for i in df['filename']]
    links = pd.DataFrame(links_list)

    df['units'] = units_list
    df['plot'] = links
    df['labels'] = label_list
    df['Github link'] = issue_list

    return df


def write_html(html_filename: str, html: str) -> None:
    """Saves the updated HTML.

    Parameters
    ----------
    html_filename: str
        The path to save the HTML file to.
    html: str
        The HTML file content.
    """
    with open(html_filename, 'w') as f:
        f.write(html)


def main():
    """Holds the main body of the script."""
    args = set_arg_parser()
    summary_csv_file = f"diagnostic_review/summary-{args.model.strip()}.csv"
    html_filename = f"docs/{args.model.strip()}.html"

    df = create_dataframe_from_csv(summary_csv_file)
    mappings = read_mappings_file(MAPPINGS_FILE_LOCATION)
    df = process_dataframe_parameters(mappings, df, args.model)

    a = HTML(df.to_html(escape=False, index=False))
    html = TEMPLATE_HTML
    html += a.data
    html += '</body></html>'
    html = html.replace('<table border="1" class="dataframe">',
                                          '<table border="1" class="dataframe" id="table_id">')

    write_html(html_filename, html)


if __name__ == "__main__":
    main()
