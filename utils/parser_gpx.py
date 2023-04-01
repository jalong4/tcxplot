"""Parse a GPX file and return a Pandas DataFrame."""
import datetime as dt
import xml.etree.ElementTree as ET
import pandas as pd

METRIC_NOT_AVAILABLE = None
TIME_NOT_AVAILABLE = None


def parse_gpx_file(file_path):
  """Parse GPX file and return a Pandas DataFrame.

  Args:
    file_path: The file path of the GPX file

  Returns:
    a Pandas DataFrame
  """

  # Load the XML file into an ElementTree object
  tree = ET.parse(file_path)
  root = tree.getroot()

  ns = {
      'gpx': 'http://www.topografix.com/GPX/1/1',
      'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1',
  }

  start_time_element = root.find('.//gpx:metadate', ns)
  start_time_str = (
      start_time_element.text if start_time_element is not None
      else TIME_NOT_AVAILABLE
  )
  try:
    start_time = dt.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%SZ')
  except ValueError:
    start_time = dt.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

  # Extract the data into a list of dictionaries
  data = []

  for trkpt in root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt'):
    time_element = trkpt.find(
        '{http://www.topografix.com/GPX/1/1}time')
    time_str = (
        time_element.text if time_element is not None else TIME_NOT_AVAILABLE
    )
    time = pd.Timestamp(time_str)

    hr_element = trkpt.find(
        './/{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr')
    hr = (
        int(hr_element.text) if hr_element is not None else METRIC_NOT_AVAILABLE
    )

    position = {'lat': float(trkpt.get('lat')), 'long': float(trkpt.get('lon'))}
    data.append({
        'time': time,
        'heart_rate': hr,
        'position': position,
        'alt_meters': METRIC_NOT_AVAILABLE,
        'distance_meters': METRIC_NOT_AVAILABLE,
        'speed': METRIC_NOT_AVAILABLE,
    })

  # Convert the list of dictionaries into a pandas DataFrame
  df = pd.DataFrame(data)
  return df, '', start_time
