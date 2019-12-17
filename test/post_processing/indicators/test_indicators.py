from multiply_post_processing.indicators import get_indicator, get_indicators

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


def test_get_indicator_geocbi():
    geocbi_variable = get_indicator('GeoCBI')

    assert 'GeoCBI' == geocbi_variable.short_name
    assert 'Geometrically Structured Composite Burned Index' == geocbi_variable.display_name
    assert geocbi_variable.unit is None
    assert '0 (unburned) - 3 (completely burned)' == geocbi_variable.range


def test_get_indicator_mnnd():
    mmd_variable = get_indicator('mnnd')

    assert 'mnnd' == mmd_variable.short_name
    assert 'Mean Nearest Neighbor Distance' == mmd_variable.display_name
    assert 'Spread of Trait Distribution, Niche Space Differentiation ' == mmd_variable.description
    assert 'Depends on number of considered traits' == mmd_variable.range
    assert 1 == len(mmd_variable.applications)
    assert 'functional diversity' == mmd_variable.applications[0]
