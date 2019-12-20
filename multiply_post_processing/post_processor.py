import logging

from abc import abstractmethod, ABCMeta
from enum import Enum
from typing import List

from multiply_core.observations import ObservationsWrapper
from multiply_core.variables import Variable

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

logging.getLogger().setLevel(logging.INFO)


class PostProcessorType(Enum):
    VARIABLE_POST_PROCESSOR = 0
    EO_DATA_POST_PROCESSOR = 1


class PostProcessor(metaclass=ABCMeta):
    """
    This is the base class for all MULTIPLY Post Processors. Each Post Processor must implement the functions defined
    herein. Post Processor Realizations should not implement this interface directly but either VariablePostProcessor or
    EODataPostprocessor.
    """

    def __init__(self, indicator_names: List[str]):
        indicator_descriptions = self.get_indicator_descriptions()
        self.indicators = []
        if len(indicator_names) > 0:
            for indicator in indicator_names:
                for indicator_description in indicator_descriptions:
                    if indicator == indicator_description.short_name:
                        self.indicators.append(indicator)
                        break
                if indicator not in self.indicators:
                    logging.info(f'Indicator {indicator} is not provided by post processor {self.get_name()}.')
        else:
            for indicator_description in indicator_descriptions:
                self.indicators.append(indicator_description.short_name)

    def get_actual_indicators(self) -> List[Variable]:
        """
        :return: The descriptions of the indicators that are actually computed by this post processor.
        """
        return self.indicators


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
    def get_indicator_descriptions(cls) -> List[Variable]:
        """
        :return: A list with the descriptions of the indicators this post processor creates.
        """

    @classmethod
    @abstractmethod
    def get_num_time_steps(cls) -> int:
        """
        :return: The number of time steps this post processor requires.
        """


class VariablePostProcessor(PostProcessor):
    """A base class for Post Processors that operate on bio-physical variables."""

    @classmethod
    def get_type(cls) -> PostProcessorType:
        return PostProcessorType.VARIABLE_POST_PROCESSOR

    def process_variables(self, variable_data: dict) -> dict:
        """
        Performs the post processing
        :param variable_data: The input data required to perform the post processing
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

    @abstractmethod
    def process_observations(self, observations: ObservationsWrapper) -> dict:
        """
        Performs the post processing
        :param observations: A Wrapper around earth observation data. Provides a convenience method to access EO Data.
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
    def get_indicator_descriptions(cls) -> List[Variable]:
        """
        :return: A list with the descriptions of the indicators this post processor creates.
        """

    @classmethod
    @abstractmethod
    def get_type(cls) -> PostProcessorType:
        """
        :return: The Type of PostProcessor.
        """

    @classmethod
    @abstractmethod
    def get_required_input_data_types(cls) -> List[str]:
        """
        :return: The Input Data Types required by this post processor.
        """


    @classmethod
    @abstractmethod
    def create_post_processor(cls, indicator_names: List[str]) -> PostProcessor:
        """
        :param indicator_names: The indicators that shall be derived using this post processor. If the list is empty,
        all indicators will be derived.
        :return: An instance of the post processor associated with this creator.
        """
