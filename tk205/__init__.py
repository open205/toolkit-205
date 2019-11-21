# Imports
from .file_io import *
from .schema import A205Schema
import os

def validate(file):
    a205schema = A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205','schema',"ASHRAE205.schema.json"))
    a205schema.validate(load(file))

def translate(input, output):
    dump(load(input),output)