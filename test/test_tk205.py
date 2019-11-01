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

def test_json_validation():
    example_dir = 'schema-205/examples/json'
    for example in os.listdir(example_dir):
        tk205.validate(os.path.join(example_dir,example))


def test_bad_examples_validation():
    example_dir = 'test/bad-examples'
    for example in os.listdir(example_dir):
        with pytest.raises(Exception):
            tk205.validate(os.path.join(example_dir,example))

def test_json_to_cbor_translation():
    example_dir = 'schema-205/examples/json'
    for example in os.listdir(example_dir):
        in_path = os.path.join(example_dir,example)
        basename = os.path.basename(in_path)
        filename = os.path.splitext(basename)[0]
        out_path = os.path.join('build/examples/cbor',filename + '.cbor')
        tk205.translate(in_path,out_path)

def test_cbor_validation():
    example_dir = 'build/examples/cbor'
    for example in os.listdir(example_dir):
        tk205.validate(os.path.join(example_dir,example))

def test_json_to_xlsx_translation():
    example_dir = 'schema-205/examples/json'
    for example in os.listdir(example_dir):
        in_path = os.path.join(example_dir,example)
        basename = os.path.basename(in_path)
        filename = os.path.splitext(basename)[0]
        out_path = os.path.join('build/examples/xlsx',filename + '.xlsx')
        tk205.translate(in_path,out_path)

def test_xlsx_to_json_translation():
    example_dir = 'build/examples/xlsx'
    for example in os.listdir(example_dir):
        in_path = os.path.join(example_dir,example)
        basename = os.path.basename(in_path)
        filename = os.path.splitext(basename)[0]
        out_path = os.path.join('build/examples/json',filename + '.json')
        tk205.translate(in_path,out_path)

#def test_xlsx_validation():
#    example_dir = 'build/examples/xlsx'
#    for example in os.listdir(example_dir):
#        tk205.validate(os.path.join(example_dir,example))

def test_xlsx_template_creation():
    rss = ['RS0001','RS0002','RS0003']
    for rs in rss:
        tk205.template(rs,'build/templates')

def test_json_to_tree_to_xlsx_translation():
    pass

def test_xlsx_to_tree_to_json_translation():
    pass

def test_json_to_tree_to_json_translation():
    pass

def test_xlsx_to_tree_to_xlsx_translation():
    pass