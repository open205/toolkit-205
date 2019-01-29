if (CMAKE_VERSION VERSION_LESS 3.2)
    set(UPDATE_DISCONNECTED_IF_AVAILABLE "")
else()
    set(UPDATE_DISCONNECTED_IF_AVAILABLE "UPDATE_DISCONNECTED 1")
endif()

include("${PROJECT_SOURCE_DIR}/cmake/DownloadProject.cmake")
download_project(PROJ                FlatBuffers
                 GIT_REPOSITORY      https://github.com/google/flatbuffers.git
                 GIT_TAG             v1.10.0
                 DOWNLOAD_DIR        "${CMAKE_CURRENT_BINARY_DIR}/FlatBuffers-dl"
                 SOURCE_DIR          "${CMAKE_CURRENT_SOURCE_DIR}/FlatBuffers"
                 BINARY_DIR          "${CMAKE_CURRENT_BINARY_DIR}/FlatBuffers"
                 ${UPDATE_DISCONNECTED_IF_AVAILABLE}
)

set(FLATBUFFERS_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(FLATBUFFERS_INSTALL OFF CACHE BOOL "" FORCE)
set(FLATBUFFERS_BUILD_FLATHASH OFF CACHE BOOL "" FORCE)


add_subdirectory(${FlatBuffers_SOURCE_DIR})
