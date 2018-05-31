<img alt="MULTIPLY" align="right" src="https://raw.githubusercontent.com/multiply-org/multiply-processing/master/doc/source/_static/logo/Multiply_multicolour.png" />


[![Build Status](https://travis-ci.org/multiply-org/multiply-processing.svg?branch=master)](https://travis-ci.org/multiply-org/multiply-processing)
[![Documentation Status](https://readthedocs.org/projects/multiply/badge/?version=latest)](http://multiply.readthedocs.io/en/latest/?badge=latest)
                
# MULTIPLY Post Processing

This repository contains the MULTIPLY post processing functionality.
It provides elemental implementations and a framework to allow users to plug-in their own dedicated post-processors.

## Contents

* `multiply_post_processing/` - The main software package
* `test/` - The test package
* `setup.py` - main build script, to be run with Python 3.6

## How to install

The first step is to clone the latest code and step into the check out directory: 

    $ git clone https://github.com/multiply-org/post-processing.git
    $ cd post-processing
    
The MULTIPLY Post Processing has been developed against Python 3.6.
It cannot be guaranteed to work with previous Python versions.
The MULTIPLY Post Processing can be run from sources directly.
To install the MULTIPLY Post Processing into an existing Python environment just for the current user, use

    $ python setup.py install --user
    
To install the MULTIPLY Post Processing for development and for the current user, use

    $ python setup.py develop --user

## How to use

MULTIPLY post Processing is available as Python Package.
To import it into your python application, use

    $ import multiply_post_processing

## License
The MULTIPLY Post Processing is distributed under terms and conditions of the [GPL3 License](https://www.gnu.org/licenses/gpl-3.0.de.html).
