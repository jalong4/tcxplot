"""Parse a TCX or GPX file and return a Pandas DataFrame."""

import os

from utils import parser_gpx
from utils import parser_tcx


def parse_file(file_path):
  """Parse a TCX or GPX file and return a Pandas DataFrame.

  Args:
    file_path: The file path of the TCS or GPX file

  Returns:
    a Pandas DataFrame
  """

  file_type = os.path.splitext(file_path.lower())[1]
  return (
      parser_tcx.parse_tcx_file(file_path)
      if file_type == '.tcx'
      else parser_gpx.parse_gpx_file(file_path)
  )
