import tk205
from tk205.file_io import set_dir
import os
import pytest

build_dir = set_dir("build")

test_dir = set_dir(os.path.join(build_dir,"test"))

examples_dir = set_dir(os.path.join(test_dir,"examples"))

cbor_dir = set_dir(os.path.join(examples_dir,"cbor"))

xlsx_dir = set_dir(os.path.join(examples_dir,"xlsx"))

json_dir = set_dir(os.path.join(examples_dir,"json"))

yaml_dir = set_dir(os.path.join(examples_dir,"yaml"))

templates_dir = set_dir(os.path.join(test_dir,"templates"))

json_source_dir = os.path.join("schema-205","examples")

'''
Process tests
'''

def test_json_validation():
    tk205.validate_directory(json_source_dir)

def test_bad_examples_validation():
    example_dir = 'test/bad-examples'
    for example in os.listdir(example_dir):
        with pytest.raises(Exception):
            tk205.validate(os.path.join(example_dir,example))

def test_json_to_cbor_translation():
    tk205.translate_directory(json_source_dir, cbor_dir)

def test_cbor_validation():
    tk205.validate_directory(cbor_dir)

def test_json_to_yaml_translation():
    tk205.translate_directory(json_source_dir, yaml_dir)

def test_yaml_validation():
    tk205.validate_directory(yaml_dir)

def test_json_to_xlsx_translation():
    tk205.translate_directory(json_source_dir, xlsx_dir)

def test_xlsx_validation():
    tk205.validate_directory(xlsx_dir)

def test_xlsx_to_json_translation():
    tk205.translate_directory(xlsx_dir, json_dir)

def test_json_round_trip():
    for rs_dir in os.listdir(json_source_dir):
        origin_dir = os.path.join(json_source_dir,rs_dir)
        product_dir = os.path.join(json_dir,rs_dir)
        for example in os.listdir(origin_dir):
            origin_path = os.path.join(origin_dir,example)
            product_path = os.path.join(product_dir,example)
            assert(tk205.load(origin_path) == tk205.load(product_path))

def test_xlsx_template_creation():
    output_dir = templates_dir
    tk205.file_io.clear_directory(output_dir)
    rss = tk205.load('config/templates.json')
    for rs, templates in rss.items():
        for template in templates:
            file_name_components = [rs]
            if template["file-name-suffix"]:
                file_name_components.append(template["file-name-suffix"])
            file_name_components.append("template.a205.xlsx")
            file_name = '-'.join(file_name_components)
            tk205.template(rs,os.path.join(output_dir,file_name), **template["keywords"])

