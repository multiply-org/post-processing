import numpy as np

from abc import abstractmethod, ABCMeta
from typing import List

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'


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


class PostProcessor(metaclass=ABCMeta):
    """
    This is the base class for all MULTIPLY Post Processors. Each Post Processor must implement the functions defined
    herein.
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
    def get_required_variables(cls) -> List[str]:
        """
        :return: The list of biophysical parameters required by this post processor to work
        """

    @classmethod
    @abstractmethod
    def get_indicator_descriptions(cls) -> List[IndicatorDescription]:
        """
        :return: A list with the descriptions of the indicators this post processor creates.
        """

    @abstractmethod
    def initialize(self):
        """
        Does any preparation work to be done before post processing is applied.
        """

    @abstractmethod
    def process(self, variable_data: List[np.array]) -> List[np.array]:
        """
        Performs actual post processing
        :param variable_data: The input data required to perform the post processing
        :return: The result of the post processing
        """
