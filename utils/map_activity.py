"""Maps an activity based on the GPS data in the given DataFrame."""

import json

import pandas as pd

from utils import utils


def map_activity(df, sport, api_key, unit_of_measure):
  """Maps an activity based on the GPS data in the given DataFrame.

  Args:
    df: A combined DataFrame containing the data of all devices.
    sport: The sport of the activity, used in the title
    api_key: Google API key used for mapping.
    unit_of_measure: IMPERIAL or METRIC

  Returns:
    The HTML content of the map.
  """

  # Remove rows with missing position data
  df = df[
      df['position'].notnull()
      & df['position'].apply(lambda x: x['lat']).notnull()
      & df['position'].apply(lambda x: x['long']).notnull()
  ]

  if 'position' not in df.columns:
    print('No gps data found for any device')
    return ''

  # Set the zoom level of the map
  zoom_level = 16

  distance_label = 'Distance (km)'
  speed_label = 'Speed (km/h)'
  ratio = 1.0
  if unit_of_measure == utils.UnitOfMeasure.IMPERIAL:
    ratio = utils.KM_TO_MILE_RATIO
    distance_label = 'Distance (mi)'
    speed_label = 'Speed (mph)'


  # Create the map URL
  map_url = 'https://maps.googleapis.com/maps/api/js?key={api_key}'.format(
      api_key=api_key
  )

  # Set the center of the map to the average lat and long of all points

  center_lat = round(float(df['position'].apply(lambda x: x['lat']).mean()), 5)
  center_long = round(
      float(df['position'].apply(lambda x: x['long']).mean()), 5)

  print(f'lat: {center_lat}, {center_long}' + f' zoom: {zoom_level}')

  # Create the HTML content of the map
  html_content = '''
      <!DOCTYPE html>
      <html>
          <head>
              <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
              <meta charset="utf-8">
              <title>{sport} Activity Map</title>
              <style>
                  #map {{
                      height: 80%;
                      max-height: 800px;
                  }}
                  html, body {{
                      height: 100%;
                      margin: 0;
                      padding: 0;
                  }}
              </style>
              <script src="{map_url}"></script>
              <script>
                function initMap() {{
                    var map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: {zoom_level},
                        center: {{lat: {center_lat}, lng: {center_long}}},
                        mapTypeId: google.maps.MapTypeId.HYBRID
                    }});

                    function createMarkerIcon(color) {{
                        return {{
                            path: google.maps.SymbolPath.CIRCLE,
                            scale: 4,
                            fillColor: color,
                            fillOpacity: 1,
                            strokeWeight: 0
                        }};
                    }}

                    var deviceColors = {device_colors_json};
                    var locations = {locations_json};

                    for (var i = 0; i < locations.length; i++) {{
                        var marker = new google.maps.Marker({{
                            position: locations[i].position,
                            map: map,
                            icon: createMarkerIcon(deviceColors[locations[i].device])
                        }});

                        // Attach click event to marker
                        attachClickEvent(marker, locations[i]);
                    }}

                    function attachClickEvent(marker, location) {{
                        var infowindow = new google.maps.InfoWindow({{
                            content: 'Device: ' + location.device + '<br>Time: ' + location.time + '<br>Heart Rate: ' + location.heart_rate  + '<br>' + location.distance_label + ' ' + location.distance + '<br>' + location.speed_label + ' ' + location.speed
                        }});

                        marker.addListener('click', function() {{
                            infowindow.open(map, marker);
                        }});
                    }}
                }}
            </script>
          </head>
          <body onload="initMap()">
              <div id="map"></div>
          </body>
      </html>
  '''

  colors = ['red', 'blue', 'green', 'purple', 'brown']

  # Generate the list of GPS locations and assign colors to device
  device_colors = {}
  locations = []
  color_index = 0
  for device, data in df.groupby('device'):
    print(f'Mapping: {device}')
    if 'position' not in data.columns or data['position'].isnull().all():
      print('No gps data for device: ', device)
      continue

    if device not in device_colors:
      device_colors[device] = colors[color_index % len(colors)]
      color_index += 1

    for _, row in data.iterrows():
      if pd.isna(row['position']['lat']) or pd.isna(row['position']['long']):
        continue

      location = {}
      location['device'] = device
      location['time'] = row['time'].strftime('%Y-%m-%d %H:%M:%S %p')
      location['heart_rate'] = row['heart_rate']
      position = {
          'lat': row['position']['lat'],
          'lng': row['position']['long']
      }
      location['alt_meters'] = row['alt_meters']
      distance = None
      if row['calc_distance_meters'] is not None:
        distance = round(float(row['calc_distance_meters']) / 1000 * ratio, 2)
      location['position'] = position
      location['distance'] = format(distance * ratio, '.4f')
      location['distance_label'] = distance_label
      location['speed'] = format(row['speed_kmh'] * ratio, '.2f')
      location['speed_label'] = speed_label
      locations.append(location)

  device_colors_json = json.dumps(device_colors)
  locations_json = json.dumps(locations)

  # Insert the device colors and locations into the HTML content
  html_content = html_content.format(
      sport=sport,
      zoom_level=zoom_level,
      center_lat=center_lat,
      center_long=center_long,
      map_url=map_url,
      device_colors_json=device_colors_json,
      locations_json=locations_json
  )

  return html_content
