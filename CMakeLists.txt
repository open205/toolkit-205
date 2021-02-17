cmake_minimum_required(VERSION 3.14.0)
project(toolkit-205)

# Set a default build type if none was specified
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
    "MinSizeRel" "RelWithDebInfo")
endif()

option( BUILD_TK205_TESTING "Build libtk205 testing targets" ON )

# Set up testing/coverage
if (BUILD_TK205_TESTING)
  set(TEST205_INPUT_EXAMPLES_DIR ${PROJECT_SOURCE_DIR}) # TODO Upgrade to configure_file method?
  enable_testing()
endif()

add_subdirectory(libtk205)
