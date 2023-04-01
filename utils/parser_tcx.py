"""Parse a TCX file and return a Pandas DataFrame."""
import datetime as dt
import xml.etree.ElementTree as ET
import pandas as pd

METRIC_NOT_AVAILABLE = None
TIME_NOT_AVAILABLE = None


def parse_tcx_file(file_path):
  """Parse TCX file and return a Pandas DataFrame.

  Args:
    file_path: The file path of the TCSfile

  Returns:
    a Pandas DataFrame
  """

  tree = ET.parse(file_path)
  root = tree.getroot()

  # Get the namespace
  ns = {
      'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
      'tpx': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
  }

  activity = root.find('tcx:Activities/tcx:Activity', ns)
  start_time_element = activity.find('tcx:Id', ns) if activity else None
  start_time_str = (
      start_time_element.text
      if start_time_element is not None
      else TIME_NOT_AVAILABLE
  )
  try:
    start_time = dt.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%SZ')
  except ValueError:
    start_time = dt.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

  # Get the sport of the first activity
  if activity is not None:
    sport = activity.get('Sport')
  else:
    sport = ''

  data = []
  # Iterate through each trackpoint
  for trackpoint in root.findall('.//tcx:Trackpoint', ns):
    time_element = trackpoint.find('tcx:Time', ns)
    time_str = (
        time_element.text if time_element is not None else TIME_NOT_AVAILABLE
    )
    time = pd.Timestamp(time_str)
    heart_rate = get_metric(trackpoint, ns, 'tcx:HeartRateBpm/tcx:Value')

    position_element = trackpoint.find('tcx:Position', ns)
    latitude = get_metric(position_element, ns, 'tcx:LatitudeDegrees')
    longitude = get_metric(position_element, ns, 'tcx:LongitudeDegrees')
    altitude = get_metric(trackpoint, ns, 'tcx:AltitudeMeters')
    distance = get_metric(trackpoint, ns, 'tcx:DistanceMeters')
    extension_element = trackpoint.find('tcx:Extensions', ns)

    speed_km_per_hr = None
    if extension_element is not None:
      tpx_element = extension_element.find('tpx:TPX', ns)
      speed = get_metric(tpx_element, ns, 'tpx:Speed')
      if speed is not None:
        # Convert from m/s to km/hr
        speed_km_per_hr = round(float(speed) * 3.6, 2)

    position = {'lat': latitude, 'long': longitude}
    data.append({
        'time': time,
        'heart_rate': heart_rate,
        'position': position,
        'alt_meters': altitude,
        'distance_meters': distance,
        'speed_km_per_hr': speed_km_per_hr,
    })

  # Create the DataFrame
  df = pd.DataFrame(data)
  return df, sport, start_time


def get_metric(element, ns, xpath) -> float:
  """Extracts a metric from an XML element.

  Args:
    element (Element): The XML element to extract the metric from.
    ns (dict): A dictionary of XML namespaces used in the file.
    xpath (str): The XPath expression to locate the metric element.

  Returns:
    float: The value of the metric, or METRIC_NOT_AVAILABLE if the element is
    not found or the value is not a valid float.
  """
  try:
    metric_element = element.find(xpath, ns) if element is not None else None
    metric_value = (
        float(metric_element.text)
        if metric_element is not None
        else METRIC_NOT_AVAILABLE
    )
  except (AttributeError, ValueError, TypeError):
    metric_value = METRIC_NOT_AVAILABLE
  return metric_value
