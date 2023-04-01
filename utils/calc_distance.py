"""Calculate a data frame of distance values for each gps coordinate."""
import numpy as np
import pandas as pd


def _haversine(lat1, lon1, lat2, lon2):
  # convert decimal degrees to radians
  lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

  # haversine formula
  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
  c = 2 * np.arcsin(np.sqrt(a))
  r = 6371  # radius of earth in kilometers
  return c * r * 1000


def calc_distance_haversine(df: pd.DataFrame) -> pd.Series:
  """Calculate the cumulative distance between consecutive GPS coordinates.

  It uses the Haversine formula.  The haversine formula is a more accurate
  way to calculate distances between GPS coordinates, as it takes into
  account the curvature of the Earth.

  Args:
      df (pd.DataFrame): A pandas DataFrame containing GPS data.

  Returns:
      pd.Series: A pandas Series of cumulative distances between consecutive
      GPS coordinates.
  """
  # extract latitude and longitude from 'position' column
  df['latitude'] = df['position'].apply(lambda pos: pos['lat'])
  df['longitude'] = df['position'].apply(lambda pos: pos['long'])

  # calculate distance for each pair of consecutive GPS coordinates
  distances = [
      _haversine(
          df['latitude'][i],
          df['longitude'][i],
          df['latitude'][i + 1],
          df['longitude'][i + 1],
      )
      for i in range(len(df) - 1)
  ]

  # add distance values to Series and make cumulative
  result = pd.Series([0] + distances)
  result_cumulative = result.cumsum()
  return result_cumulative
