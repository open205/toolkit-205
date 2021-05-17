# Imports
from .file_io import translate, translate_directory_recursive, translate_directory, load
from .xlsx import template, generate_templates
from schema205 import A205Schema
from .util import objects_near_equal
import os

def validate(file_path):
    contents = load(file_path)
    a205schema = A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205','build','schema',f"{contents['metadata']['schema']}.schema.json"))
    a205schema.validate(contents)
