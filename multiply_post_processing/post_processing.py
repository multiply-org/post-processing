import glob
import pkg_resources

from multiply_core.observations import GeoTiffWriter, ObservationsFactory, data_validation
from multiply_core.util import FileRef, FileRefCreation, Reprojection, get_time_from_string
from shapely.geometry import Polygon
from typing import List, Optional, Union

from .post_processor import PostProcessor, PostProcessorCreator, PostProcessorType


__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

POST_PROCESSOR_CREATOR_REGISTRY = []


def add_post_processor_creator(post_processor_creator: PostProcessorCreator):
    POST_PROCESSOR_CREATOR_REGISTRY.append(post_processor_creator)


registered_post_processor_creators = pkg_resources.iter_entry_points('post_processor_creators')
for registered_post_processor_creator in registered_post_processor_creators:
    add_post_processor_creator(registered_post_processor_creator.load())
    POST_PROCESSOR_CREATOR_REGISTRY.append(registered_post_processor_creator.load())


def get_post_processor_names() -> List[str]:
    """
    :return: the names of all post processors registered in the post processing component
    """
    post_processor_names = []
    for post_processor_creator in POST_PROCESSOR_CREATOR_REGISTRY:
        post_processor_names.append(post_processor_creator.get_name())
    return post_processor_names


def get_post_processor_description(name: str) -> str:
    """
    :param A name of a post-processor
    :return: the description of the post processor of the requested name
    """
    for post_processor_creator in POST_PROCESSOR_CREATOR_REGISTRY:
        if name == post_processor_creator.get_name():
            return post_processor_creator.get_description()
    raise ValueError('No post processor with name {} found.'.format(name))


def get_post_processor(name: str) -> PostProcessor:
    """
    :param A name of a post-processor
    :return: the post processor of the requested name
    """
    for post_processor_creator in POST_PROCESSOR_CREATOR_REGISTRY:
        if name == post_processor_creator.get_name():
            return post_processor_creator.create_post_processor()
    raise ValueError('No post processor with name {} found.'.format(name))


# todo almost the same method is included in inference engine. Move it to core as part of the observations factory.
def _get_valid_files(datasets_dir: str, supported_eo_data_types: Optional[List[str]] = []) -> FileRef:
    file_refs = []
    file_ref_creation = FileRefCreation()
    found_files = glob.glob(datasets_dir + '/**', recursive=True)
    for found_file in found_files:
        type = data_validation.get_valid_type(found_file)
        if (len(supported_eo_data_types) > 0 and type in supported_eo_data_types) or type is not '':
            file_ref = file_ref_creation.get_file_ref(type, found_file)
            if file_ref is not None:
                file_refs.append(file_ref)
    return file_refs


def run_post_processor(name: str, data_path: str,
                       roi: Optional[Union[str, Polygon]],
                       spatial_resolution: Optional[int],
                       roi_grid: Optional[str],
                       destination_grid: Optional[str],
                       output_format: Optional[str] = 'GTiff', ):
    post_processor = get_post_processor(name)
    if post_processor.get_type() == PostProcessorType.EO_DATA_POST_PROCESSOR:
        post_processor.initialize()
        # collect input data
        supported_eo_data_types = post_processor.get_names_of_supported_eo_data_types()
        file_refs = _get_valid_files(data_path, supported_eo_data_types)
        observations_factory = ObservationsFactory()
        observations_factory.sort_file_ref_list(file_refs)
        # an observations wrapper to be passed to kafka
        observations = observations_factory.create_observations(file_refs)
        # todo consider passing reprojection
        results = post_processor.process_observations(observations)
        if output_format == 'GTiff':
            writer = GeoTiffWriter()

        # def init(self, file_names: List[str], geo_transform: tuple, projection: str, width: int, height: int,
        #          num_bands: Optional[List[int]], data_types: Optional[List[str]]):
