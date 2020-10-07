[![Build and Test](https://github.com/open205/toolkit-205/workflows/Build%20and%20Test/badge.svg)](https://github.com/open205/toolkit-205/actions?query=workflow%3A%22Build+and+Test%22)

Toolkit 205
===========

A toolkit to facilitate the adoption of the ASHRAE Standard 205P data exchange specification.

**Disclaimer:** While this toolkit is developed in conjunction with the ASHRAE Standard 205 project committee, it is not an official ASHRAE product or a part of the standard.

**Warning!**  As the proposed ASHRAE Standard 205P has not yet been published, the content in this repository is subject to change and should be considered unstable for application development.

About ASHRAE 205
----------------

ASHRAE Standard 205P is "Standard Representation of Performance Simulation Data for HVAC&R and Other Facility Equipment". While the standard is not yet published, public reviews are available at [ASHRAE's online review portal](https://osr.ashrae.org/default.aspx).

The stated purpose of ASHRAE Standard 205 is:

> To facilitate sharing of equipment characteristics for performance simulation by defining standard representations such as data models, data formats, and automation interfaces.

The Standard is intended to support the following use cases:

- **Data Publication** Data publishers (typically equipment manufacturers) use representation specifications to guide implementation of data writing and validity testing software that produces correctly-formed representation files.

- **Application Development** Application developers use representation specifications to guide implementation of software that correctly reads representation data. Such implementations may include validity tests and developers may use representation specification example data for testing purposes.

- **Data Application** Application users use representation specifications to understand and check representation data. Data exchange will generally be automated but the availability of representation specifications facilitates additional data checking when needed.

Generally, a data publisher (e.g., manufacturer) provides an ASHRAE Standard 205 representation of a specific piece of equipment that the application user can load into compliant performance simulation software.

Building
--------

Toolkit 205 uses git submodules. To clone the submodules, you will either have to:

1. use a recursive clone when initially cloning this repository:

    `git clone --recurse-submodules https://github.com/open205/toolkit-205.git`

    or

2. do a recursive submodule update after cloneing this repository:

    `git submodule update --init --recursive`

We are currently supporting python 3.x.

In order to contribute to Toolkit 205, you will need to set up a consistent virtual environment for testing.
This project uses `pipenv` to create a virtual python environment and install the required dependencies.
Install `pipenv` through `pip`:

`pip install pipenv`

With `pipenv` installed, you may now create the virtual environment (defined in the `Pipfile`) where you will install the project and developer dependencies:

`pipenv install --dev`


Finally, you can build (generate the schema, translate examples, generate templates, and generate web content) and test the toolkit:

`pipenv run doit`

### Products

tk205 is both a python module and a command line tool.

Example Usage
-------------

TODO