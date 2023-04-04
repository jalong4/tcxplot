"""Plots distance over the time of the activity."""
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import mean_absolute_error
from utils import utils

ZOOM_LEVEL = 16


def get_distance_metrics(combined_df, ref_device, ratio, small_ratio):
  """Gets the summary metrics for distance data vs ref device."""

  # Find the ground truth line
  ref_data = combined_df[
      combined_df['device'].str.contains(ref_device, case=False)
  ]
  # Calculate metrics for each line
  rows = []

  ref_total_distance = ref_data['calc_distance_meters'].max()

  rows.append({
      'Device': f'Ref:\t({ref_device})',
      'MAE': '---',
      'Distance': round(ref_total_distance / 1000 * ratio, 4),
      'Variance': '---',
  })

  # Calculate the metrics for the other devices
  for device, data in combined_df.groupby('device'):
    if not device.lower().startswith(ref_device.lower()):
      device_data = data.dropna(subset=['calc_distance_meters'])
      merged_df = pd.merge(
          device_data, ref_data, on='time', how='outer', suffixes=('', '_ref')
      )
      # Drop any rows with missing values
      merged_df = merged_df.dropna(
          subset=['calc_distance_meters', 'calc_distance_meters_ref']
      )
      # measure MEA in smaller unit (ft or meters)
      if not merged_df.empty:
        mae = mean_absolute_error(
            merged_df['calc_distance_meters'] * small_ratio,
            merged_df['calc_distance_meters_ref'] * small_ratio,
        )
        total_distance = (
            device_data['calc_distance_meters'].max()
        )

        var = '---'
        if device != ref_device:
          var = (
              format(
                  ((total_distance - ref_total_distance) / ref_total_distance)
                  * 100.0,
                  '.2f',
              )
              + '%'
          )
        row = {
            'Device': device.replace(' ', '\t'),
            'MAE': round(mae, 2),
            'Distance': round(total_distance / 1000 * ratio, 4),
            'Variance': var
        }
        rows.append(row)

  metrics_table = pd.DataFrame(rows)
  return metrics_table


def has_valid_position(row):
  position = row['position']
  return position['lat'] is not None and position['long'] is not None


def plot_distance(df, ref_device, sport, start_time, unit_of_measure):
  """plots distance data for a given dataframe.

  Args:
    df:  the dataframe containing the data
    ref_device: the reference test device label
    sport: specifices the sport eg. Biking for which the data was generated
    start_time: start time of the activity
    unit_of_measure:  IMPERIAL or METRIC

  Returns:
    fig:  A plot of the distances for the activity

  """

  mae_label = 'MAE\t(m)'
  distance_label = 'Distance (km)'
  distance_label_short = 'km'
  ratio = 1.0
  small_ratio = 1.0
  if unit_of_measure == utils.UnitOfMeasure.IMPERIAL:
    ratio = utils.KM_TO_MILE_RATIO
    small_ratio = utils.M_TO_FT_RATIO
    distance_label = 'Distance (mi)'
    distance_label_short = 'mi'
    mae_label = 'MAE\t(ft)'

  metrics_table = get_distance_metrics(df, ref_device, ratio, small_ratio)
  # Calculate the duration
  min_time = df['time'].min()
  max_time = df['time'].max()
  duration = max_time - min_time
  minutes, seconds = divmod(duration.seconds, 60)

  # Calculate the maximum distance across all dataframes
  max_distance_m = 0
  for _, data in df.groupby('device'):
    max_distance_m = max(max_distance_m, df['calc_distance_meters'].max())
  max_distance = round(max_distance_m / 1000 * ratio, 4)

  # Create a single plot with two traces
  fig = go.Figure()

  # Set the y-axis range to start at 0
  fig.update_layout(yaxis_range=[0, max_distance * 1.25])

  # Filter the DataFrame to keep only rows with non-null position data
  df_with_position = df[
      df['position'].apply(lambda pos: has_valid_position({'position': pos}))
  ]

  # Filter the DataFrame to keep only rows with non-null distance data
  df_with_position_and_distance = df_with_position.dropna(
      subset=['calc_distance_meters']
  )

  # Group the filtered DataFrame by 'device'
  grouped_data = df_with_position_and_distance.groupby('device')

  # Add a trace for the distance data
  for device, data in grouped_data:
    distance = data['calc_distance_meters'] / 1000 * ratio

    fig.add_trace(
        go.Scatter(
            x=data['time'],
            y=distance,
            mode='lines',
            name=device,
            legendgroup=device,
            showlegend=True
        )
    )

  # Set the title and devices
  fig.update_layout(
      title=dict(
          text=(f'Distance ({sport}) - {start_time}'),
          font=dict(size=20, color='black'),
          yanchor='top',
          y=0.95,
          xanchor='center',
          x=0.5,
      ),
      xaxis_title=f'Duration: {minutes}m {seconds}s',
      yaxis_title=distance_label,
      plot_bgcolor='white',
      xaxis=dict(linecolor='black'),
      yaxis=dict(linecolor='black'),
      legend=dict(
          orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5
      ),
      margin=dict(l=20, r=20, t=20, b=20),
      height=600,
      width=1200
  )

  # Add the metrics table above the x-axis, in the bottom right corner of the
  # plot
  fig.add_trace(
      go.Table(
          columnwidth=[2.5, 1, 1, 1],
          header=dict(
              values=['Device', mae_label, distance_label_short, '+/-\t(%)'],
              fill_color='paleturquoise',
              align=['left', 'right', 'right', 'right'],
              font=dict(size=14),
              height=40
          ),
          cells=dict(
              values=[
                  metrics_table['Device'],
                  metrics_table['MAE'],
                  metrics_table['Distance'],
                  metrics_table['Variance'],
              ],
              fill_color='lavender',
              align=['left', 'right', 'right', 'right'],
              font=dict(size=12),
              height=30

          ),
          domain=dict(x=[0.6, 1.0], y=[0.01, 0.3]),
      )
  )

  return fig
