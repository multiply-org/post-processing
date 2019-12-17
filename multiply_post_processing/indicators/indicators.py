import pkg_resources
import yaml

from multiply_core.variables import Variable

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


def get_indicators():
    return yaml.safe_load(pkg_resources.resource_stream(__name__, 'indicators_library.yaml'))


def get_indicator(indicator_name: str) -> Variable:
    indicators = get_indicators()
    for indicator in indicators:
        if indicator['Variable']['short_name'] == indicator_name:
            return Variable(indicator['Variable'])
    return None
