from multiply_core.variables import get_registered_variable
from multiply_post_processing.indicators import get_indicators

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


def test_get_indicators():
    indicators = get_indicators()

    assert 5 == len(indicators)
    assert 'geocbi' == indicators[0]['Variable']['short_name']
    assert 'Geo CBI' == indicators[0]['Variable']['display_name']
    assert indicators[0]['Variable']['unit'] is None
    assert '0-3' == indicators[0]['Variable']['range']
    assert 1 == len(indicators[0]['Variable']['applications'])
    assert 'fire severity' in indicators[0]['Variable']['applications']


def test_indicators_are_in_variables():
    geocbi_variable = get_registered_variable('geocbi')

    assert 'geocbi' == geocbi_variable.short_name
    assert 'Geo CBI' == geocbi_variable.display_name
    assert geocbi_variable.unit is None
    assert '0-3' == geocbi_variable.range
