"""Process all TCX and GPS files in the given data folder."""

import os
import webbrowser

import pandas as pd
import plotly.io as pio

from utils import calc_distance, calc_speed, combine_html, map_activity, parser, plot_distance, plot_heart_rate, plot_speed, utils


def process_files(folder_path, output_dir, google_maps_api_key, launch_browser,
                  ground_truth_device, ref_device, unit_of_measure):
  """Process each data file in the data folder.

  Args:
    folder_path: Folder containing the data files
    output_dir: Folder to save the results
    google_maps_api_key: Required for the map output to render
    launch_browser: determines if browser opens automatically
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
    if sport and sport != 'Unknown':
      sports.add(sport)
    if start_time:
      start_times.add(start_time)

    file_name = os.path.splitext(os.path.basename(f))[0]
    df['device'] = file_name
    dfs.append(df)

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


