from multiply_post_processing.burned_severity_post_processor import BurnedSeverityPostProcessor


__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


def test_get_num_time_steps():
    assert 2 == BurnedSeverityPostProcessor.get_num_time_steps()
