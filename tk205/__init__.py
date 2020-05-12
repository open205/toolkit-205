# Imports
from .file_io import *
from .schema import A205Schema
import os

def validate(file):
    a205schema = A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205','schema',"ASHRAE205.schema.json"))
    a205schema.validate(load(file))

def translate(input, output):
    dump(load(input),output)

def translate_directory_recursive(source_dir, output_dir, output_extension):
    for source in os.listdir(source_dir):
        source_path = os.path.join(source_dir, source)
        if os.path.isdir(source_path):
            output_dir_path = os.path.join(output_dir, source)
            os.mkdir(output_dir_path)
            translate_directory_recursive(source_path, output_dir_path, output_extension)
        else:
            if '~$' not in source:  # Ignore temporary Excel files
                base_name = os.path.basename(source_path)
                file_name = os.path.splitext(base_name)[0]
                output_path = os.path.join(output_dir,file_name + output_extension)
                translate(source_path, output_path)

def translate_directory(source_dir, output_dir, clear=True):
    output_extension = '.' + os.path.split(output_dir)[-1]
    if clear:
        clear_directory(output_dir)
    translate_directory_recursive(source_dir, output_dir, output_extension)

def validate_directory(example_dir):
    errors = []
    for example in os.listdir(example_dir):
        example_path = os.path.join(example_dir,example)
        if os.path.isdir(example_path):
            errors += validate_directory(example_path)
        else:
            if '~$' not in example:  # Ignore temporary Excel files
                try:
                    validate(os.path.join(example_dir,example))
                except Exception as e: # Change to tk205 Exception
                    errors.append(e)
    if len(errors) > 0:
        error_str = '\n\n'.join([f"{e}" for e in errors])
        raise Exception(f"{error_str}")
    return errors
