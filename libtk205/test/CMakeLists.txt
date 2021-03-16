# Test Executable

include_directories("${libtk205_SOURCE_DIR}/include"
                    "${libtk205_SOURCE_DIR}/../schema-205/build/include"
                    "${gtest_SOURCE_DIR}/include")

file(GLOB RS_SOURCES "${libtk205_SOURCE_DIR}/../schema-205/build/cpp/*.cpp")
file(GLOB RS_HEADERS "${libtk205_SOURCE_DIR}/../schema-205/build/include/*.h")

set(library_sources
  fixtures_libtk205.hpp
  main_libtk205.cpp
  ${RS_HEADERS} 
  ${RS_SOURCES}
)
message(STATUS "${library_sources}")

link_libraries(libtk205 gtest gmock)

add_executable(libtk205_tests ${library_sources})

include(GoogleTest)

gtest_discover_tests(libtk205_tests TEST_PREFIX libtk205:)

# add_custom_command(TARGET libtk205_tests POST_BUILD
#                    COMMAND doit clean
#                    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../../schema-205")
