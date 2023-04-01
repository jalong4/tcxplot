r"""Script for processing xml files for sensor testing activities."""

USAGE = """
data_folder:  Path to folder containing TCX/GPX files
optional arguments:
  --output_dir: the output folder to save results (default: NONE)
  --gt: Ground Truth device (default: Polar)
  --ref: Ground Truth device (default: Apple)
  --key: Google Maps API key (default: None)
  --launch_browser: determines if browser opens automatically (default: True)
  --units: determine the unit of measure; imperial or metric (default: imperial)
"""


import argparse
import os
import sys

from utils.process_files import process_files

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Append the subdirectory to the path
project_dir = os.path.join(current_dir, 'utils')
sys.path.insert(0, project_dir)

# Import the required module from the subdirectory
from utils import utils


def main():
    parser = argparse.ArgumentParser(description='Process xml files for sensor testing activities.')
    parser.add_argument('data_folder', type=str, help='Path to folder containing TCX/GPX files')
    parser.add_argument('--output_dir', type=str, required=True, help='the output folder to save results')
    parser.add_argument('--key', type=str, help='Google maps API key, alternatively set env GOOGLE_MAPS_API_KEY')
    parser.add_argument('--gt', type=str, default='Polar', help='Specifies the ground truth device for heart rate (default: Polar)')
    parser.add_argument('--ref', type=str, default='Apple', help='Specifies the reference device (default: Apple)')
    parser.add_argument('--launch_browser', action='store_true', help='Automatically launch the webview on the resulting html file')
    parser.add_argument('--no-launch_browser', dest='launch_browser', action='store_false', help='Do not launch the webview on the resulting html file')
    parser.add_argument('--units', type=str, default='metric', help='Specifies the units of measure. Options are metric or imperial (default: metric)')

    args = parser.parse_args()

    # Set variables based on command line arguments
    data_folder = args.data_folder
    output_dir = args.output_dir
    google_maps_api_key = args.key or os.getenv('GOOGLE_MAPS_API_KEY')
    ground_truth_device = args.gt
    ref_device = args.ref
    launch_browser = args.launch_browser
    unit_of_measure_string = args.units

    # Convert the unit of measure string to a UnitOfMeasure enum value
    try:
        unit_of_measure = utils.UnitOfMeasure[unit_of_measure_string.upper()]
    except KeyError:
        print(f'Invalid unit of measure: {unit_of_measure_string}')
        print('Using metric...')
        unit_of_measure = utils.UnitOfMeasure.METRIC

    # Call the function that processes the files and creates the output
    process_files(data_folder, output_dir, google_maps_api_key, launch_browser,
                  ground_truth_device, ref_device, unit_of_measure)


if __name__ == '__main__':
    main()