import os
import json
import cbor2
import yaml
from .xlsx import template, A205XLSXTree

def get_extension(file):
    return os.path.splitext(file)[1]

def load(input_file_path):
    ext = get_extension(input_file_path).lower()
    if (ext == '.json'):
        with open(input_file_path, 'r') as input_file:
            return json.load(input_file)
    elif (ext == '.cbor'):
        with open(input_file_path, 'rb') as input_file:
            return cbor2.load(input_file)
    elif (ext == '.xlsx'):
        tree = A205XLSXTree()
        return tree.load_workbook(input_file_path).get_content()
    elif (ext == '.yaml') or (ext == '.yml'):
        return yaml.load(input_file_path, Loader=yaml.FullLoader)
    else:
        raise Exception(f"Unsupported input \"{ext}\".")

def dump(content, output_file_path):
    ext = get_extension(output_file_path).lower()
    if (ext == '.json'):
        with open(output_file_path,'w') as output_file:
            json.dump(content, output_file, indent=4)
    elif (ext == '.cbor'):
        with open(output_file_path,'wb') as output_file:
            cbor2.dump(content, output_file)
    elif (ext == '.xlsx'):
        tree = A205XLSXTree()
        tree.load(content)
        tree.save(output_file_path)
    elif (ext == '.yaml') or (ext == '.yml'):
        with open(output_file_path, 'w') as out_file:
            yaml.dump(content, out_file)

    else:
        raise Exception(f"Unsupported output \"{ext}\".")

