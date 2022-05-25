# repo_name is unique to the project
set(repo_name "libtk205")
set(upload_repo "github.com/open205/${repo_name}")
set(authenticated_repo "https://${PA_TOKEN}:x-oauth-basic@${upload_repo}") # PA_TOKEN is set by GitHub Actions

message(STATUS ${authenticated_repo})

if(NOT EXISTS "${PROJECT_SOURCE_DIR}/ci")
   file(MAKE_DIRECTORY "${PROJECT_SOURCE_DIR}/ci")
endif()
set(clone_dir "${PROJECT_SOURCE_DIR}/ci/${repo_name}")

find_package(Git QUIET)

if(GIT_FOUND)
   if(NOT EXISTS "${clone_dir}")
      execute_process(COMMAND ${GIT_EXECUTABLE} clone ${authenticated_repo}
                      WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/ci
                      RESULT_VARIABLE GIT_SUBMOD_RESULT)
      if(NOT GIT_SUBMOD_RESULT EQUAL "0")
         message(FATAL_ERROR "${GIT_EXECUTABLE} clone ${authenticated_repo} failed with ${GIT_SUBMOD_RESULT}.")
      endif()
   endif()
else()
   message(FATAL_ERROR "git not found!")
endif()

# git branch name query
execute_process(COMMAND ${GIT_EXECUTABLE} rev-parse --abbrev-ref HEAD
                WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
                OUTPUT_VARIABLE current_git_branch
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Current local branch is ${current_git_branch}.")

execute_process(COMMAND ${GIT_EXECUTABLE} log -1 --pretty=%B
                WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
                OUTPUT_VARIABLE last_commit_msg
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Last commit message on local branch was \"${last_commit_msg}\"")

execute_process(COMMAND ${GIT_EXECUTABLE} ls-remote --heads --exit-code ${authenticated_repo} ${current_git_branch}
                WORKING_DIRECTORY ${clone_dir}
                RESULT_VARIABLE exit_code
                OUTPUT_VARIABLE output_repo_branches
)
if(exit_code EQUAL "0")
   message(STATUS "Branch ${current_git_branch} exists in upload remote.")
   execute_process(COMMAND ${GIT_EXECUTABLE} checkout ${current_git_branch}
                   WORKING_DIRECTORY ${clone_dir}
   )
else()
   message(STATUS "Branch ${current_git_branch} must be created in upload remote.")
   execute_process(COMMAND ${GIT_EXECUTABLE} checkout -b ${current_git_branch}
                   WORKING_DIRECTORY ${clone_dir}
   )
   execute_process(COMMAND ${GIT_EXECUTABLE} push -u origin ${current_git_branch}
                   WORKING_DIRECTORY ${clone_dir}
   )
endif()

set(include_dest_dir "${clone_dir}/include/${repo_name}")
set(src_dest_dir "${clone_dir}/src")

file(MAKE_DIRECTORY "${include_dest_dir}")
file(MAKE_DIRECTORY "${src_dest_dir}")

# Copy generated files 
file(COPY "${PROJECT_SOURCE_DIR}/../schema-205/build/include/"
     DESTINATION "${include_dest_dir}"
     FILES_MATCHING PATTERN *.h)
file(COPY "${PROJECT_SOURCE_DIR}/include/"
     DESTINATION "${include_dest_dir}"
     FILES_MATCHING PATTERN *.h)
file(COPY "${PROJECT_SOURCE_DIR}/../schema-205/schema205/src/"
     DESTINATION "${include_dest_dir}"
     FILES_MATCHING PATTERN *.h)

file(COPY "${PROJECT_SOURCE_DIR}/../schema-205/build/cpp/"
     DESTINATION "${src_dest_dir}"
     FILES_MATCHING PATTERN *.cpp)
file(COPY "${PROJECT_SOURCE_DIR}/src/"
     DESTINATION "${src_dest_dir}"
     FILES_MATCHING PATTERN *.cpp)
file(COPY "${PROJECT_SOURCE_DIR}/../schema-205/schema205/src/"
     DESTINATION "${src_dest_dir}"
     FILES_MATCHING PATTERN *.cpp)

file(COPY "${PROJECT_SOURCE_DIR}/test/"
     DESTINATION "${clone_dir}/test"
     FILES_MATCHING 
      PATTERN *.cpp
      PATTERN *.hpp)

file(COPY "${PROJECT_SOURCE_DIR}/../schema-205/examples"
     DESTINATION "${clone_dir}")

# git config
execute_process(COMMAND ${GIT_EXECUTABLE} config user.name "Actions CI"
                WORKING_DIRECTORY ${clone_dir}
)
execute_process(COMMAND ${GIT_EXECUTABLE} config user.email "ci.bigladdersoftware.com"
                WORKING_DIRECTORY ${clone_dir}
)
# git add
execute_process(COMMAND ${GIT_EXECUTABLE} add include src test examples
                WORKING_DIRECTORY ${clone_dir}
)
# git commit
execute_process(COMMAND ${GIT_EXECUTABLE} commit -m"${last_commit_msg}"
                WORKING_DIRECTORY ${clone_dir}
)
# git push
execute_process(COMMAND ${GIT_EXECUTABLE} push
                WORKING_DIRECTORY ${clone_dir}
)
