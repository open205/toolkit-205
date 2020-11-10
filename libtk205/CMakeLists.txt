cmake_minimum_required(VERSION 3.0.0)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
project(libtktest VERSION 0.1.0)

include(CTest)
enable_testing()
set(JSON_BuildTests OFF CACHE INTERNAL "")

include_directories(vendor/btwxt/src)
include_directories(vendor/json/single_include)
include_directories(vendor/json/include)
include_directories(src/build/cpp)
include_directories(include)

list(APPEND Factory_SOURCES "./src/RS_instance_factory.cpp"
                            "./src/RS0001_factory.cpp"
                            "./src/RS0002_factory.cpp"
                            "./src/RS0003_factory.cpp"
                            "./src/RS0004_factory.cpp"
                            "./src/RS0005_factory.cpp"
                            "./src/RS0006_factory.cpp"
)
list(APPEND RS_SOURCES "./src/build/cpp/ASHRAE205.cpp"
                       "./src/build/cpp/RS0001.cpp"
                       "./src/build/cpp/RS0002.cpp"
                       "./src/build/cpp/RS0003.cpp"
                       "./src/build/cpp/RS0004.cpp"
                       "./src/build/cpp/RS0005.cpp"
                       "./src/build/cpp/RS0006.cpp"
)

set (SOURCES ${Factory_SOURCES} ${RS_SOURCES})
add_executable(libtk205 src/load.cpp ${SOURCES})

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
