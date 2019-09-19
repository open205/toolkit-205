import json
import jsonschema
import os

resolver = jsonschema.RefResolver('file://%s/' % os.path.abspath(os.path.dirname(__file__)), None)
with open("ASHRAE205.schema.json", "r") as read_file:
    schema = json.load(read_file)
    with open("RS0001ExampleFile.json", "r") as test_file:
        file = json.load(test_file)
        jsonschema.validate(instance=file, schema=schema, resolver=resolver)