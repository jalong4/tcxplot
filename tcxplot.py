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
import webbrowser
import sys
import pandas as pd
import plotly.io as pio


sys.path.append('/home/user/myproject')
from utils import calc_distance
from utils import calc_speed
from utils import combine_html
from utils import map_activity
from utils import parser
from utils import plot_distance
from utils import plot_heart_rate
from utils import plot_speed
from utils import utils


def process_files(folder_path, output_dir, google_maps_api_key, launch_browser,
                  ground_truth_device, ref_device, unit_of_measure):
  """Process each data file in the data folder.

  Args:
    folder_path: Folder containing the data files
    output_dir: Folder to save the results
    google_maps_api_key: Required for the map output to render
    launch_browser: determines if browser opens automatically (default: True)
    ground_truth_device:  the string used to determine GT device
    ref_device:  the string used to determine the ref device
    unit_of_measure:  imperial or metric

  Raises:
    <Any>:
  """
  # Read all TCX and GPX files in the specified folder
  file_paths = [
      os.path.join(folder_path, f)
      for f in os.listdir(folder_path)
      if f.lower().endswith('.tcx') or f.lower().endswith('.gpx')
  ]

  dfs = []
  sports = set()
  start_times = set()
  sport = None
  for f in file_paths:
    print('File: ', f)
    df, sport, start_time = parser.parse_file(f)
    df = df.dropna(subset=['time'])
    if all(
        df['position'].apply(
            lambda pos: pos.get('lat') is not None
            and pos.get('long') is not None
        )
    ):
      df['calc_distance_meters'] = calc_distance.calc_distance_haversine(df)
      df['speed_kmh'] = calc_speed.calc_speed(df)
    if sport:
      sports.add(sport)
    if start_time:
      start_times.add(start_time)

    file_name = os.path.splitext(os.path.basename(f))[0]
    df['device'] = file_name
    dfs.append(df)

  # Check if all files are the same sport
  if len(sports) > 1:
    raise ValueError('All data files must be of the same sport.')

  sport = 'Unknown'
  if sports:
    sport = sports.pop()

  if start_times:
    start_time = start_times.pop()
  else:
    start_time = None

  start_time_string = 'Unknown Time'
  if start_time is not None:
    start_time_string = utils.to_local_time_string(start_time)
    print('Start Time: ', start_time_string)

  # Combine all DataFrames into a single DataFrame
  combined_df = pd.concat(dfs)

  # Convert the time column to local time
  combined_df['time'] = combined_df['time'].apply(utils.to_local_time)

  heart_rate_fig = plot_heart_rate.plot_heart_rate(
      combined_df, ground_truth_device, sport, start_time_string
  )

  distance_fig = plot_distance.plot_distance(
      combined_df, ref_device, sport, start_time_string, unit_of_measure)

  speed_fig = plot_speed.plot_speed(
      combined_df, sport, start_time_string, unit_of_measure
  )

  base_filename = os.path.join(
      output_dir, f'{sport}_{utils.to_local_time(start_time).date()}'
  )
  base_filename = base_filename.replace(' ', '_')
  hr_filename = base_filename + '-hr.html'
  distance_filename = base_filename + '-distance.html'
  speed_filename = base_filename + '-speed.html'

  pio.write_html(speed_fig, speed_filename)
  map_filename = base_filename + '-map.html'

  pio.write_html(distance_fig, distance_filename)
  pio.write_html(heart_rate_fig, hr_filename)

  # Create a google map of the activity
  map_html_string = map_activity.map_activity(
      combined_df, sport, google_maps_api_key, unit_of_measure
  )
  if map_html_string:
    with open(map_filename, 'w') as f:
      f.write(map_html_string)

  combined_filename = base_filename + '.html'
  combine_html.combine_html(
      combined_filename,
      [hr_filename, distance_filename, speed_filename, map_filename],
      ['Heart Rate', 'Distance', 'Speed', 'Map'])

  if os.path.exists(combined_filename):
    # delete the individual files
    if os.path.exists(hr_filename):
      os.remove(hr_filename)
    if os.path.exists(distance_filename):
      os.remove(distance_filename)
    if os.path.exists(speed_filename):
      os.remove(speed_filename)
    if os.path.exists(map_filename):
      os.remove(map_filename)

  url = f'file://{os.path.abspath(combined_filename)}'

  if launch_browser:
    print('launching browser with results')
    webbrowser.open_new_tab(url)


def main():
    parser = argparse.ArgumentParser(description='Process xml files for sensor testing activities.')
    parser.add_argument('data_folder', type=str, help='Path to folder containing TCX/GPX files')
    parser.add_argument('--output_dir', type=str, required=True, help='the output folder to save results')
    parser.add_argument('--key', type=str, help='Google maps API key, alternatively set env GOOGLE_MAPS_API_KEY')
    parser.add_argument('--gt', type=str, default='Polar', help='Specifies the ground truth device for heart rate (default: Polar)')
    parser.add_argument('--ref', type=str, default='Apple', help='Specifies the reference device (default: Apple)')
    parser.add_argument('--launch_browser', action='store_true', help='Automatically launch the webview on the resulting html file')
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