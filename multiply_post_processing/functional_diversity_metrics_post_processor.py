import logging
from abc import ABCMeta, abstractmethod

from multiply_post_processing import PostProcessorCreator, PostProcessor, VariablePostProcessor, PostProcessorType
from multiply_post_processing.indicators import get_indicator
from multiply_core.variables import Variable
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy import stats
from scipy import spatial
from scipy.spatial.distance import squareform, pdist
from sklearn.neighbors import NearestNeighbors
import sklearn.preprocessing as sk
from typing import List

__author__ = "L.T.Hauser (University Leiden, NL), Tonio Fincke (Brockmann Consult GmbH)"

logging.getLogger().setLevel(logging.INFO)

__NAME__ = 'FunctionalDiversityMetrics'
__DESCRIPTION__ = 'This post Processor calculates Functional Diversity from multiple plant trait variables. ' \
                  'Functional Diversity metrics are calculated over plots of adjecent pixels considering the ' \
                  'N-dimensional combination of traits found in these pixels.'
_CVH_NAME = 'cvh'
_MNND_NAME = 'mnnd'
_FE_NAME = 'fe'
_F_DIV_NAME = 'fdiv'
_INDICATOR_DESCRIPTIONS = [get_indicator(_CVH_NAME), get_indicator(_MNND_NAME),
                           get_indicator(_FE_NAME), get_indicator(_F_DIV_NAME)]
_NO_DATA_VALUE = np.NaN
_VALID_THRESHOLD = 95


def _pre_process(variables:  dict) -> dict:
    preprocessed = {}
    for variable in variables:
        preprocessed[variable] = _pre_process_trait(variables[variable])
    return preprocessed


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


def _process(variable_data: dict, indicator_names: List[str]) -> dict:
    x_size = 10
    y_size = 10
    x_offset = 5
    y_offset = 5
    first_var_name = list(variable_data.keys())[0]
    first_var = variable_data[first_var_name]
    num_vars = 3
    rows = first_var.shape[0]
    columns = first_var.shape[1]

    functions = _get_functions(indicator_names, rows, columns, x_offset, y_offset)

    for row in np.arange(x_offset, rows, x_size):
        for column in np.arange(y_offset, columns, y_size):

            # read data in moving window
            r_first_var = first_var[(row - x_offset):(row + x_offset), (column - y_offset):(column + y_offset)]

            num_valid = np.sum(np.isfinite(r_first_var))
            if num_valid < _VALID_THRESHOLD:
                logging.warning('Not enough valid pixels found for {}: {} < {}. Will not derive metrics for part of '
                                'image'.format(first_var_name, num_valid, _VALID_THRESHOLD))
                continue
            concatenate_list = []
            for variable in variable_data:
                r_var = variable_data[variable][(row - x_offset):(row + x_offset), (column - y_offset):(column + y_offset)]
                concatenate_list.append(np.concatenate(r_var))
            # arrange data#
            traitslist = np.array(concatenate_list)
            # EXCLUDE MISSING VALUES / NaN FROM ANALYSIS ##
            est = traitslist[~np.isnan(traitslist)]
            lengthr = int(len(est) / num_vars)
            est = np.reshape(est, (num_vars, lengthr))
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

    def process_variables(self, variable_data: dict) -> dict:
        if len(self.indicators) == 0:
            logging.info('No indicator selected. Will not compute.')
            return {}
        pre_processed_variable_data = _pre_process(variable_data)
        return _process(pre_processed_variable_data, self.indicators)

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
    def get_type(cls) -> PostProcessorType:
        return PostProcessorType.VARIABLE_POST_PROCESSOR

    @classmethod
    def get_required_input_data_types(cls) -> List[str]:
        return []

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
