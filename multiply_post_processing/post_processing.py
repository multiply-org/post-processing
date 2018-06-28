import pkg_resources

from typing import List

from .post_processor import PostProcessor


__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

POST_PROCESSOR_REGISTRY = []


def add_post_processor(post_processor: PostProcessor):
    POST_PROCESSOR_REGISTRY.append(post_processor)


registered_post_processors = pkg_resources.iter_entry_points('post_processors')
for registered_post_processor in registered_post_processors:
    add_post_processor(registered_post_processor.load())
    POST_PROCESSOR_REGISTRY.append(registered_post_processor.load())


def get_post_processor_names() -> List[str]:
    """
    :return: the names of all post processors registered in the post processing component
    """
    post_processor_names = []
    for post_processor in POST_PROCESSOR_REGISTRY:
        post_processor_names.append(post_processor.get_name())
    return post_processor_names


def get_post_processor(name: str) -> PostProcessor:
    """
    :param A name of a post-processor
    :return: the post processor of the requested name
    """
    for post_processor in POST_PROCESSOR_REGISTRY:
        if name == post_processor.get_name():
            return post_processor
    raise ValueError('No post processor with name {} found.'.format(name))
