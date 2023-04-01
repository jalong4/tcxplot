"""Enum class for unit of measure."""

import enum
from dateutil import tz


class UnitOfMeasure(enum.Enum):
  METRIC = 1
  IMPERIAL = 2

KM_TO_MILE_RATIO = 0.621371
M_TO_FT_RATIO = 3.28084


def to_local_time(time):
  # Set the timezone of the datetime object to UTC
  time_utc = time.replace(tzinfo=tz.tzutc())
  time_localized = time_utc.astimezone(tz.tzlocal())
  return time_localized


def to_local_time_string(time):
  return to_local_time(time).strftime('%Y-%m-%d %I:%M:%S %p')
