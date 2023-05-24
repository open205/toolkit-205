cmake_minimum_required(VERSION 3.14.0)
project(toolkit-205)

if (USE_CLANGTIDY_STATIC_ANALYSIS)
   set(CMAKE_CXX_CLANG_TIDY 
   clang-tidy;
   -checks=-*,clang-analyzer-*,cppcoreguidelines-*
   )
endif()

# Set a default build type if none was specified
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
    "MinSizeRel" "RelWithDebInfo")
endif()

# Run libtk205 generator

file(GLOB RS_schemas "${PROJECT_SOURCE_DIR}/schema-205/schema-source/*.schema.yaml")

foreach(schema IN LISTS RS_schemas)
  string(REGEX REPLACE "${PROJECT_SOURCE_DIR}/schema-205/schema-source/(.*).schema.yaml" "\\1" schema_name "${schema}")
  string(TOLOWER ${schema_name} schema_name)
  list(APPEND rs_headers "${PROJECT_SOURCE_DIR}/schema-205/build/include/${schema_name}.h")
  list(APPEND rs_src "${PROJECT_SOURCE_DIR}/schema-205/build/cpp/${schema_name}.cpp")
  if (schema_name MATCHES "rs.*")
    list(APPEND factory_headers "${PROJECT_SOURCE_DIR}/schema-205/build/include/${schema_name}_factory.h")
    list(APPEND factory_src "${PROJECT_SOURCE_DIR}/schema-205/build/cpp/${schema_name}_factory.cpp")
  endif()
endforeach()

if(BUILD_LIBTK205)
  execute_process(
    COMMAND ${CMAKE_COMMAND} -DPA_TOKEN=${PA_TOKEN} -DPROJECT_SOURCE_DIR=${PROJECT_SOURCE_DIR} -P "cmake/get_lib_repo_local.cmake"
  )
  add_subdirectory(libtk205)

  add_custom_target(libtk205_generator ALL
                    DEPENDS ${rs_headers} ${rs_src} ${factory_headers} ${factory_src})
                    
  # Runs if OUTPUT is missing, or if OUTPUT exists BUT file DEPENDencies have changed
  # If OUTPUT exists and DEPENDS files haven't changed, the command is not run.
  # If no target depends on its outputs, the command is not run (see libtk205_generator custom target)
  add_custom_command(OUTPUT ${rs_headers} ${rs_src} ${factory_headers} ${factory_src}
                    COMMAND poetry run doit cpp
                    COMMAND ${CMAKE_COMMAND} -DPROJECT_SOURCE_DIR=${PROJECT_SOURCE_DIR} -P "../cmake/update_lib_repo_local.cmake"
                    DEPENDS ${RS_schemas}
                    COMMENT "Generate libtk205 files from YAML schema"
                    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/schema-205")
endif()