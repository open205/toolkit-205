include_directories("${PROJECT_SOURCE_DIR}/vendor/FlatBuffers/include")
include_directories("${PROJECT_BINARY_DIR}/cpp")

if(EXISTS "${CMAKE_TOOLCHAIN_FILE}")
  # do not apply any global settings if the toolchain
  # is being configured externally
elseif(APPLE)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -stdlib=libc++")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -pedantic -Werror -Wextra -Wno-unused-parameter")
elseif(CMAKE_COMPILER_IS_GNUCXX)
  if(CYGWIN)
    set(CMAKE_CXX_FLAGS
      "${CMAKE_CXX_FLAGS} -std=gnu++11")
  else(CYGWIN)
    set(CMAKE_CXX_FLAGS
      "${CMAKE_CXX_FLAGS} -std=c++0x")
  endif(CYGWIN)
  set(CMAKE_CXX_FLAGS
    "${CMAKE_CXX_FLAGS} -Wall -pedantic -Werror -Wextra -Werror=shadow")
  if (GCC_VERSION VERSION_GREATER 4.4)
    set(CMAKE_CXX_FLAGS
      "${CMAKE_CXX_FLAGS} -Wunused-result -Werror=unused-result \
                          -Wunused-parameter -Werror=unused-parameter")
  endif()

  # Certain platforms such as ARM do not use signed chars by default
  # which causes issues with certain bounds checks.
  set(CMAKE_CXX_FLAGS
    "${CMAKE_CXX_FLAGS} -fsigned-char")

elseif(${CMAKE_CXX_COMPILER_ID} MATCHES "Clang")
  set(CMAKE_CXX_FLAGS
      "${CMAKE_CXX_FLAGS} -std=c++0x -Wall -pedantic -Werror \
                          -Wextra -Wno-unused-parameter")
  if(NOT "${CMAKE_SYSTEM_NAME}" MATCHES "Linux")
    set(CMAKE_CXX_FLAGS
        "${CMAKE_CXX_FLAGS} -stdlib=libc++")
  endif()
  if(NOT ("${CMAKE_SYSTEM_NAME}" MATCHES "FreeBSD" OR
          "${CMAKE_SYSTEM_NAME}" MATCHES "Linux"))
    set(CMAKE_EXE_LINKER_FLAGS
        "${CMAKE_EXE_LINKER_FLAGS} -lc++abi")
  endif()

  # Certain platforms such as ARM do not use signed chars by default
  # which causes issues with certain bounds checks.
  set(CMAKE_CXX_FLAGS
    "${CMAKE_CXX_FLAGS} -fsigned-char")

elseif(MSVC)
  # Visual Studio pedantic build settings
  # warning C4512: assignment operator could not be generated
  # warning C4316: object allocated on the heap may not be aligned
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4 /WX /wd4512 /wd4316")
endif()

add_executable(chiller-parser chiller.cpp)
add_dependencies(chiller-parser ASHRAE205-cpp)

add_test(
  NAME cpp-reader-test
  COMMAND chiller-parser "${PROJECT_BINARY_DIR}/examples/python-writer/chiller.a205"
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)
