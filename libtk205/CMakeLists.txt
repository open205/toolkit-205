set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
project(libtk205)

include(CTest)
set(JSON_BuildTests OFF CACHE INTERNAL "")

# include_directories adds locations to the -I command line
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/btwxt/src)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/json/single_include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/json/include)
# Two "deeper" include directories necessary bc Valijson doesn't scope includes the same as everyone else
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/json/single_include/nlohmann)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/json/include/nlohmann)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/valijson/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../schema-205/build/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../schema-205/schema205/src)

file(GLOB RS_schemas "${PROJECT_SOURCE_DIR}/../schema-205/schema-source/*.schema.yaml")

foreach(schema IN LISTS RS_schemas)
  string(REGEX REPLACE "${PROJECT_SOURCE_DIR}/../schema-205/schema-source/(.*).schema.yaml" "\\1" schema_name "${schema}")
  list(APPEND RS_headers "${PROJECT_SOURCE_DIR}/../schema-205/build/include/${schema_name}.h")
  list(APPEND RS_src "${PROJECT_SOURCE_DIR}/../schema-205/build/cpp/${schema_name}.cpp")
endforeach()

list(APPEND lib_headers "${PROJECT_SOURCE_DIR}/../schema-205/build/include/libtk205.h")
list(APPEND lib_src "${PROJECT_SOURCE_DIR}/../schema-205/build/cpp/libtk205.cpp")

add_custom_command(OUTPUT ${RS_headers} ${RS_src} ${lib_headers} ${lib_src}
                  COMMAND poetry run doit cpp
                  DEPENDS ${RS_schemas}
                  COMMENT "Generate libtk205 files from YAML schema"
                  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../schema-205")

set (SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/src/error_handling_tk205.cpp"
             "${RS_headers}"
             "${RS_src}"
             "${lib_headers}"
             "${lib_src}")

add_library(libtk205 ${SOURCES})

add_subdirectory(vendor)

if (BUILD_TK205_TESTING)
  add_compile_definitions(TEST205_INPUT_EXAMPLES_DIR="${TEST205_INPUT_EXAMPLES_DIR}")
  add_subdirectory(test)
endif()

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
