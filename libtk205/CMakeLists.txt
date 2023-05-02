set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
project(libtk205)

include(CTest)
set(JSON_BuildTests OFF CACHE INTERNAL "")

# include_directories adds locations to the -I command line
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/btwxt/include/btwxt)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/json/single_include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/vendor/json/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../schema-205/build/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../schema-205/schema205/src)

file(GLOB RS_schemas "${PROJECT_SOURCE_DIR}/../schema-205/schema-source/*.schema.yaml")
file(GLOB base_classes
        "${PROJECT_SOURCE_DIR}/../schema-205/schema205/src/*.h"
        "${PROJECT_SOURCE_DIR}/../schema-205/schema205/src/*.cpp")

foreach(schema IN LISTS RS_schemas)
  string(REGEX REPLACE "${PROJECT_SOURCE_DIR}/../schema-205/schema-source/(.*).schema.yaml" "\\1" schema_name "${schema}")
  string(TOLOWER ${schema_name} schema_name)
  list(APPEND rs_headers "${PROJECT_SOURCE_DIR}/../schema-205/build/include/${schema_name}.h")
  list(APPEND rs_src "${PROJECT_SOURCE_DIR}/../schema-205/build/cpp/${schema_name}.cpp")
  if (schema_name MATCHES "rs.*")
    list(APPEND factory_headers "${PROJECT_SOURCE_DIR}/../schema-205/build/include/${schema_name}_factory.h")
    list(APPEND factory_src "${PROJECT_SOURCE_DIR}/../schema-205/build/cpp/${schema_name}_factory.cpp")
  endif()
endforeach()

list(APPEND lib_headers "${CMAKE_CURRENT_SOURCE_DIR}/include/typeinfo_205.h"
                        "${CMAKE_CURRENT_SOURCE_DIR}/include/loadobject_205.h")

# Runs if OUTPUT is missing, or if OUTPUT exists BUT file DEPENDencies have changed
# If OUTPUT exists and DEPENDS files haven't changed, the command is not run (?)
add_custom_command(OUTPUT ${rs_headers} ${rs_src} ${lib_headers} ${base_classes}
                  COMMAND poetry run doit cpp
                  DEPENDS ${RS_schemas}
                  COMMENT "Generate libtk205 files from YAML schema"
                  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../schema-205")

set (SOURCES "${lib_headers}"
             "${rs_headers}"
             "${rs_src}"
             "${factory_headers}"
             "${factory_src}"
             "${base_classes}")

add_library(libtk205 ${SOURCES})

# add_custom_target(update_lib_repo ALL
#                   COMMAND ${CMAKE_COMMAND} "-DPROJECT_SOURCE_DIR=${PROJECT_SOURCE_DIR}" -P "${PROJECT_SOURCE_DIR}/cmake/update_lib_repo.cmake"
#                   VERBATIM)
# add_dependencies(update_lib_repo libtk205)

add_subdirectory(vendor)
target_link_libraries(libtk205 PUBLIC courierr fmt)

if (BUILD_TK205_TESTING)
  add_compile_definitions(TEST205_INPUT_EXAMPLES_DIR="${TEST205_INPUT_EXAMPLES_DIR}")
  add_subdirectory(test)
endif()

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
