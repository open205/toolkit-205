if (NOT TARGET btwxt)
    add_subdirectory(btwxt)
endif()

if (NOT TARGET nlohmann_json) #TODO: check if used
    add_subdirectory(json)
endif()

if (BUILD_TK205_TESTING AND NOT TARGET gtest)

    # Prevent GoogleTest from overriding our compiler/linker options
    # when building with Visual Studio
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    set(BUILD_GTEST ON CACHE BOOL "" FORCE)
    add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/btwxt/vendor/googletest)

endif()