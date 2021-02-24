# Copy headers, for classes that must be distributed (not factories), into the project
# include directory

file(GLOB autogenerated_factories "${PROJECT_SOURCE_DIR}/../schema-205/build/include/*factory.h")
file(GLOB autogenerated_headers "${PROJECT_SOURCE_DIR}/../schema-205/build/include/*.h")
foreach(filename ${autogenerated_factories})
    list(REMOVE_ITEM autogenerated_headers ${filename})
endforeach(filename)

foreach(filename ${autogenerated_headers})
    configure_file(${filename} ${PROJECT_SOURCE_DIR}/include COPYONLY)
endforeach(filename)
