project("Toolkit-205")

cmake_minimum_required(VERSION 2.8.2)

add_subdirectory(vendor)

set(RSs "0001" "0002" "0003")

set(languages "cpp" "python")

# Generate language interfaces
foreach(language ${languages})

  add_custom_target("Front-${language}" ALL
    COMMAND flatc --${language} -o "${PROJECT_BINARY_DIR}/${language}" schema/Front.fbs
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    DEPENDS flatc
    SOURCES schema/Front.fbs
  )

  add_custom_target("ASHRAE205-${language}" ALL
    COMMAND flatc --${language} -o "${PROJECT_BINARY_DIR}/${language}" schema/ASHRAE205.fbs
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    DEPENDS flatc
    SOURCES schema/ASHRAE205.fbs schema/Front.fbs
  )

  foreach(RS ${RSs})
    add_custom_target("${RS}-${language}" ALL
      COMMAND flatc --${language} -o "${PROJECT_BINARY_DIR}/${language}" schema/${RS}.fbs
      WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
      DEPENDS flatc
      SOURCES schema/${RS}.fbs schema/ASHRAE205.fbs
    )
  endforeach(RS)

endforeach(language)

# Generate schema
add_custom_target("binary-schema" ALL
  COMMAND flatc --binary --schema -o "${PROJECT_BINARY_DIR}/schema" --raw-binary "schema/ASHRAE205.fbs"
  WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
  DEPENDS flatc
  SOURCES schema/ASHRAE205.fbs
)

add_custom_target("json-schema" ALL
  COMMAND flatc --json --strict-json -o "${PROJECT_BINARY_DIR}/schema" --raw-binary vendor/FlatBuffers/reflection/reflection.fbs -- "${PROJECT_BINARY_DIR}/schema/ASHRAE205.bfbs"
  WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
  DEPENDS flatc "binary-schema"
)

include(ctest)

add_subdirectory(examples)
