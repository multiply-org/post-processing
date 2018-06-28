import pkg_resources

from typing import List

from .post_processor import PostProcessor, PostProcessorCreator


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
