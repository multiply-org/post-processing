#!/usr/bin/env python

from setuptools import setup

requirements = [
    # 'numpy',
    # 'scipy',
    # 'scikit-learn',
    # 'shapely',
    # 'gdal'
]

__version__ = None
with open('multiply_post_processing/version.py') as f:
    exec(f.read())

setup(name='multiply-post-processing',
      version=__version__,
      description='MULTIPLY Post Processing',
      author='MULTIPLY Team',
      packages=['multiply_post_processing'],
      entry_points={
          'console_scripts': [
              'multiply_post = multiply_post_processing.cli.cli:main',
          ],
          'post_processor_creators': [
              'burned_severity_post_processor_creator = '
              'multiply_post_processing:burned_severity_post_processor.BurnedSeverityPostProcessorCreator',
              'functional_diversity_metrics_post_processor_creator = multiply_post_processing:'
              'functional_diversity_metrics_post_processor.FunctionalDiversityMetricsPostProcessorCreator'
          ],
          # 'variables': ['indicators = multiply_post_processing.indicators:indicators.get_indicators']
      },
      install_requires=requirements
)
