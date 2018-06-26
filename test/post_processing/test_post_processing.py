from typing import List

import numpy as np

import multiply_post_processing
from multiply_post_processing import IndicatorDescription, VariablePostProcessor

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


def test_add_post_processor():
    dummy_post_processor = DummyPostProcessor()
    multiply_post_processing.add_post_processor(dummy_post_processor)
    post_processor_names = multiply_post_processing.get_post_processor_names()
    assert 1, len(post_processor_names)
    assert "dummy", post_processor_names[0]


class DummyPostProcessor(VariablePostProcessor):

    @classmethod
    def get_name(cls) -> str:
        return "dummy"

    @classmethod
    def get_description(cls) -> str:
        return "A post processor for testing"

    @classmethod
    def get_names_of_required_variables(cls) -> List[str]:
        return ['just_pass_in_anything']

    @classmethod
    def get_names_of_required_masks(cls) -> List[str]:
        return []

    @classmethod
    def get_indicator_descriptions(cls) -> List[IndicatorDescription]:
        return [IndicatorDescription("dummy descriptor", "seriously, it's just a dummy")]

    def process_variables(self, variable_data: List[np.array], masks: List[np.array]) -> List[np.array]:
        return variable_data * 2

    def initialize(self):
        pass
