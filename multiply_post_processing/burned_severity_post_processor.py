from abc import ABCMeta
import logging
from typing import List, Optional

import numpy as np

from multiply_core.observations import ObservationsWrapper, DataTypeConstants, SENTINEL_2_MODEL_DATA_TYPE
from multiply_core.variables import Variable
from multiply_post_processing import EODataPostProcessor, PostProcessorCreator, PostProcessor, PostProcessorType
from multiply_post_processing.indicators import get_indicator

__author__ = 'Tonio Fincke (Brockmann Consult GmbH), Gonzalo Otón & Magí Franquesa (Universidad de Alcalá)'

__NAME__ = 'BurnedSeverity'
__DESCRIPTION__ = 'This post processor creates a burned area mask and ' \
                  'as a second step it determines its severity using RBR.'

_SENTINEL_2_DICT = {'no_data': -9999,'scale_factor': 0.0001, 'version': '_3', 'nir': 'B8A_sur.tif',
                    'smir': 'B11_sur.tif', 'swir': 'B12_sur.tif'}
_LANDSAT_7_DICT = {'scale_factor': 0.0001, 'version': '_1'}
_LANDSAT_8_DICT = {'scale_factor': 0.0001, 'version': '_1'}
_DATA_DICTS = {DataTypeConstants.AWS_S2_L2: _SENTINEL_2_DICT, DataTypeConstants.S2_L2: _SENTINEL_2_DICT}
_INDICATOR_NAMES = ['GeoCBI']
_INDICATOR_DESCRIPTIONS = [get_indicator('GeoCBI')]

logging.getLogger().setLevel(logging.INFO)


def calc_nbr(swir, nir, comp_mask, no_data, scale_factor):
    logging.info('Calculating: NBR')

    swir = np.where((swir == no_data), -1, swir)
    nir = np.where((nir == no_data), -1, nir)

    nir = nir * scale_factor
    swir = swir * scale_factor

    mask = np.where(((nir + swir) == 0), False, True)
    nir *= mask
    swir = swir * mask + 0.2 * np.invert(mask)  # The factor (0.2) doesn't affect, is for Nodata values

    nbr = (nir - swir) / (nir + swir)

    comp_mask *= mask
    nbr = nbr * comp_mask + no_data * np.invert(comp_mask)

    nbr = nbr.astype(np.float32)
    # Name=str(Year)+str(Month)+str(Day)+'_'+Band+'.tif'
    # saveTIFnew(SD,nbr,path,Name,gridColumnTot,gridLineTot,DataType,NoData)
    return nbr


def calc_mirbi(smir, swir, mask, no_data, scale_factor):
    logging.info('Calculating: MIRBI')

    swir = np.where((swir == no_data), -1, swir)
    smir = np.where((smir == no_data), -1, smir)

    smir = smir * scale_factor
    swir = swir * scale_factor

    mirbi = 10 * swir - 9.8 * smir + 2
    mirbi = mirbi * mask + no_data * np.invert(mask)

    mirbi = mirbi.astype(np.float32)
    # Name=str(Year)+str(Month)+str(Day)+'_'+Band+'.tif'
    # saveTIFnew(SD,MIRBI,path,Name,gridColumnTot,gridLineTot,DataType,NoData)
    return mirbi


def calc_nbr2(smir, swir, Mask, no_data: float, scale_factor: float):
    logging.info('Calculating: NBR2')

    swir = np.where((swir == no_data), -1, swir)
    smir = np.where((smir == no_data), -1, smir)

    smir = smir * scale_factor
    swir = swir * scale_factor

    mask2 = np.where(((smir + swir) == 0), False, True)
    smir *= mask2
    swir = swir * mask2 + 0.2 * np.invert(mask2)  # The factor (0.2) doesn't affect, is for Nodata values

    NBR2 = (smir - swir) / (smir + swir)

    Mask *= mask2
    NBR2 = NBR2 * Mask + no_data * np.invert(Mask)

    NBR2 = NBR2.astype(np.float32)
    # Name=str(Year)+str(Month)+str(Day)+'_'+Band+'.tif'
    # saveTIFnew(SD,NBR2,path,Name,gridColumnTot,gridLineTot,DataType,NoData)
    return NBR2


