cmake_minimum_required(VERSION 3.0.0)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
project(libtktest)

include(CTest)
enable_testing()
set(JSON_BuildTests OFF CACHE INTERNAL "")

include_directories(vendor/btwxt/src)
include_directories(vendor/json/single_include)
include_directories(vendor/json/include)
include_directories(src/build/include)
include_directories(include)

add_subdirectory(vendor/btwxt)

list(APPEND Factory_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/src/RS_instance_factory.cpp"
                            "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0001_factory.cpp"
                            "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0002_factory.cpp"
                            "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0003_factory.cpp"
                            "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0004_factory.cpp"
                            "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0005_factory.cpp"
                            "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0006_factory.cpp"
)
list(APPEND RS_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/ASHRAE205.cpp"
                       "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0001.cpp"
                       "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0002.cpp"
                       "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0003.cpp"
                       "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0004.cpp"
                       "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0005.cpp"
                       "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp/RS0006.cpp"
)

add_custom_target(generate_cpp ALL 
                  COMMAND pipenv run doit headers
                  COMMAND pipenv run doit cpp
                  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../schema-205")

# copy_directory will create the destination if it does not exist
add_custom_target(copy_generated_source ALL
                  COMMAND cmake -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/../schema-205/build/include" "${CMAKE_CURRENT_SOURCE_DIR}/src/build/include"
                  COMMAND cmake -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/../schema-205/build/cpp" "${CMAKE_CURRENT_SOURCE_DIR}/src/build/cpp"
                  COMMAND cmake -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/../schema-205/schema205/src" "${CMAKE_CURRENT_SOURCE_DIR}/include")

set (SOURCES ${Factory_SOURCES} ${RS_SOURCES})
# The GENERATED property prevents the source files being used before they exist.
set_source_files_properties(${SOURCES} PROPERTIES GENERATED TRUE)

add_library(libtk205 src/libtk205.cpp ${SOURCES})
target_link_libraries(libtk205 btwxt)
add_dependencies(libtk205 copy_generated_source)
add_dependencies(copy_generated_source generate_cpp)

add_executable(libtktest src/load.cpp)
target_link_libraries(libtktest libtk205)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
