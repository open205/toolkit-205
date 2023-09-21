set(clone_dir "${PROJECT_SOURCE_DIR}/${repo_name}")

set(include_dest_dir "${clone_dir}/include/${repo_name}")
set(src_dest_dir "${clone_dir}/src")

file(MAKE_DIRECTORY "${include_dest_dir}")
file(MAKE_DIRECTORY "${src_dest_dir}")

# Move/copy generated and fixed files
file(GLOB generated_rs_headers "${PROJECT_SOURCE_DIR}/schema-205/build/include/*.h")
foreach(filepath ${generated_rs_headers})
  get_filename_component(filename ${filepath} NAME)
  message(STATUS "Moving ${filepath} to ${include_dest_dir}/${filename}.")
  file(RENAME ${filepath} ${include_dest_dir}/${filename})
endforeach(filepath)

file(GLOB fixed_headers "${PROJECT_SOURCE_DIR}/schema-205/schema205/libtk205_fixed_src/include/*.h")
foreach(in_file IN LISTS fixed_headers)
     # Get just the file name, w/o path
     get_filename_component(out_file ${in_file} NAME)
     message(STATUS "Copying ${in_file} to ${include_dest_dir}/${out_file}.")
     file(COPY_FILE ${in_file} "${include_dest_dir}/${out_file}")
endforeach()

file(GLOB generated_rs_src "${PROJECT_SOURCE_DIR}/schema-205/build/cpp/*.cpp")
foreach(filepath ${generated_rs_src})
     get_filename_component(filename ${filepath} NAME)
     message(STATUS "Moving ${filepath} to ${src_dest_dir}/${filename}.")
     file(RENAME ${filepath} ${src_dest_dir}/${filename})
endforeach(filepath)
     
file(GLOB fixed_src "${PROJECT_SOURCE_DIR}/schema-205/schema205/libtk205_fixed_src/src/*.cpp")
foreach(in_file IN LISTS fixed_src)
     # Get just the file name, w/o path
     get_filename_component(out_file ${in_file} NAME)
     message(STATUS "Copying ${in_file} to ${src_dest_dir}/${out_file}.")
     file(COPY_FILE ${in_file} "${src_dest_dir}/${out_file}")
endforeach()
     
file(COPY "${PROJECT_SOURCE_DIR}/schema-205/examples"
     DESTINATION "${clone_dir}")

# git status (see if files changed)
execute_process(COMMAND ${GIT_EXECUTABLE} status
        WORKING_DIRECTORY ${clone_dir}
)