def mask_values(array, NoData):
    if np.max(array) == NoData:
        return NoData
    y = np.ma.masked_values(array, NoData)
    mean = y.mean()

    print(mean)
    return mean


class BurnedSeverityPostProcessor(EODataPostProcessor):

    @classmethod
    def get_num_time_steps(cls) -> int:
        return 2

    @classmethod
    def get_names_of_supported_eo_data_types(cls) -> List[str]:
        return [SENTINEL_2_MODEL_DATA_TYPE, DataTypeConstants.AWS_S2_L2, DataTypeConstants.S2_L2]

    @classmethod
    def get_names_of_required_bands(cls, data_type: str) -> List[str]:
        data_dict = cls._get_data_dict(data_type)
        if data_dict is None:
            return []
        return [data_dict['nir'], data_dict['smir'], data_dict['swir']]

    @staticmethod
    def _get_data_dict(data_type: str) -> Optional[dict]:
        if data_type in _DATA_DICTS:
            return _DATA_DICTS[data_type]

    def process_observations(self, observations: ObservationsWrapper) -> dict:
        # If we do not have exactly two observations of the same data type wrapped we'll exit.
        if len(observations.dates) != 2:
            logging.info("Not exactly two observations provided. Exiting.")
            return [np.array([], dtype=np.float64)]
        data_type = observations.get_data_type(observations.dates[0])
        other_data_type = observations.get_data_type(observations.dates[1])
        if data_type != other_data_type:
            logging.warning('Found types of different data. Cannot determine burned severity. Exiting.')
            return [np.array([], dtype=np.float64)]
        data_dict = self._get_data_dict(data_type)
        no_data = data_dict['no_data']
        scale_factor = data_dict['scale_factor']
        observations.set_no_data_value(observations.dates[0], data_dict['smir'], no_data * scale_factor)
        observations.set_no_data_value(observations.dates[0], data_dict['swir'], no_data * scale_factor)
        observations.set_no_data_value(observations.dates[1], data_dict['smir'], no_data * scale_factor)
        observations.set_no_data_value(observations.dates[1], data_dict['swir'], no_data * scale_factor)
        smir_0 = observations.get_band_data_by_name(observations.dates[0], data_dict['smir'], False).observations
        swir_0 = observations.get_band_data_by_name(observations.dates[0], data_dict['swir'], False).observations
        smir_1 = observations.get_band_data_by_name(observations.dates[1], data_dict['smir'], False).observations
        swir_1 = observations.get_band_data_by_name(observations.dates[1], data_dict['swir'], False).observations
        smir_0 /= scale_factor
        smir_1 /= scale_factor
        swir_0 /= scale_factor
        swir_1 /= scale_factor
        smir_0 = smir_0.astype(np.int)
        smir_1 = smir_1.astype(np.int)
        swir_0 = swir_0.astype(np.int)
        swir_1 = swir_1.astype(np.int)
        logging.info('Calculating SWIR/SMIR Mask')
        swir_mask = (swir_1 != no_data) * (swir_0 != no_data)
        smir_mask = (smir_1 != no_data) * (smir_0 != no_data)
        s_mask = swir_mask * smir_mask
        logging.info('Calculating MIRBI')
        mirbi_1 = calc_mirbi(smir_1, swir_1, s_mask, no_data, scale_factor)
        mean_mirbi_1 = mask_values(mirbi_1, no_data)
        mirbi_0 = calc_mirbi(smir_0, swir_0, s_mask, no_data, scale_factor)
        logging.info('Calculating difMIRBI')
        diff_mirbi = mirbi_1 - mirbi_0
        diff_mirbi *= s_mask + no_data * np.invert(s_mask)
        logging.info('Calculating NBR2')
        nbr2_1 = calc_nbr2(smir_1, swir_1, s_mask, no_data, scale_factor)
        mean_nbr2_1 = mask_values(nbr2_1, no_data)
        nbr2_0 = calc_nbr2(smir_0, swir_0, s_mask, no_data, scale_factor)
        logging.info('Calculating difNBR2')
        diff_nbr2 = nbr2_1 - nbr2_0
        diff_nbr2 = diff_nbr2 * s_mask + no_data * np.invert(s_mask)
        observations.set_no_data_value(observations.dates[0], data_dict['nir'], no_data * scale_factor)
        observations.set_no_data_value(observations.dates[1], data_dict['nir'], no_data * scale_factor)
        nir_0 = observations.get_band_data_by_name(observations.dates[0], data_dict['nir'], False).observations
        nir_1 = observations.get_band_data_by_name(observations.dates[1], data_dict['nir'], False).observations
        nir_0 /= scale_factor
        nir_1 /= scale_factor
        nir_0 = nir_0.astype(np.int)
        nir_1 = nir_1.astype(np.int)
        logging.info('Calculating NIR Mask')
        nir_mask = (nir_1 != no_data) * (nir_0 != no_data)
        logging.info('Calculating NIR')
        mean_nir_1 = mask_values(nir_1, no_data)
        logging.info('Calculating difNIR')
        diff_nir = nir_1 - nir_0
        diff_nir = diff_nir * nir_mask + no_data * np.invert(nir_mask)

        logging.info('Calculating Burned Mask')
        mean_mirbi_mask = mirbi_1 > mean_mirbi_1
        diff_mirbi_mask = diff_mirbi > 0.25
        mean_nbr2_1_mask = nbr2_1 < mean_nbr2_1
        diff_nbr2_mask = diff_nbr2 < -0.05
        mean_nir_1_mask = nir_1 < mean_nir_1
        diff_nir_mask = diff_nir < -0.01
        burned_mask = s_mask * nir_mask * mean_mirbi_mask * diff_mirbi_mask * mean_nbr2_1_mask * diff_nbr2_mask * \
                      mean_nir_1_mask * diff_nir_mask
        logging.info('Calculating NBR')
        nbr_1 = calc_nbr(swir_1, nir_1, burned_mask, no_data, scale_factor)
        nbr_0 = calc_nbr(swir_0, nir_0, burned_mask, no_data, scale_factor)
        logging.info('Calculating difNBR')
        diff_nbr = (nbr_0 - nbr_1) * burned_mask + no_data * np.invert(burned_mask)
        logging.info('Calculating RBR')
        rbr = diff_nbr / (nbr_0 + 1.001)
        rbr = rbr * burned_mask + no_data * np.invert(burned_mask)
        geo_cbi = rbr
        geo_cbi[geo_cbi != no_data] *= 2.80278
        geo_cbi[geo_cbi != no_data] += 1.07541
        geo_cbi[geo_cbi > 3.0] = 3.0
        results = {'geocbi': geo_cbi}
        return results

    @classmethod
    def get_name(cls) -> str:
        return __NAME__

    @classmethod
    def get_description(cls) -> str:
        return __DESCRIPTION__

    @classmethod
    def get_indicator_descriptions(cls) -> List[Variable]:
        return _INDICATOR_DESCRIPTIONS


class BurnedSeverityPostProcessorCreator(PostProcessorCreator):

    @classmethod
    def get_type(cls) -> PostProcessorType:
        return PostProcessorType.EO_DATA_POST_PROCESSOR

    @classmethod
    def get_required_input_data_types(cls) -> List[str]:
        return [SENTINEL_2_MODEL_DATA_TYPE]

    @classmethod
    def get_name(cls) -> str:
        return __NAME__

    @classmethod
    def get_description(cls) -> str:
        return __DESCRIPTION__

    @classmethod
    def get_indicator_descriptions(cls) -> List[Variable]:
        return _INDICATOR_DESCRIPTIONS

    @classmethod
    def create_post_processor(cls, indicator_names: List[str]) -> PostProcessor:
        return BurnedSeverityPostProcessor(indicator_names)
