import logging
import numpy as np

from abc import abstractmethod, ABCMeta
from enum import Enum
from typing import List, Optional

from multiply_core.observations import ObservationsWrapper

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

logging.getLogger().setLevel(logging.INFO)


class IndicatorDescription:
    """
    A description of the indicator derived from post processing.
    """

    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description

    @property
    def name(self):
        """The name of the indicator"""
        return self._name

    @property
    def description(self):
        """A description of the indicator"""
        return self._description


class PostProcessorType(Enum):
    VARIABLE_POST_PROCESSOR = 0
    EO_DATA_POST_PROCESSOR = 1


class PostProcessor(metaclass=ABCMeta):
    """
    This is the base class for all MULTIPLY Post Processors. Each Post Processor must implement the functions defined
    herein. Post Processor Realizations should not implement this interface directly but either VariablePostProcessor or
    EODataPostprocessor.
    """

    def __init__(self, indicators: List[str]):
        indicator_descriptions = self.get_indicator_descriptions()
        self.indicators = []
        for indicator in indicators:
            for indicator_description in indicator_descriptions:
                if indicator_description == indicator_description:
                    self.indicators.append(indicator)
                    break
            logging.info('Indicator {} is not provided by post processor {}.'.format(indicator, self.get_name()))


    @abstractmethod
    def get_actual_indicators(self) -> IndicatorDescription:
        """
        :return: The descriptions of the indicators that are actually computed by this post processor.
        """


    @classmethod
    @abstractmethod
    def get_type(cls) -> PostProcessorType:
        """
        :return: The Type of PostProcessor.
        """

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """
        :return: the name of the post processor in a representational form.
        """

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """
        :return: A short description of the post processor.
        """

    @classmethod
    @abstractmethod
    def get_indicator_descriptions(cls) -> List[IndicatorDescription]:
        """
        :return: A list with the descriptions of the indicators this post processor creates.
        """


class VariablePostProcessor(PostProcessor):
    """A base class for Post Processors that operate on bio-physical variables."""

    @classmethod
    def get_type(cls) -> PostProcessorType:
        return PostProcessorType.VARIABLE_POST_PROCESSOR

    @classmethod
    @abstractmethod
    def get_names_of_required_variables(cls) -> List[str]:
        """
        :return: The list of biophysical parameters required by this post processor to work. Input data is expected to
        be passed in the order given by this list.
        """

    @classmethod
    @abstractmethod
    def get_names_of_required_masks(cls) -> List[str]:
        """
        :return: The list of masks required by this post processor to work. Input data is expected to be passed in the
        order given by this list.
        """

    @abstractmethod
    def process_variables(self, variable_data: dict, masks: Optional[np.array] = None) -> dict:
        """
        Performs the post processing
        :param variable_data: The input data required to perform the post processing
        :param masks: Mask data used to mask out array cells during post-processing.
        :return: The result of the post processing
        """


class EODataPostProcessor(PostProcessor):
    """A base class for post processors that work on measurements from EO Data."""

    @classmethod
    def get_type(cls) -> PostProcessorType:
        return PostProcessorType.EO_DATA_POST_PROCESSOR

    @classmethod
    @abstractmethod
    def get_names_of_supported_eo_data_types(cls) -> List[str]:
        """
        :return: The list of EO Data Types supported by this post processor.
        """

    @classmethod
    @abstractmethod
    def get_names_of_required_bands(cls, data_type: str) -> List[str]:
        """
        :return: The list of names of the bands required by this post processor, given per data type. Input data is
        expected to be passed in the order given by this list.+ get_names_
        """

    @classmethod
    @abstractmethod
    def get_names_of_required_masks(cls) -> List[str]:
        """
        :return: The list of masks required by this post processor to work. Input data is expected to be passed in the
        order given by this list.
        """

    @abstractmethod
    def process_eo_data(self, eo_data: List[np.array], masks: List[np.array]) -> List[np.array]:
        """
        Performs the post processing
        :param eo_data: The input data required to perform the post processing
        :param masks: Mask data used to mask out array cells during post-processing.
        :return: The result of the post processing
        """

    @abstractmethod
    def process_observations(self, observations: ObservationsWrapper, masks: Optional[List[np.array]] = None) \
            -> dict:
        """
        Performs the post processing
        :param observations: A Wrapper around earth observation data. Provides a convenience method to access EO Data.
        :param masks: Mask data used to mask out array cells during post-processing.
        :return: The result of the post processing
        """


class PostProcessorCreator(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """
        :return: the name of the postprocessor associated with this creator.
        """

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """
        :return: the description of the postprocessor associated with this creator.
        """

    @classmethod
    @abstractmethod
    def get_indicator_descriptions(cls) -> List[IndicatorDescription]:
        """
        :return: A list with the descriptions of the indicators this post processor creates.
        """

    @classmethod
    @abstractmethod
    def create_post_processor(cls, indicators: List[str]) -> PostProcessor:
        """
        :param indicators: The indicators that shall be derived using this post processor.
        :return: An instance of the post processor associated with this creator.
        """
