set(repo_name "libtk205")
set(clone_dir "${PROJECT_SOURCE_DIR}/${repo_name}")

set(include_dest_dir "${clone_dir}/include/${repo_name}")
set(src_dest_dir "${clone_dir}/src")

file(MAKE_DIRECTORY "${include_dest_dir}")
file(MAKE_DIRECTORY "${src_dest_dir}")

# Move/copy generated files
file(GLOB generated_rs_headers "${PROJECT_SOURCE_DIR}/schema-205/build/include/*.h")
foreach(filepath ${generated_rs_headers})
  get_filename_component(filename ${filepath} NAME)
  message(STATUS "Moving ${filepath} to ${include_dest_dir}/${filename}.")
  file(RENAME ${filepath} ${include_dest_dir}/${filename})
endforeach(filepath)

file(COPY "${PROJECT_SOURCE_DIR}/../schema-205/schema205/libtk205_fixed_src/include/"
     DESTINATION "${include_dest_dir}"
     FILES_MATCHING PATTERN *.h)

file(GLOB generated_rs_src "${PROJECT_SOURCE_DIR}/schema-205/build/cpp/*.cpp")
     foreach(filepath ${generated_rs_src})
       get_filename_component(filename ${filepath} NAME)
       message(STATUS "Moving ${filepath} to ${src_dest_dir}/${filename}.")
       file(RENAME ${filepath} ${src_dest_dir}/${filename})
     endforeach(filepath)
     
file(COPY "${PROJECT_SOURCE_DIR}/../schema-205/schema205/libtk205_fixed_src/src/"
     DESTINATION "${src_dest_dir}"
     FILES_MATCHING PATTERN *.cpp)

file(COPY "${PROJECT_SOURCE_DIR}/schema-205/examples"
     DESTINATION "${clone_dir}")

# git status (see if files changed)
execute_process(COMMAND ${GIT_EXECUTABLE} status
        WORKING_DIRECTORY ${clone_dir}
)

# # git add
# execute_process(COMMAND ${GIT_EXECUTABLE} add include src test examples
#                 WORKING_DIRECTORY ${clone_dir}
# )
# # git commit
# execute_process(COMMAND ${GIT_EXECUTABLE} commit -m "\"${last_commit_msg}\""
#                 WORKING_DIRECTORY ${clone_dir}
# )
# # git push
# execute_process(COMMAND ${GIT_EXECUTABLE} push
#                 WORKING_DIRECTORY ${clone_dir}
# )
