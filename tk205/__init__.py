# Imports
from .util import *
import json
import jsonschema
import os
import posixpath

def validate(file):
    abs_path = uri_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','schema'))

    if os.sep != posixpath.sep:
        uri_path = posixpath.sep + uri_path

    resolver = jsonschema.RefResolver(f'file://{uri_path}/', None)
    with open(os.path.join(abs_path,"..","schema","ASHRAE205.schema.json"), "r") as read_file:
        schema = json.load(read_file)
        with open(file, "r") as test_file:
            instance = json.load(test_file)
            validator = jsonschema.Draft7Validator(schema, resolver=resolver)
            errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
            for error in errors:
                for suberror in sorted(error.context, key=lambda e: e.schema_path):
                    print(list(suberror.schema_path), suberror.message, sep=", ")
            if len(errors) == 0:
                print(f"Validation Successful for {instance['ASHRAE205']['description']}")