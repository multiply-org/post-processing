#!/usr/bin/env python

from setuptools import setup

requirements = [
    'numpy'
]

__version__ = None
with open('multiply_data_access/version.py') as f:
    exec(f.read())

setup(name='multiply-post-processing',
      version=__version__,
      description='MULTIPLY Post Processing',
      author='MULTIPLY Team',
      packages=['multiply_post_processing'],
      entry_points={
          'post_processor_creators': [
          ],
      },
      install_requires=requirements
)
