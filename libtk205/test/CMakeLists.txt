# Test Executable

include_directories("${libtk205_SOURCE_DIR}/include"
                    "${libtk205_SOURCE_DIR}/src/build/include"
                    "${gtest_SOURCE_DIR}/include")

set(library_sources
  fixtures_libtk205.hpp
  main_libtk205.cpp
)

link_libraries(libtk205 gtest gmock)

add_executable(libtk205_tests ${library_sources})

include(GoogleTest)

gtest_discover_tests(libtk205_tests TEST_PREFIX libtk205:)
