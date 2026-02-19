import argparse
import iris
import iris.cube
import matplotlib.pyplot as plt
import os
import csv

from iris.quickplot import pcolormesh
from pathlib import Path

UKCM2_IMAGE_DIR = "diagnostic_review/UKCM2-0-LL_images"
UKCM2_SUMMARY_DATA_FILE_LOCATION = "diagnostic_review/summary-UKCM2.csv"


def set_arg_parser() -> argparse.Namespace:
    """Creates an argument parser to take arguments from the command line.

    Returns
    -------
    argparse.Namespace
        The argument parser to handle command line arguments.
    """
    parser = argparse.ArgumentParser(description=("Reviews existing diagnostic data and generates a sumarry with "
                                                  "example plots for any new data files found within the data_dir that "
                                                  "have not yet been processed."))
    parser.add_argument("data_dir", help="The full path to the directory containing the data ready for processing.")

    return parser.parse_args()


def read_summary_csv_file(summary_file: Path) -> list:
    """Reads the contents of the existing summary csv file and returns the contents as a list where each item is a row
    from the csv. Note that this CSV file should not contain headers and is expected to have the data type formatting:
    string, string, float, float, float, float, loat, float, float, float, float

    Parameters
    ----------
    summary_file: Path
        The path to the existing csv summary file.

    Returns
    -------
    list
        The summary csv file content as a list where each item is a row.
    """
    summary_data = []
    with open(summary_file) as myfile:
        r = csv.reader(myfile)
        for row in r:
            summary_data.append(row)

    return summary_data


def extract_cube_from_data(datafile: str) -> iris.cube.Cube:
    """Reviews a single datafile and extracts ands processes the appropriate cube.

    Parameters
    ----------
    datafile: str
        The path to the data file.

    Returns
    -------
    <class 'iris.cube.Cube'>
        The data cube to be processed.

    Raises
    ------
    RuntimeError
        If no cube can be found in the datafile. In this case, the faulty datafile and the extracted cube list is
        printed to the user for debugging.
    """
    cube_list = iris.load(datafile)
    cube = None
    for i in cube_list:
        if 'time' in [j.name() for j in i.dim_coords]:
            cube = i
    if cube is None:
        raise RuntimeError(f"No cube found for {datafile}.\n{cube_list}")
    if len(cube.shape) > 3:
        try:
            cube = cube.slices(['time', 'latitude', 'longitude']).next()
        except ValueError:
            cube = cube.extract(iris.Constraint(depth=0))

    cube.attributes['realm'] = cube.attributes['realm'].split(" ")[0]

    return cube


def get_cmip7_compound_name(cube: iris.cube.Cube) -> str:
    """Generates the CMIP7 compound name based off of the cube attributes for a single cube.

    Parameters
    ----------
    cube: <class 'iris.cube.Cube'>
        The cube.

    Returns
    -------
    str
        The CMIP7 compound name.
    """
    return '{realm}.{branded_variable}.{frequency}.{region}'.format(**cube.attributes)


def summary_string(cube: iris.cube.Cube) -> str:
    """Generates the summary string containing mean, maximum and minimum cube data to be appended to the summary data
    csv file for a single cube.

    Parameters
    ----------
    cube: <class 'iris.cube.Cube'>
        The cube.

    Returns
    ---------
    str
        The summary string containing mean, maximum and minimum cube data.
    """
    return f'(mean = {cube.data.mean():03f}, max = {cube.data.max():03f}, min = {cube.data.min():03f})'


def summarise_data(name: str, cubes: list) -> list:
    """Summarises the data for each cube in a single datafile.

    Parameters
    ----------
    name: str
        The CMIP7 compound name.
    cubes: list
        The list of cubes to process.

    Returns
    -------
    list
        The summarised data as a list of floats for each cube.
    """
    result = [name]

    for cube in cubes:
        result += [float(i) for i in [cube.data.mean(), cube.data.max(), cube.data.min()]]

    return result


def get_cube_means(cube: iris.cube.Cube) -> iris.cube.Cube:
    """Returns a cube of the mean over the time dimension for a single cube.

    Parameters
    ----------
    cube: <class 'iris.cube.Cube'>
        The cube.

    Returns
    -------
    <class 'iris.cube.Cube'>
        A cube of the mean of the input cube along the time dimension.
    """
    return cube.collapsed('time', iris.analysis.MEAN)


