import os, shutil
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
        with open(input_file_path, 'r') as input_file:
            return yaml.load(input_file, Loader=yaml.FullLoader)
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
            yaml.dump(content, out_file, sort_keys=False)

    else:
        raise Exception(f"Unsupported output \"{ext}\".")

def clear_directory(directory_path):
    '''
    Delete contents of a directory

    Based on: https://stackoverflow.com/a/185941/1344457
    '''
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

