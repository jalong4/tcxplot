"""Combine multiple HTML files into a single HTML file with tabs."""
import os


def combine_html(output_filename, html_files, tab_labels):
  """Combine multiple HTML files into a single HTML file with tabs.

  Args:
    output_filename (str): The output file path. If not specified, a temporary
      file will be used.
    html_files (list): A list of HTML file paths to combine.
    tab_labels (list): A list of labels for the tabs.

  Returns:
    str: The path of the combined HTML file.
  """

  template_filename = 'html/combined_template.html'
  template_path = os.path.join(os.path.dirname(__file__), template_filename)
  with open(template_path, 'r') as template_file:
    combined_html = template_file.read()

  # Create the tab header
  tab_header = ''
  for i, label in enumerate(tab_labels):
    if i == 0:
      tab_header += (
          '<button class="tablinks active" onclick="openTab(event,'
          f" 'tab{i}')\">{label}</button>\n"
      )
    else:
      tab_header += (
          '<button class="tablinks" onclick="openTab(event,'
          f" 'tab{i}')\">{label}</button>\n"
      )
  combined_html = combined_html.replace('{tab_header}', tab_header)

  # Create the tab content
  tab_content = ''
  for i, html_file in enumerate(html_files):
    with open(html_file, 'r') as infile:
      content = infile.read()
      if i == 0:
        tab_content += f'<div id="tab{i}" class="tabcontent active">\n'
      else:
        tab_content += f'<div id="tab{i}" class="tabcontent">\n'
      tab_content += content
      tab_content += '</div>\n'
  combined_html = combined_html.replace('{tab_content}', tab_content)

  with open(output_filename, 'w') as outfile:
    outfile.write(combined_html)

  return output_filename
