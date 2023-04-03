# tcxplot

`tcxplot` is a Python command-line tool for processing TCX and GPX files and generating visualizations of the data. The tool uses Google Maps API to generate a map of the route and plots graphs of heart rate, distance and speed.

## Installation

1. Clone this repository: `git clone https://github.com/yourusername/tcxplot.git`
2. Navigate to the project directory: `cd tcxplot`
3. Create a virtual environment: `python3 -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`

## Usage

`tcxplot` can be run from the command line with the following arguments:

python tcxplot.py <data_folder> --output_dir=<output_dir> --key=<google_maps_api_key> [--gt=<ground_truth_device>] [--ref=<reference_device>] [--no-launch_browser] [--units=<metric/imperial>]


* `data_folder`: the path to the folder containing TCX/GPX files to be processed.
* `output_dir`: the path to the directory where output files will be saved.
* `google_maps_api_key`: your Google Maps API key.
* `ground_truth_device` (optional): the ground truth device for heart rate (default: Polar).
* `reference_device` (optional): the reference device for heart rate (default: Apple).
* `no_browser` (optional): disables the launch the webview on the resulting HTML file
* `units` (optional): specifies the units of measure, options are metric or imperial (default: imperial).

## Examples

Generate output files for all TCX files in the `data` directory, with the resulting files saved in the `results` directory:


* `data_folder`: the path to the folder containing TCX/GPX files to be processed.
* `output_dir`: the path to the directory where output files will be saved.
* `google_maps_api_key`: your Google Maps API key.
* `ground_truth_device` (optional): the ground truth device for heart rate (default: Polar).
* `reference_device` (optional): the reference device for heart rate (default: Apple).
* `launch_browser` (optional): automatically launch the webview on the resulting HTML file (default).
* `no_browser` (optional): Do not launch the webview on the resulting html file.
* `units` (optional): specifies the units of measure, options are metric or imperial (default: metric).

## Examples

Generate output files for all TCX files in the `data` directory, with the resulting files saved in the `results` directory:

python tcxplot.py data --output_dir=results --key=YOUR_API_KEY


Generate output files for all GPX files in the `data` directory, with the resulting files saved in the `results` directory, and launch the webview automatically:



Generate output files for all GPX files in the `data` directory, with the resulting files saved in the `results` directory, and launch the webview automatically:

python tcxplot.py data --output_dir=results --key=YOUR_API_KEY --launch_browser


## License

`tcxplot` is licensed under the MIT License. See the `LICENSE` file for more information.

