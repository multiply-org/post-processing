import logging
from abc import ABCMeta, abstractmethod

from multiply_post_processing import PostProcessorCreator, PostProcessor, VariablePostProcessor
from multiply_core.variables import get_registered_variable, Variable
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy import stats
from scipy import spatial
from scipy.spatial.distance import squareform, pdist
from sklearn.neighbors import NearestNeighbors
import sklearn.preprocessing as sk
from typing import List, Optional, Tuple

__author__ = "L.T.Hauser (University Leiden, NL), Tonio Fincke (Brockmann Consult GmbH)"

logging.getLogger().setLevel(logging.INFO)

__NAME__ = 'FunctionalDiversityMetrics'
__DESCRIPTION__ = ''

_LAI_NAME = 'lai'
_CW_NAME = 'cw'
_CAB_NAME = 'cab'
__NAMES_OF_REQUIRED_VARIABLES__ = [_LAI_NAME, _CW_NAME, _CAB_NAME]
_CVH_NAME = 'cvh'
_MNND_NAME = 'mnnd'
_FE_NAME = 'fe'
_F_DIV_NAME = 'fdiv'
_INDICATOR_DESCRIPTIONS = [get_registered_variable(_CVH_NAME), get_registered_variable(_MNND_NAME),
                           get_registered_variable(_FE_NAME), get_registered_variable(_F_DIV_NAME)]
_NO_DATA_VALUE = np.NaN
_VALID_THRESHOLD = 95


def _pre_process(lai: np.array, cab: np.array, cw: np.array) -> Tuple[np.array, np.array, np.array]:
    a_lai = _pre_process_trait(lai)
    a_cab = _pre_process_trait(cab)
    a_cw = _pre_process_trait(cw)
    return a_lai, a_cab, a_cw


def _pre_process_trait(trait: np.array) -> np.array:
    """
    Assign No-Data-Value and standardize
    """
    trait[trait == 0] = _NO_DATA_VALUE
    reshaped_trait = trait.reshape(-1, 1)
    scale_all = sk.StandardScaler()
    transformed_reshaped_trait = scale_all.fit_transform(reshaped_trait)
    return transformed_reshaped_trait.reshape(trait.shape)


class FunctionalDiversityMetricsFunction(metaclass=ABCMeta):

    def __init__(self, rows: int, cols: int, x_offset: int, y_offset: int):
        self._array = np.full((rows, cols), _NO_DATA_VALUE, dtype=np.float, order='C')
        self._x_offset = x_offset
        self._y_offset = y_offset

    def get_array(self):
        return self._array

    def set_value(self, row: int, column: int, value: np.float):
        self._array[(row - self._x_offset):(row + self._x_offset),
                    (column - self._y_offset):(column + self._y_offset)] = value

    @classmethod
    @abstractmethod
    def get_name(cls):
        pass

    def apply_function(self, traits: np.array, row: int, column: int):
        value = self._func(traits)
        self.set_value(row, column, value)

    @abstractmethod
    def _func(self, traits: np.array) -> np.float:
        """
        A function that computes a functional diversity metric based on the incoming trait
        :param traits: Traits in the form of a n * 3 numpy array
        :return: A functional diversity metric
        """


class CVHFunction(FunctionalDiversityMetricsFunction):

    @classmethod
    def get_name(cls):
        return _CVH_NAME

    def _func(self, traits: np.array) -> np.float:
        try:
            return spatial.ConvexHull(traits).volume
        except:
            return _NO_DATA_VALUE


class MNNDFunction(FunctionalDiversityMetricsFunction):

    @classmethod
    def get_name(cls):
        return _MNND_NAME

    def _func(self, traits: np.array) -> np.float:
        scaler = sk.StandardScaler()
        scaler.fit(traits)
        nestd = scaler.transform(traits)
        nnbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(nestd)
        ndistances, nindices = nnbrs.kneighbors(nestd)
        return np.mean(ndistances[:, 1])


class FEFunction(FunctionalDiversityMetricsFunction):

    @classmethod
    def get_name(cls):
        return _FE_NAME

    def _func(self, traits: np.array) -> np.float:
        undgraph = squareform(pdist(traits, 'euclidean'))
        mintree = minimum_spanning_tree(undgraph)
        mstmat = mintree.toarray().astype(float)
        mstpasser = mstmat == 0
        mst = mstmat[~mstpasser]
        mst_shape = np.shape(mst)
        if np.shape(mst)[0] == 0:
            return _NO_DATA_VALUE
        ss = np.zeros(mst_shape)
        ss = (1 / (ss + len(mst)))
        PEW = (mst / np.sum(mst))
        return np.mean((np.sum(np.minimum(PEW, ss)) - ss[0]) / (1 - ss[0]))


