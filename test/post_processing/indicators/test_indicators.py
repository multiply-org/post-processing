from multiply_core.variables import get_registered_variable
from multiply_post_processing.indicators import get_indicators

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


def test_get_indicators():
    indicators = get_indicators()

    assert 5 == len(indicators)
    assert 'GeoCBI' == indicators[0]['Variable']['short_name']
    assert 'Geometrically Structured Composite Burned Index' == indicators[0]['Variable']['display_name']
    assert indicators[0]['Variable']['unit'] is None
    assert '0 (unburned) - 3 (completely burned)' == indicators[0]['Variable']['range']
    assert 2 == len(indicators[0]['Variable']['applications'])
    assert 'Burned Area Discrimination' in indicators[0]['Variable']['applications']
    assert 'Fire Severity Estimation' in indicators[0]['Variable']['applications']


def test_indicators_are_in_variables():
    geocbi_variable = get_registered_variable('GeoCBI')

    assert 'GeoCBI' == geocbi_variable.short_name
    assert 'Geometrically Structured Composite Burned Index' == geocbi_variable.display_name
    assert geocbi_variable.unit is None
    assert '0 (unburned) - 3 (completely burned)' == geocbi_variable.range
