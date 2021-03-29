set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
project(libtk205)

include(CTest)
set(JSON_BuildTests OFF CACHE INTERNAL "")

# include_directories adds locations to the -I command line
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/btwxt/src)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/json/single_include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/json/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../schema-205/build/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../schema-205/schema205/src)

add_subdirectory(vendor/btwxt)

add_custom_target(generate_cpp ALL 
                  COMMAND doit headers
                  #COMMAND doit -s cpp
                  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../schema-205")

set (SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/src/libtk205.cpp"
             "${CMAKE_CURRENT_SOURCE_DIR}/src/error_handling_tk205.cpp"
             "${CMAKE_CURRENT_SOURCE_DIR}/src/rs_instance_factory.cpp")

message(STATUS "libtk205 sources: ${SOURCES}")

add_library(libtk205 ${SOURCES})
add_dependencies(libtk205 generate_cpp)

add_subdirectory(vendor)

if (BUILD_TK205_TESTING)
  add_compile_definitions(TEST205_INPUT_EXAMPLES_DIR="${TEST205_INPUT_EXAMPLES_DIR}")
  add_subdirectory(test)
endif()

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
