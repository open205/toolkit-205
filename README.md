[![Build and Test](https://github.com/open205/toolkit-205/workflows/Build%20and%20Test/badge.svg)](https://github.com/open205/toolkit-205/actions?query=workflow%3A%22Build+and+Test%22)

Toolkit 205
===========

A toolkit to facilitate the adoption of the ASHRAE Standard 205, "Representation of Performance Data for HVAC&R and Other Facility Equipment", data exchange specification. Learn more about ASHRAE Standard 205 at https://data.ashrae.org/standard205/.

**Disclaimer:** While this toolkit is developed in conjunction with the ASHRAE Standard 205 project committee, it is not an official ASHRAE product or a part of the standard.

Building the Toolkit
--------------------

Toolkit 205 uses git submodules. To clone the submodules, you will either have to:

1. use a recursive clone when initially cloning this repository:

    `git clone --recurse-submodules https://github.com/open205/toolkit-205.git`

    or

2. do a recursive submodule update after cloning this repository:

    `git submodule update --init --recursive`

We are currently supporting python 3.7 and higher.

This project uses [Poetry](https://python-poetry.org/docs/#installation) python package management tool. Once you have Poetry installed you can install the dependencies using:

`poetry install`

You can test your installation using:

`poetry run doit`

### Products

tk205 is both a python module and a command line tool.

Building the Toolkit C++ library
--------------------------------

The toolkit can additionally build a C++ library suitable for import into C++ modeling tools. The library (libtk205) uses elements of the schema-205 submodule to auto-generate source code for Representation Specifications, and includes other source files from this repository.

To build the library, use

`cmake -B build`

to generate build files for an "out-of-source" build directory, then

`cmake --build build --config [Debug/Release]`

to build libtk205.

**Note:** Because the tests for libtk205 automatically clean all auto-generated files after the build, the cmake generator must be run fresh each time. This ensures that no Representations are out of date.
