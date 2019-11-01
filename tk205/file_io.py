import os
import json
import cbor2
from .xlsx import template, A205XLSXTree

def get_extension(file):
    return os.path.splitext(file)[1]

def load(file):
    # todo check file exisits
    ext = get_extension(file).lower()
    if (ext == '.json'):
        with open(file, 'r') as input_file:
            return json.load(input_file)
    elif (ext == '.cbor'):
        with open(file, 'rb') as input_file:
            return cbor2.load(input_file)
    elif (ext == '.xlsx'):
        tree = A205XLSXTree()
        return tree.load_workbook(file).get_content()
    else:
        raise Exception(f"Unsupported input \"{ext}\".")

def dump(content, file):
    # todo check file exisits
    ext = get_extension(file).lower()
    if (ext == '.json'):
        with open(file,'w') as output_file:
            json.dump(content, output_file, indent=4)
    elif (ext == '.cbor'):
        with open(file,'wb') as output_file:
            cbor2.dump(content, output_file)
    elif (ext == '.xlsx'):
        tree = A205XLSXTree()
        tree.load(content)
        tree.save(file)
    else:
        raise Exception(f"Unsupported output \"{ext}\".")

