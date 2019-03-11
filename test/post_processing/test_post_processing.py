from typing import List, Optional

import numpy as np
import os
import shutil

from multiply_core.util import FileRef
from multiply_core.variables import Variable
import multiply_post_processing
from multiply_post_processing import PostProcessorCreator, VariablePostProcessor
from multiply_post_processing.post_processing import _group_file_refs_by_date, _get_valid_files, run_post_processing

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

ROI = 'POLYGON ((-2.1161534436028333 39.06796998380795, -2.0891905679389984 39.06776250050584, ' \
      '-2.089424595200457 39.049546053296766, -2.1163805451389095 39.049753402686, ' \
      '-2.1161534436028333 39.06796998380795))'
SPATIAL_RESOLUTION = 10
ROI_GRID = 'EPSG:4326'
DESTINATION_GRID = 'EPSG:32630'


def test_add_post_processor():
    dummy_post_processor_creator = DummyPostProcessorCreator()
    multiply_post_processing.add_post_processor_creator(dummy_post_processor_creator)
    post_processor_names = multiply_post_processing.get_post_processor_names()
    assert 1, len(post_processor_names)
    assert "dummy", post_processor_names[0]


def test_group_file_refs_by_date():
    file_refs = [FileRef('1', '1999-01-01', '1999-01-01', 'image/tiff'),
                 FileRef('2', '1999-01-01', '1999-01-01', 'image/tiff'),
                 FileRef('3', '1999-01-01', '1999-01-01', 'image/tiff'),
                 FileRef('4', '1999-01-02', '1999-01-02', 'image/tiff'),
                 FileRef('5', '1999-01-03', '1999-01-03', 'image/tiff'),
                 FileRef('6', '1999-01-03', '1999-01-03', 'image/tiff'),
                 ]
    file_refs_by_date = _group_file_refs_by_date(file_refs)

    assert file_refs_by_date is not None
    assert 3 == len(file_refs_by_date)
    assert '1999-01-01' in file_refs_by_date
    assert '1999-01-02' in file_refs_by_date
    assert '1999-01-03' in file_refs_by_date
    assert 3 == len(file_refs_by_date['1999-01-01'])
    assert 1 == len(file_refs_by_date['1999-01-02'])
    assert 2 == len(file_refs_by_date['1999-01-03'])


def test_get_valid_files():
    data_path = './test/test_data/'
    cab_files = _get_valid_files(data_path, ['cab'])
    expected_cab_file_paths = ['{}{}'.format(data_path, 'cab_A2017156.tif'),
                               '{}{}'.format(data_path, 'cab_A2017166.tif')]
    assert 2 == len(cab_files)
    assert cab_files[0].url in expected_cab_file_paths
    assert cab_files[1].url in expected_cab_file_paths

    valid_files = _get_valid_files(data_path, ['cw', 'lai', 'psoil'])
    expected_valid_file_paths = ['{}{}'.format(data_path, 'cw_A2017156.tif'),
                                 '{}{}'.format(data_path, 'cw_A2017166.tif'),
                                 '{}{}'.format(data_path, 'lai_A2017156.tif'),
                                 '{}{}'.format(data_path, 'lai_A2017166.tif'),
                                 '{}{}'.format(data_path, 'psoil_A2017156.tif'),
                                 '{}{}'.format(data_path, 'psoil_A2017166.tif')]
    assert 6 == len(valid_files)
    assert valid_files[0].url in expected_valid_file_paths
    assert valid_files[1].url in expected_valid_file_paths
    assert valid_files[2].url in expected_valid_file_paths
    assert valid_files[3].url in expected_valid_file_paths
    assert valid_files[4].url in expected_valid_file_paths
    assert valid_files[5].url in expected_valid_file_paths


_INDICATOR_DESCRIPTIONS = [Variable({'short_name': "indicator_1", 'display_name': "Indicator 1",
                                     'unit': None, 'description': "expected", 'range': None,
                                     'applications': None}),
                           Variable({'short_name': "indicator_2", 'display_name': "Indicator 2",
                                     'unit': None, 'description': "unexpected", 'range': None,
                                     'applications': None})]


def test_run_post_processing():
    output_path = './test/test_data/output/'
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    try:
        run_post_processing(['indicator_1'], data_path='./test/test_data/', output_path=output_path, roi=ROI,
                            spatial_resolution=SPATIAL_RESOLUTION, roi_grid=ROI_GRID, destination_grid=DESTINATION_GRID)
        assert os.path.exists(output_path)
        assert os.path.exists('{}{}'.format(output_path, 'indicator_1_2017-06-05.tif'))
        assert os.path.exists('{}{}'.format(output_path, 'indicator_1_2017-06-15.tif'))
    finally:
        if os.path.exists(output_path):
            shutil.rmtree(output_path)


class DummyPostProcessor(VariablePostProcessor):

    @classmethod
    def get_name(cls) -> str:
        return "dummy"

    @classmethod
    def get_description(cls) -> str:
        return "A post processor for testing"

    def get_names_of_required_variables(self) -> List[str]:
        required_variables = []
        if 'indicator_1' in self.indicators:
            required_variables.append('cdm')
            required_variables.append('psoil')
        if 'indicator_2' in self.indicators:
            required_variables.append('vzghtj')
        return required_variables

    @classmethod
    def get_names_of_required_masks(cls) -> List[str]:
        return []

    @classmethod
    def get_indicator_descriptions(cls) -> List[Variable]:
        return _INDICATOR_DESCRIPTIONS

    def process_variables(self, variable_data: dict, masks: Optional[np.array] = None) -> dict:
        result = {}
        if 'indicator_1' in self.indicators:
            result['indicator_1'] = variable_data['cdm'] + variable_data['psoil'] / 2
        if 'indicator_2' in self.indicators:
            result['indicator_2'] = variable_data['vzghtj']
        return result


class DummyPostProcessorCreator(PostProcessorCreator):

    def get_name(cls) -> str:
        return DummyPostProcessor.get_name()

    def get_description(cls) -> str:
        return DummyPostProcessor.get_description()

    @classmethod
    def get_indicator_descriptions(cls) -> List[Variable]:
        return _INDICATOR_DESCRIPTIONS

    def create_post_processor(cls, indicators: List[str]) -> DummyPostProcessor:
        return DummyPostProcessor(indicators)