def get_cube_max(cube: iris.cube.Cube) -> iris.cube.Cube:
    """Returns a cube of the maximum over the time dimension for a single cube.

    Parameters
    ----------
    cube: <class 'iris.cube.Cube'>
        The cube.

    Returns
    -------
    <class 'iris.cube.Cube'>
        A cube of the maximum of the input cube along the time dimension.
    """
    return cube.collapsed('time', iris.analysis.MAX)


def get_cube_min(cube: iris.cube.Cube) -> iris.cube.Cube:
    """Returns a cube of the minimum over the time dimension for a single cube.

    Parameters
    ----------
    cube: <class 'iris.cube.Cube'>
        The cube.

    Returns
    -------
    <class 'iris.cube.Cube'>
        A cube of the minimum of the input cube along the time dimension.
    """
    return cube.collapsed('time', iris.analysis.MIN)


def generate_plots(cube: iris.cube.Cube, imgfile: str) -> None:
    """Generates plots of the mean, maximum and minimum values for a single cube.

    Parameters
    ----------
    cube: <class 'iris.cube.Cube'>
        The cube.
    img_file: str
        The full path that the generated plot will be saved as.
    """
    mean_result = get_cube_means(cube)
    max_result = get_cube_max(cube)
    min_result = get_cube_min(cube)

    cmap = 'RdBu_r'
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    plt.sca(axes[0])
    pcolormesh(mean_result, cmap=cmap)
    plt.title('Time mean\n' + summary_string(mean_result))

    plt.sca(axes[1])
    pcolormesh(max_result, cmap=cmap)
    plt.title('Time max\n' + summary_string(max_result))

    plt.sca(axes[2])
    pcolormesh(min_result, cmap=cmap)
    plt.title('Time min\n' + summary_string(min_result))

    # plt.savefig(imgfile)
    # plt.close(fig)
    plt.show()


def update_summary_data(cube: iris.cube.Cube, summary_data: list, filename: str) -> list:
    """Updates the list of summary data on processed cubes ready to be saved back to the summary csv file.

    Parameters
    ----------
    cube: <class 'iris.cube.Cube'>
        The cube.
    summary_data: list
        The summary csv file content as a list where each item is a row.
    fielname: str
        The name of the data file.

    Returns
    -------
    list
        The updated summary csv file content as a list where each item is a row contianing newly processed data.
    """
    cmip7_compound_name = get_cmip7_compound_name(cube)
    mean_result = get_cube_means(cube)
    max_result = get_cube_max(cube)
    min_result = get_cube_min(cube)

    summary_data.append([filename] + summarise_data(cmip7_compound_name, [mean_result, max_result, min_result]))

    return summary_data


def write_summary_csv_file(summary_file: Path, summary_data) -> None:
    """Writes out and saves the newly updated summary data to the csv files for future use.

    Parameters
    ----------
    summary_file: Path
        The path to the existing csv summary file.
    summary_data: list
        The updated summary csv file content as a list where each item is a row contianing newly processed data.
    """
    with open(summary_file, 'w') as myfile:
        wr = csv.writer(myfile)
        for row in summary_data:
            wr.writerow(row)


def main():
    """Holds the main body of the script."""
    args = set_arg_parser()
    summary_file = UKCM2_SUMMARY_DATA_FILE_LOCATION
    summary_data = read_summary_csv_file(summary_file)

    files_done = [i[0] for i in summary_data]
    for root, directories, files in os.walk(args.data_dir):
        for filename in files:
            datafile = os.path.join(root, filename)
            if filename in files_done:
                print(f"{datafile} already done")
                continue

            image_file = os.path.join(UKCM2_IMAGE_DIR, filename[:-3] + '.png')
            try:
                cube = extract_cube_from_data(datafile)
                generate_plots(cube, image_file)
                summary_data = update_summary_data(cube, summary_data, filename)
            except ValueError:
                print(f"ERROR: {datafile}")

    # write_summary_csv_file(summary_file, summary_data)


if __name__ == "__main__":
    main()
