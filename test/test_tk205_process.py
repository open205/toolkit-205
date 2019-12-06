import tk205
import os
import pytest

if not os.path.isdir('build'):
    os.mkdir('build')

if not os.path.isdir('build/examples'):
    os.mkdir('build/examples')

if not os.path.isdir('build/examples/cbor'):
    os.mkdir('build/examples/cbor')

if not os.path.isdir('build/examples/xlsx'):
    os.mkdir('build/examples/xlsx')

if not os.path.isdir('build/examples/json'):
    os.mkdir('build/examples/json')

if not os.path.isdir('build/templates'):
    os.mkdir('build/templates')

'''
Process tests
'''

def test_json_validation():
    tk205.validate_directory('schema-205/examples/json')

def test_bad_examples_validation():
    example_dir = 'test/bad-examples'
    for example in os.listdir(example_dir):
        with pytest.raises(Exception):
            tk205.validate(os.path.join(example_dir,example))

def test_json_to_cbor_translation():
    tk205.translate_directory('schema-205/examples/json', 'build/examples/cbor')

def test_cbor_validation():
    tk205.validate_directory('build/examples/cbor')

def test_json_to_xlsx_translation():
    tk205.translate_directory('schema-205/examples/json', 'build/examples/xlsx')

def test_xlsx_to_json_translation():
    tk205.translate_directory('build/examples/xlsx', 'build/examples/json')

def test_json_round_trip():
    origin_dir = 'schema-205/examples/json'
    product_dir = 'build/examples/json'
    for example in (os.listdir(origin_dir)):
        origin_path = os.path.join(origin_dir,example)
        product_path = os.path.join(product_dir,example)
        assert(tk205.load(origin_path) == tk205.load(product_path))

def test_xlsx_validation():
    tk205.validate_directory('build/examples/xlsx')

def test_xlsx_template_creation():
    output_dir = 'build/templates'
    tk205.file_io.clear_directory(output_dir)
    rss = [
            ('RS0001', {}, None),
            ('RS0002', {'performance_map_type': 'DISCRETE'}, 'discrete-fan'),
            ('RS0002', {'performance_map_type': 'CONTINUOUS'}, 'continuous-fan'),
            ('RS0003', {'performance_map_type': 'DISCRETE'}, 'discrete'),
            ('RS0003', {'performance_map_type': 'CONTINUOUS'}, 'continuous'),
        ]
    for rs in rss:
        file_name_components = [rs[0]]
        if rs[2]:
            file_name_components.append(rs[2])
        file_name_components.append("template.a205.xlsx")
        file_name = '-'.join(file_name_components)
        tk205.template(rs[0],os.path.join(output_dir,file_name), **rs[1])

