import json
import jsonschema
import os
import posixpath

abs_path = os.path.abspath(os.path.dirname(__file__))

if os.sep != posixpath.sep:
    abs_path = posixpath.sep + abs_path

resolver = jsonschema.RefResolver(f'file://{abs_path}/', None)
with open("ASHRAE205.schema.json", "r") as read_file:
    schema = json.load(read_file)
    with open("../examples/json/RS0001ExampleFile.json", "r") as test_file:
        file = json.load(test_file)
        jsonschema.validate(instance=file, schema=schema, resolver=resolver)
