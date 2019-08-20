import json
from jsonschema import validate

with open("ASHRAE205.schema.json", "r") as read_file:
    schema = json.load(read_file)
    with open("RS0001ExampleFile.json", "r") as test_file:
        file = json.load(test_file)
        validate(instance=file, schema=schema)
