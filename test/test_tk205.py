import tk205
import os
import pytest

def test_json_examples_validation():
    example_dir = 'examples/json'
    for example in os.listdir(example_dir):
        tk205.validate(os.path.join(example_dir,example))


def test_bad_examples_validation():
    example_dir = 'test/bad-examples'
    for example in os.listdir(example_dir):
        with pytest.raises(Exception):
            tk205.validate(os.path.join(example_dir,example))

def test_example_translation():
    example_dir = 'examples/json'
    for example in os.listdir(example_dir):
        in_path = os.path.join(example_dir,example)
        basename = os.path.basename(in_path)
        filename = os.path.splitext(basename)[0]
        out_path = os.path.join('examples/cbor',filename + '.cbor')
        tk205.translate(in_path,out_path)

def test_cbor_examples_validation():
    example_dir = 'examples/cbor'
    for example in os.listdir(example_dir):
        tk205.validate(os.path.join(example_dir,example))

def test_xlsx_template_creation():
    tk205.template('RS0001','output')
