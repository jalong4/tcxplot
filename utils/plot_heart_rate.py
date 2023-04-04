"""Plots heart rate data."""

import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import mean_absolute_error

ZOOM_LEVEL = 16


def get_heart_rate_metrics(combined_df, ground_truth_device):
  """Gets the summary metrics for heart rate data vs gt device."""

  # Find the ground truth line
  ground_truth = combined_df[
      combined_df['device'].str.contains(ground_truth_device, case=False)
  ]
  # Calculate metrics for each line
  rows = []
  # Calculate the average heart rate and variance for GT Device
  gt_avg_heart_rate = round(ground_truth['heart_rate'].mean(), 2)

  rows.append({
      'Device': f'GT ({ground_truth_device})',
      'MAE': '---',
      'avgBPM': gt_avg_heart_rate,
      'Variance': '---',
  })

  # Calculate the metrics for the other devices
  for device, data in combined_df.groupby('device'):
    if not device.lower().startswith(ground_truth_device.lower()):
      device_data = data.dropna(subset=['heart_rate'])
      merged_data = data.merge(ground_truth, on='time', how='inner',
                               suffixes=('', '_gt'))

      merged_data = merged_data.dropna(subset=['heart_rate', 'heart_rate_gt'])
      if not merged_data.empty:
        mae = mean_absolute_error(merged_data['heart_rate'],
                                  merged_data['heart_rate_gt'])
        avg_heart_rate = round(device_data['heart_rate'].mean(), 2)
        var = (
            round(avg_heart_rate - gt_avg_heart_rate, 2)
            if device != ground_truth_device
            else '-'
        )
        row = {
            'Device': device,
            'MAE': round(mae, 2),
            'avgBPM': avg_heart_rate,
            'Variance': var,
        }
        rows.append(row)
    else:
      gt_device = device

  if gt_device is not None:
    rows[0]['Device'] = gt_device

  metrics_table = pd.DataFrame(rows)
  return metrics_table


def plot_heart_rate(df, ground_truth_device, sport, start_time):
  """plots heart rate data for a given dataframe.

  Args:
    df:  the dataframe containing the data
    ground_truth_device: The label for the device considered to be the source
                         of truth for heart rate data
    sport: specifices the sport eg. Biking for which the data was generated
    start_time: start time of the activity

  Returns:
    fig:  A plot of the heart rates for the activity

  """

  metrics_table = get_heart_rate_metrics(df, ground_truth_device)

  # Calculate the duration
  min_time = df['time'].min()
  max_time = df['time'].max()
  duration = max_time - min_time
  minutes, seconds = divmod(duration.seconds, 60)

  # Create a single plot with two traces
  fig = go.Figure()

  # Add a trace for the heart rate data
  for device, data in df.groupby('device'):
    fig.add_trace(
        go.Scatter(
            x=data['time'],
            y=data['heart_rate'],
            mode='lines',
            name=device,
            legendgroup=device,
        )
    )

  # Set the title and devices
  fig.update_layout(
      title=dict(
          text=(f'Heart Rate ({sport}) - {start_time}'),
          font=dict(size=20, color='black'),
          yanchor='top',
          y=0.95,
          xanchor='center',
          x=0.5,
      ),
      xaxis_title=f'Duration: {minutes}m {seconds}s',
      yaxis_title='Heart Rate (BPM)',
      plot_bgcolor='white',
      xaxis=dict(linecolor='black'),
      yaxis=dict(linecolor='black'),
      legend=dict(
          orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5
      ),
      margin=dict(l=50, r=50, t=50, b=20),
      height=600
  )

  # Add the metrics table above the x-axis, in the bottom right corner of the
  # plot
  fig.add_trace(
      go.Table(
          columnwidth=[2.0, 1.2, 1.2, 1.2],
          header=dict(
              values=['Device', 'MAE vs GT', 'Avg BPM', 'BPM vs GT'],
              fill_color='paleturquoise',
              align=['left', 'right', 'right', 'right'],
              font=dict(size=14),
              height=40
          ),
          cells=dict(
              values=[
                  metrics_table['Device'],
                  metrics_table['MAE'],
                  metrics_table['avgBPM'],
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

