# Imports
from .util import *
import json
import jsonschema
import os
import posixpath
import cbor2

def load(file):
    # todo check file exisits
    ext = get_extension(file)
    if (ext.lower() == '.json'):
        with open(file, 'r') as input_file:
            return json.load(input_file)
    if (ext.lower() in ['.a205','.cbor']):
        with open(file, 'rb') as input_file:
            return cbor2.load(input_file)
    else:
        # TODO unsupported input
        print(f"Unsupported input \"{ext}\".")
        assert(False)

def validate(file):
    abs_path = uri_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','schema-205','schema'))

    if os.sep != posixpath.sep:
        uri_path = posixpath.sep + uri_path

    resolver = jsonschema.RefResolver(f'file://{uri_path}/', None)
    with open(os.path.join(abs_path,"ASHRAE205.schema.json"), "r") as read_file:
        schema = json.load(read_file)
        instance = load(file)
        validator = jsonschema.Draft7Validator(schema, resolver=resolver)
        errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
        for error in errors:
            for suberror in sorted(error.context, key=lambda e: e.schema_path):
                print(list(suberror.schema_path), suberror.message, sep=", ")
        if len(errors) == 0:
            print(f"Validation Successful for {instance['ASHRAE205']['description']}")

def translate(input, output):
    with open(input,'r') as input_file:
        with open(output,'wb') as output_file:
            cbor2.dump(json.load(input_file),output_file)