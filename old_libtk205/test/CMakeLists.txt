# Test Executable

include(GoogleTest)

set (SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/fixtures_libtk205.hpp
             ${CMAKE_CURRENT_SOURCE_DIR}/main_libtk205.cpp
             ${PROJECT_SOURCE_DIR}/../schema-205/schema205/src/rs_instance_factory.h
             ${PROJECT_SOURCE_DIR}/../schema-205/schema205/src/rs_instance_factory.cpp)

set_source_files_properties(${SOURCES} PROPERTIES GENERATED TRUE) #TODO: Check if GENERATED property is used

add_executable(libtk205_tests ${SOURCES})
target_include_directories(libtk205_tests PRIVATE 
                           ${PROJECT_SOURCE_DIR}/include 
                           ${PROJECT_SOURCE_DIR}/../schema-205/build/include 
                           ${PROJECT_SOURCE_DIR}/../schema-205/schema205/src 
                           ${gtest_SOURCE_DIR}/include)
target_link_libraries(libtk205_tests libtk205 btwxt nlohmann_json gtest gmock)

gtest_discover_tests(libtk205_tests TEST_PREFIX libtk205:)
                                                                                                                                                                                                                                       