class FDIVFunction(FunctionalDiversityMetricsFunction):

    @classmethod
    def get_name(cls):
        return _F_DIV_NAME

    def _func(self, traits: np.array) -> np.float:
        try:
            cvh = spatial.ConvexHull(traits)
            centroid = np.mean(traits[cvh.simplices, 0]), np.mean(traits[cvh.simplices, 1]), \
                       np.mean(traits[cvh.simplices, 2])
            eucdist = np.zeros(len(traits))
            for i in range(len(traits)):
                eucdist[i] = spatial.distance.euclidean(traits[i], centroid)
            return np.mean(eucdist)
        except:
            return _NO_DATA_VALUE


def _get_functions(indicator_names: List[str], rows: int, columns: int, x_offset: int, y_offset: int) -> \
        List[FunctionalDiversityMetricsFunction]:
    functions = []
    if _CVH_NAME in indicator_names:
        functions.append(CVHFunction(rows, columns, x_offset, y_offset))
    if _MNND_NAME in indicator_names:
        functions.append(MNNDFunction(rows, columns, x_offset, y_offset))
    if _FE_NAME in indicator_names:
        functions.append(FEFunction(rows, columns, x_offset, y_offset))
    if _F_DIV_NAME in indicator_names:
        functions.append(FDIVFunction(rows, columns, x_offset, y_offset))
    return functions


def _process(a_lai: np.array, a_cab: np.array, a_cw: np.array, indicator_names: List[str]) -> dict:
    x_size = 10
    y_size = 10
    x_offset = 5
    y_offset = 5
    rows = a_lai.shape[0]
    columns = a_lai.shape[1]

    functions = _get_functions(indicator_names, rows, columns, x_offset, y_offset)

    for row in np.arange(x_offset, rows, x_size):
        for column in np.arange(y_offset, columns, y_size):

            # read data in moving window
            r_lai = a_lai[(row - x_offset):(row + x_offset), (column - y_offset):(column + y_offset)]

            num_valid = np.sum(np.isfinite(r_lai))
            if num_valid < _VALID_THRESHOLD:
                logging.warning('Not enough valid pixels found for {}: {} < {}. Will not derive metrics for part of '
                                'image'.format(_LAI_NAME, num_valid, _VALID_THRESHOLD))
                continue
            r_cab = a_cab[(row - x_offset):(row + x_offset), (column - y_offset):(column + y_offset)]
            r_cw = a_cw[(row - x_offset):(row + x_offset), (column - y_offset):(column + y_offset)]
            # arrange data#
            traitslist = np.array([np.concatenate(r_cab), np.concatenate(r_cw), np.concatenate(r_lai)])
            # EXCLUDE MISSING VALUES / NaN FROM ANALYSIS ##
            est = traitslist[~np.isnan(traitslist)]
            lengthr = int(len(est) / 3)
            est = np.reshape(est, (3, lengthr))
            # kernel density estimates to define outliers
            try:
                kde = stats.gaussian_kde(est)
                density = kde(est)
                if np.sum(np.isfinite(density)) == 0:
                    estd = est.T
                else:
                    percentile = 5
                    num_non_outliers = 0
                    while num_non_outliers < _VALID_THRESHOLD / num_valid and percentile > -1:
                        noutliers = (density > np.percentile(density, percentile))
                        num_non_outliers = np.sum(noutliers)
                        percentile -= 1
                    # noinspection PyUnboundLocalVariable
                    estd = est.T[noutliers]
            except:  # if outlier detection failed
                estd = est.T
            for func in functions:
                func.apply_function(estd, row, column)

    logging.info("Finished derival of functional diversity metrics")

    output = {}
    for func in functions:
        output[func.get_name()] = func.get_array()

    return output


class FunctionalDiversityMetricsPostProcessor(VariablePostProcessor):

    @classmethod
    def get_num_time_steps(cls) -> int:
        return 1

    @classmethod
    def get_names_of_required_variables(cls) -> List[str]:
        return __NAMES_OF_REQUIRED_VARIABLES__

    @classmethod
    def get_names_of_required_masks(cls) -> List[str]:
        return []

    def process_variables(self, variable_data: dict, masks: Optional[np.array] = None) -> dict:
        if len(self.indicators) == 0:
            logging.info('No indicator selected. Will not compute.')
            return {}
        a_lai, a_cab, a_cw = _pre_process(variable_data[_LAI_NAME], variable_data[_CAB_NAME], variable_data[_CW_NAME])
        return _process(a_lai, a_cab, a_cw, self.indicators)

    @classmethod
    def get_name(cls) -> str:
        return __NAME__

    @classmethod
    def get_description(cls) -> str:
        return __DESCRIPTION__

    @classmethod
    def get_indicator_descriptions(cls) -> List[Variable]:
        return _INDICATOR_DESCRIPTIONS


class FunctionalDiversityMetricsPostProcessorCreator(PostProcessorCreator):

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
        return FunctionalDiversityMetricsPostProcessor(indicator_names)
