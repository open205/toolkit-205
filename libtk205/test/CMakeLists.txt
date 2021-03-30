# Test Executable

include_directories(${PROJECT_SOURCE_DIR}/vendor/json/single_include)
include_directories(${PROJECT_SOURCE_DIR}/vendor/json/include)

include_directories(${PROJECT_SOURCE_DIR}/include)
include_directories(${PROJECT_SOURCE_DIR}/../schema-205/build/include)
include_directories(${gtest_SOURCE_DIR}/include)

include(GoogleTest)

execute_process(COMMAND doit headers cpp
                WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/../schema-205")
file(GLOB RS_headers "${PROJECT_SOURCE_DIR}/../schema-205/build/include/*.h")
file(GLOB RS_src "${PROJECT_SOURCE_DIR}/../schema-205/build/cpp/*.cpp")

set (SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/fixtures_libtk205.hpp
             ${CMAKE_CURRENT_SOURCE_DIR}/main_libtk205.cpp
             ${RS_headers}
             ${RS_src})
message(STATUS "libtk205_tests sources: ${SOURCES}")

#Does the following command do anything?
set_source_files_properties(${SOURCES} PROPERTIES GENERATED TRUE)

add_executable(libtk205_tests ${SOURCES})
target_link_libraries(libtk205_tests libtk205 btwxt gtest gmock)

gtest_discover_tests(libtk205_tests TEST_PREFIX libtk205:)

# Optional clean: Copy files to distributable directory first, if desired
add_custom_command(TARGET libtk205_tests POST_BUILD
                   COMMAND doit clean headers cpp
                   WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/../schema-205")

