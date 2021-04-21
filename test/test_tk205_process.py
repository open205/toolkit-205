import tk205
from tk205.file_io import set_dir
import os
import pytest

BUILD_PATH = set_dir("build")

EXAMPLES_OUTPUT_PATH = set_dir(os.path.join(BUILD_PATH,"examples"))

CBOR_OUTPUT_PATH = set_dir(os.path.join(EXAMPLES_OUTPUT_PATH,"cbor"))

XLSX_OUTPUT_PATH = set_dir(os.path.join(EXAMPLES_OUTPUT_PATH,"xlsx"))

JSON_OUTPUT_PATH = set_dir(os.path.join(EXAMPLES_OUTPUT_PATH,"json"))

YAML_OUTPUT_PATH = set_dir(os.path.join(EXAMPLES_OUTPUT_PATH,"yaml"))

EXAMPLES_SOURCE_PATH = os.path.join("schema-205","examples")

'''
Process tests
'''

IGNORED_FILE_PATTERNS = [".DS_Store"]

def collect_examples(example_dir):
    paths = []
    names = []

    for example in sorted(os.listdir(example_dir)):
        example_path = os.path.join(example_dir,example)
        if os.path.isdir(example_path):
            paths += collect_examples(example_path)[0]
            names += collect_examples(example_path)[1]
        else:
            if all(pattern not in example for pattern in IGNORED_FILE_PATTERNS):
                paths.append(os.path.join(example_dir,example))
                names.append(example)
    return paths, names

paths, names = collect_examples(CBOR_OUTPUT_PATH)

@pytest.mark.parametrize("example",paths, ids=names)
def test_validate_cbor(example):
    tk205.validate(example)

paths, names = collect_examples(YAML_OUTPUT_PATH)

@pytest.mark.parametrize("example",paths, ids=names)
def test_validate_yaml(example):
    tk205.validate(example)

paths, names = collect_examples(XLSX_OUTPUT_PATH)

@pytest.mark.parametrize("example",paths, ids=names)
def test_validate_xlsx(example):
    tk205.validate(example)

origin_paths, origin_names = collect_examples(EXAMPLES_SOURCE_PATH)
product_paths, product_names = collect_examples(JSON_OUTPUT_PATH)

paths = [(origin_paths[i], product_paths[i]) for i in range(len(origin_paths))]
@pytest.mark.parametrize("origin, product",paths, ids=origin_names)
def test_json_round_trip(origin, product):
    assert(tk205.util.objects_near_equal(tk205.load(origin), tk205.load(product)))