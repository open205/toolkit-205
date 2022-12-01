# Test Executable

include_directories(${PROJECT_SOURCE_DIR}/vendor/json/single_include)
include_directories(${PROJECT_SOURCE_DIR}/vendor/json/include)

include_directories(${PROJECT_SOURCE_DIR}/include)
include_directories(${PROJECT_SOURCE_DIR}/../schema-205/build/include)
include_directories(${PROJECT_SOURCE_DIR}/../schema-205/schema205/src) # rs_instance_factory/base
include_directories(${gtest_SOURCE_DIR}/include)

include(GoogleTest)

set (SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/fixtures_libtk205.hpp
             ${CMAKE_CURRENT_SOURCE_DIR}/main_libtk205.cpp
             ${PROJECT_SOURCE_DIR}/../schema-205/schema205/src/rs_instance_factory.h
             ${PROJECT_SOURCE_DIR}/../schema-205/schema205/src/rs_instance_factory.cpp)

#Does the following command do anything?
set_source_files_properties(${SOURCES} PROPERTIES GENERATED TRUE)

add_executable(libtk205_tests ${SOURCES})
target_link_libraries(libtk205_tests libtk205 btwxt gtest gmock)

gtest_discover_tests(libtk205_tests TEST_PREFIX libtk205:)
