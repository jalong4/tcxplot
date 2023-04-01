"""Calculates speed over the time of the activity."""
import pandas as pd

def calc_speed(df):
  """calculated speed data for a given dataframe.

  Args:
    df:  the dataframe containing the data

  Returns:
    data:  a data series of the speed

  """
  # Filter the DataFrame to keep only rows with non-null distance data
  df_with_distance = df.dropna(subset=['calc_distance_meters'])

  # calculate time difference between consecutive rows
  time_diff = (
      df_with_distance['time'] - df_with_distance['time'].shift()
  ).fillna(pd.Timedelta(seconds=0))
  # convert time difference to hours
  time_diff_hours = time_diff.apply(lambda x: x.total_seconds() / 3600)
  # calculate speed in km/h
  speed_kmh = (
      (
          df_with_distance['calc_distance_meters']
          - df_with_distance['calc_distance_meters'].shift()
      )
      / time_diff_hours
      / 1000.0
  )

  return speed_kmh
