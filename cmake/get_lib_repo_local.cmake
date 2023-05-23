# repo_name is unique to the project
set(repo_name "libtk205")
set(upload_repo "https://github.com/open205/${repo_name}")
if(${PA_TOKEN})
   set(authenticated_repo "https://${PA_TOKEN}:x-oauth-basic@${upload_repo}") # PA_TOKEN is set by GitHub Actions
else()
   set(authenticated_repo ${upload_repo})
endif()

message(STATUS ${authenticated_repo})

set(clone_dir "${PROJECT_SOURCE_DIR}/${repo_name}")

find_package(Git QUIET)

if(GIT_FOUND)
   if(NOT EXISTS "${clone_dir}")
      execute_process(COMMAND ${GIT_EXECUTABLE} clone ${authenticated_repo}
                      WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
                      RESULT_VARIABLE GIT_SUBMOD_RESULT)
      if(NOT GIT_SUBMOD_RESULT EQUAL "0")
         message(FATAL_ERROR "${GIT_EXECUTABLE} clone ${authenticated_repo} failed with ${GIT_SUBMOD_RESULT}.")
      endif()
   # else() pull or fetch?
   endif()
else()
   message(FATAL_ERROR "git not found!")
endif()

# git branch name query
execute_process(COMMAND ${GIT_EXECUTABLE} rev-parse --abbrev-ref HEAD
                WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
                OUTPUT_VARIABLE current_git_branch
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Current local branch is ${current_git_branch}.")

execute_process(COMMAND ${GIT_EXECUTABLE} log -1 --pretty=%B
                WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
                OUTPUT_VARIABLE last_commit_msg
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Last commit message on local branch was \"${last_commit_msg}\"")

execute_process(COMMAND ${GIT_EXECUTABLE} ls-remote --heads --exit-code ${authenticated_repo} ${current_git_branch}
                WORKING_DIRECTORY ${clone_dir}
                RESULT_VARIABLE exit_code
                OUTPUT_VARIABLE output_repo_branches
)
if(exit_code EQUAL "0") # Successful communication with remote (but matching refs status unknown)
   message(STATUS "Checking out branch ${current_git_branch} from ${repo_name} remote.")
   execute_process(COMMAND ${GIT_EXECUTABLE} checkout ${current_git_branch}
                   WORKING_DIRECTORY ${clone_dir}
   )
elseif(exit_code EQUAL "2") # No matching refs in remote
   message(STATUS "Branch ${current_git_branch} must be created in upload remote.")
   execute_process(COMMAND ${GIT_EXECUTABLE} checkout -b ${current_git_branch}
                   WORKING_DIRECTORY ${clone_dir}
   )
   execute_process(COMMAND ${GIT_EXECUTABLE} push -u origin ${current_git_branch}
                   WORKING_DIRECTORY ${clone_dir}
   )
endif()
