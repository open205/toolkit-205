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

Why FlatBuffers?
----------------

[FlatBuffers](http://google.github.io/flatbuffers/) is a computationally fast and memory efficient cross platform serialization library. It uses a defined schema to generate minimal source code for several languages including: C/C++, Python, Java, and JavaScript.

Supported Equipment
-------------------

Each type of equipment has a corresponding FlatBuffer schema file (*.fbs):

- **RS0001** Liquid-Cooled Chillers
- **RS0002** Unitary Cooling Air-Conditioning Equipment
- **RS0003** Fan Assemblies

Each of these schemas is nested within a top level schema, *ASHRAE205.fbs*, that is analogous to a base-class for any equipment representation schema.

Finally, there are common definitions included in the *common.fbs* schema file referenced by all representations.

Building
--------

### Compiled Components

#### Dependencies

- CMake
- Git
- Anaconda Python 3.x (used in example)
- C++ compiler (used in example)

#### Compile steps:

From the root directory:

1. `mkdir build`
2. `cd build`
3. `cmake ..`
4. `cmake --build . --config Release`

### Python Toolkit, tk205

1. `python -m venv env`
2. On Windows, run:

    `env\Scripts\activate.bat`

    On Unix or MacOS, run:

    `source env/bin/activate`
3. `pip install --editable .`
4. `deactivate` when finished with development


### Products

Currently, the build process will produce:

- C++ language files for reading/writing ASHRAE 205 FlatBuffer files
- Python language files for reading/writing ASHRAE 205 FlatBuffer files
- Binary and JSON versions of the schema
- An example C++ program to read an RS0001 (i.e., Chiller) representation.

Example Usage
-------------

To test the example type `ctest -C Release` in the `build` directory.

The provided example demonstrates the ability to generate a FlatBuffer in Python based on spreadsheet data provided by a manufacturer.

The FlatBuffer is then read into C++ demonstrating general functionality of the data exchange and use in native C++ structures.
