"""Plots speed over the time of the activity."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from utils import utils

ZOOM_LEVEL = 16


def plot_speed(df, sport, start_time, unit_of_measure):
  """plots speed data for a given dataframe.

  Args:
    df:  the dataframe containing the data
    sport: specifices the sport eg. Biking for which the data was generated
    start_time: start time of the activity
    unit_of_measure:  IMPERIAL or METRIC

  Returns:
    fig:  A plot of the speeds for the activity

  """
  speed_label = 'Avg\tSpeed\t(km/h)'
  yaxis_title = 'Speed (km/h)'
  ratio = 1.0
  if unit_of_measure == utils.UnitOfMeasure.IMPERIAL:
    ratio = utils.KM_TO_MILE_RATIO
    yaxis_title = 'Speed (mph)'
    speed_label = 'Avg\tSpeed\t(mph)'

  # Calculate the duration
  min_time = df['time'].min()
  max_time = df['time'].max()
  duration = max_time - min_time
  minutes, seconds = divmod(duration.seconds, 60)

  # Create a single plot with two traces
  fig = go.Figure()

  # Filter the DataFrame to keep only rows with non-null speed data
  df_with_speed = df.dropna(
      subset=['speed_kmh']
  )
  max_speed = df_with_speed['speed_kmh'].max() * ratio

  # Set the y-axis range to start at 0 km
  fig.update_layout(yaxis_range=[0, max_speed * 1.2])

  # Group the filtered DataFrame by 'device'
  grouped_data = df_with_speed.groupby('device')

  metrics = []
  # Add a trace for the speed data
  for device, data in grouped_data:
    # calculate z-scores
    z_scores = np.abs(
        (data['speed_kmh'] - data['speed_kmh'].mean()) / data['speed_kmh'].std()
    )

    # identify outliers with z-score > 3
    outliers = data[z_scores > 3]

    # calculate total distance and total time
    total_distance = data['calc_distance_meters'].iloc[-1] / 1000.0 * ratio
    total_time = (
        data['time'].iloc[-1] - data['time'].iloc[0]
    ).total_seconds() / 3600

    # calculate average speed
    avg_speed = total_distance / total_time

    metrics.append({
        'Device': device.replace(' ', '\t'),
        'AvgSpeed': round(avg_speed, 2),
        'Outliers': len(outliers),
    })

    fig.add_trace(
        go.Scatter(
            x=data['time'],
            y=data['speed_kmh'] * ratio,
            mode='lines',
            name=device,
            legendgroup=device,
            showlegend=True
        )
    )
    # plot the outliers separately with a different symbol
    fig.add_trace(
        go.Scatter(
            x=outliers['time'],
            y=outliers['speed_kmh'] * ratio,
            mode='markers',
            marker=dict(symbol='x', size=10),
            name=f'{device} Outliers',
            legendgroup=device,
            showlegend=True
        )
    )

  metrics_table = pd.DataFrame(metrics)
  fig.add_trace(
      go.Table(
          columnwidth=[2.5, 1.7, 1],
          header=dict(
              values=['Device', speed_label, 'Outliers'],
              fill_color='paleturquoise',
              align=['left', 'right', 'right'],
              font=dict(size=14),
              height=40
          ),
          cells=dict(
              values=[
                  metrics_table['Device'],
                  metrics_table['AvgSpeed'],
                  metrics_table['Outliers'],
              ],
              fill_color='lavender',
              align=['left', 'right', 'right'],
              font=dict(size=12),
              height=30

          ),
          domain=dict(x=[0.6, 1.0], y=[0.0, 0.0]),
      )
  )

  # Set the title and devices
  fig.update_layout(
      title=dict(
          text=(f'Speed ({sport}) - {start_time}'),
          font=dict(size=20, color='black'),
          yanchor='top',
          y=0.95,
          xanchor='right',
          x=0.5,
      ),
      xaxis_title=f'Duration: {minutes}m {seconds}s',
      yaxis_title=yaxis_title,
      plot_bgcolor='white',
      xaxis=dict(linecolor='black'),
      yaxis=dict(linecolor='black'),
      legend=dict(
          orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5
      ),
      margin=dict(l=20, r=20, t=20, b=20),
      height=800,
      width=1200
  )

  return fig
