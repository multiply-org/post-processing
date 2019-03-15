<img alt="MULTIPLY" align="right" src="https://raw.githubusercontent.com/multiply-org/multiply-core/master/doc/source/_static/logo/Multiply_multicolour.png" />


[![Build Status](https://travis-ci.org/multiply-org/multiply-processing.svg?branch=master)](https://travis-ci.org/multiply-org/multiply-processing)

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

## Run the command line

To run the Post-Processing Framework from the command line, first checkout multiply-core and create conda environment
`multiply-platform-dev`:

    $ git clone https://github.com/multiply-org/multiply-core.git
    $ cd multiply-core
    $ conda env create

If the last command fails because `multiply-platform-dev` environment already exists, then just update it

    $ conda env update

Once in a while

    $ cd multiply-core
    $ git pull

Install

    $ source activate xcube-server-dev
    $ python setup.py develop

Then, checkout the post-processing framework and install it:

    $ git clone https://github.com/multiply-org/post-processing.git
    $ cd post-processing
    $ python setup.py develop

From then on, when you are within the multiply environment, you can use the command line.

Type:

    $ multiply_post --help

for info. Supported commands are

    $ multiply_post describe : Describes a post processor
    $ multiply_post indicators : Lists the provided indicators
    $ multiply_post process_indicators : Retrieves indicators
    $ multiply_post processors : Lists the names of the provided post processors
    $ multiply_post run_processor : Runs a post processor

Example calls for running the post processing from the command line are:

    $ multiply_post run_processor BurnedSeverity "\home\test_data" -r
        "POLYGON ((-2.1161534436028333 39.06796998380795, -2.0891905679389984 39.06776250050584,
        -2.089424595200457 39.049546053296766, -2.1163805451389095 39.049753402686,
        -2.1161534436028333 39.06796998380795))" -sr 10

Runs the BurnedSeverityPostProcessor on data provided at "\home\test_data" on the area stated with "-r" in
the resolution stated with "-sr" (10 m).

    $ multiply_post process_indicators 'cvh,mnnd,fe,fdiv' "\home\test_data"
        -r "POLYGON ((-2.1161534436028333 39.06796998380795, -2.0891905679389984 39.06776250050584,
        -2.089424595200457 39.049546053296766, -2.1163805451389095 39.049753402686,
        -2.1161534436028333 39.06796998380795))" -sr 20

Retrieves indicators cvh, mnnd, fe, and fdiv from data provided at "\home\test_data" on the area stated with "-r" in
the resolution stated with "-sr" (20 m).

## License
The MULTIPLY Post Processing is distributed under terms and conditions of the [GPL3 License](https://www.gnu.org/licenses/gpl-3.0.de.html).
