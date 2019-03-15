import click

from multiply_post_processing.version import __version__
from multiply_post_processing import get_available_indicators, get_post_processor_description, get_post_processor_names, \
    run_post_processor, run_post_processing
from typing import List

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


# noinspection PyShadowingBuiltins
@click.command(name="run_processor")
@click.argument('post_processor', metavar='<post_processor>')
@click.argument('input_path', metavar='<input_path>')
@click.option('--output_path', '-o', metavar='<output_path>', help="Where to write the output files. "
                                                                   "If not given, the output is written to the"
                                                                   "directory given by input_path.")
@click.option('--roi', '-r', metavar='<roi>', help="The region of interest on which the post processor shall be run. "
                                                   "Must be given as geometry in WKT.")
@click.option('--spatial_resolution', '-sr', metavar='<spatial_resolution>', help="The spatial resolution the output "
                                                                                  "shall have. To be provided in m.")
@click.option("-rg", "--roi_grid", metavar='<roi_grid>',
              help="A representation of the spatial reference system in which the roi is given, either as EPSG-code "
                   "or as WKT representation. If not given, it is assumed that the roi is given in the "
                   "destination spatial reference system. If that is not given neither, it will be assumed the "
                   "coordinates are given in WGS84.")
@click.option("-dg", "--destination_grid", metavar='<destination_grid>',
              help="A representation of the spatial reference system in which the output shall be given, either as "
                   "EPSG-code or as WKT representation. If not given, it is tried to derive this from <roi_grid>.")
def run_processor(post_processor: str, input_path: str, output_path: str = None, roi: str = None,
                  spatial_resolution: str = None, roi_grid: str = None, destination_grid: str = None):
    """
    Runs post processor <post_processor> on data located at <input_path>.
    """
    if output_path is None:
        output_path = input_path
    spatial_resolution = int(spatial_resolution)
    run_post_processor(post_processor, input_path, output_path, roi, spatial_resolution, roi_grid, destination_grid)


# noinspection PyShadowingBuiltins
@click.command(name="process_indicators")
@click.argument('indicator_names', metavar='<indicator_names>')
@click.argument('input_path', metavar='<input_path>')
@click.option('--output_path', '-o', metavar='<output_path>', help="Where to write the output files. "
                                                                   "If not given, the output is written to the"
                                                                   "directory given by input_path.")
@click.option('--roi', '-r', metavar='<roi>', help="The region of interest on which the post processor shall be run. "
                                                   "Must be given as geometry in WKT.")
@click.option('--spatial_resolution', '-sr', metavar='<spatial_resolution>', help="The spatial resolution the output "
                                                                                  "shall have. To be provided in m.")
@click.option("-rg", "--roi_grid", metavar='<roi_grid>',
              help="A representation of the spatial reference system in which the roi is given, either as EPSG-code "
                   "or as WKT representation. If not given, it is assumed that the roi is given in the "
                   "destination spatial reference system. If that is not given neither, it will be assumed the "
                   "coordinates are given in WGS84.")
@click.option("-dg", "--destination_grid", metavar='<destination_grid>',
              help="A representation of the spatial reference system in which the output shall be given, either as "
                   "EPSG-code or as WKT representation. If not given, it is tried to derive this from <roi_grid>.")
def process_indicators(indicator_names: List[str], input_path: str, output_path: str = None, roi: str = None,
                       spatial_resolution: int = None, roi_grid: str = None, destination_grid: str = None):
    """
    Retrieves indicators <indicator_names> on data located at <input_path>.
    """
    print(type(indicators))
    if output_path is None:
        output_path = input_path
    spatial_resolution = int(spatial_resolution)
    run_post_processing(indicator_names, input_path, output_path, roi, spatial_resolution, roi_grid, destination_grid)


# noinspection PyShadowingBuiltins
@click.command(name="processors")
def processors():
    """
    Lists the names of provided post processors.
    """
    post_processor_names = get_post_processor_names()
    print(post_processor_names)


# noinspection PyShadowingBuiltins
@click.command(name="describe")
@click.argument('post_processor', metavar='<post_processor>')
def describe(post_processor: str):
    """
    Describes a post processor.
    """
    post_processor_description = get_post_processor_description(post_processor)
    print(post_processor_description)


# noinspection PyShadowingBuiltins
@click.command(name="indicators")
def indicators():
    """
    Lists the provided indicators.
    """
    available_indicators = get_available_indicators()
    print(available_indicators)



# noinspection PyShadowingBuiltins
@click.group()
@click.version_option(__version__)
def cli():
    """
    MULTIPLY Post-Processing
    """


cli.add_command(run_processor)
cli.add_command(process_indicators)
cli.add_command(processors)
cli.add_command(describe)
cli.add_command(indicators)


def main(args=None):
    cli.main(args=args)


if __name__ == '__main__':
    main()
