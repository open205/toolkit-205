# repo_name is unique to the project
set(repo_name "libtk205")
set(upload_repo "github.com/open205/${repo_name}")
set(authenticated_repo "https://${PA_TOKEN}:x-oauth-basic@${upload_repo}") # PA_TOKEN is set by GitHub Actions
set(clone_dir "${PROJECT_SOURCE_DIR}/${repo_name}")

find_package(Git QUIET)

if(NOT GIT_FOUND)
   message(FATAL_ERROR "git not found!")
endif()

message(STATUS "Working directory: ${PROJECT_SOURCE_DIR}.")
# Collect relevant info from toolkit-205:
execute_process(COMMAND ${GIT_EXECUTABLE} log -1 --pretty=%B
                WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
                OUTPUT_VARIABLE last_commit_msg
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Last commit message on ${PROJECT_NAME} branch was \"${last_commit_msg}\"")

message(STATUS "Working directory: ${clone_dir}.")
# libtk205 remote side:
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
# git status (see if files changed)
execute_process(COMMAND ${GIT_EXECUTABLE} status
                WORKING_DIRECTORY ${clone_dir}
)
# git commit
execute_process(COMMAND ${GIT_EXECUTABLE} commit -m "\"${last_commit_msg}\""
                WORKING_DIRECTORY ${clone_dir}
)
# git push
execute_process(COMMAND ${GIT_EXECUTABLE} push ${authenticated_repo}
                WORKING_DIRECTORY ${clone_dir}
)
