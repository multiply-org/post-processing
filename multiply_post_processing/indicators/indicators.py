import pkg_resources
import yaml

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


def get_indicators():
    return yaml.safe_load(pkg_resources.resource_stream(__name__, 'indicators_library.yaml'))
