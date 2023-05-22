# repo_name is unique to the project
set(repo_name "libtk205")
set(upload_repo "github.com/open205/${repo_name}")
set(authenticated_repo "https://${PA_TOKEN}:x-oauth-basic@${upload_repo}") # PA_TOKEN is set by GitHub Actions
set(clone_dir "${PROJECT_SOURCE_DIR}/${repo_name}")

# Collect relevant info from toolkit-205:
execute_process(COMMAND ${GIT_EXECUTABLE} log -1 --pretty=%B
                WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
                OUTPUT_VARIABLE last_commit_msg
                OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Last commit message on local branch was \"${last_commit_msg}\"")

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
# git commit
execute_process(COMMAND ${GIT_EXECUTABLE} commit -m "\"${last_commit_msg}\""
                WORKING_DIRECTORY ${clone_dir}
)
# git push
execute_process(COMMAND ${GIT_EXECUTABLE} push
                WORKING_DIRECTORY ${clone_dir}
)
