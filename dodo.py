import os
import tk205
from doit.tools import create_folder

BUILD_PATH = "build"
SCHEMA_SOURCE_PATH = os.path.join("schema-205","schema-source")
JSON_SCHEMA_PATH = os.path.join("schema-205","build","schema")
EXAMPLES_SOURCE_PATH = os.path.join("schema-205","examples")
EXAMPLES_OUTPUT_PATH = os.path.join(BUILD_PATH,"examples")
TEMPLATE_OUTPUT_PATH = os.path.join(BUILD_PATH,"templates")
TEMPLATE_CONFIG = os.path.join('config','templates.json')
LIB_BUILD_PATH = os.path.join(BUILD_PATH,"libtk205")

def task_build_schema():
  '''Build the schema'''
  return {
    'actions': ['doit -d schema-205']
  }

def collect_schema_files():
  file_list = []
  for file_name in sorted(os.listdir(SCHEMA_SOURCE_PATH)):
    if '.schema.yaml' in file_name:
      file_name_root = os.path.splitext(os.path.splitext(file_name)[0])[0]
      file_list.append(os.path.join(JSON_SCHEMA_PATH,f'{file_name_root}.schema.json'))
  return file_list

def collect_examples(example_dir):
  file_paths = []

  for example in sorted(os.listdir(example_dir)):
    example_path = os.path.join(example_dir,example)
    if os.path.isdir(example_path):
      file_paths += collect_examples(example_path)
    else:
      file_paths.append(os.path.join(example_dir,example))
  return file_paths

def collect_generated_examples(examples_source_dir, examples_output_dir, extension):
  file_paths = []

  for example in sorted(os.listdir(examples_source_dir)):
    example_source_path = os.path.join(examples_source_dir,example)
    example_output_path = os.path.join(examples_output_dir,example)
    if os.path.isdir(example_source_path):
      file_paths += collect_generated_examples(example_source_path, example_output_path, extension)
    else:
      base_name = os.path.basename(example)
      file_name = os.path.splitext(base_name)[0]
      file_paths.append(os.path.join(examples_output_dir,f'{file_name}.{extension}'))
  return file_paths

def collect_template_outputs(template_config):
  file_paths = []
  for rs, templates in template_config.items():
    for t in templates:
      file_name_components = [rs]
      if t["file-name-suffix"]:
        file_name_components.append(t["file-name-suffix"])
      file_name_components.append("template.a205.xlsx")
      file_name = '-'.join(file_name_components)
      file_paths.append(os.path.join(TEMPLATE_OUTPUT_PATH,file_name))
  return file_paths

source_examples = collect_examples(EXAMPLES_SOURCE_PATH)

CBOR_OUTPUT_PATH = os.path.join(EXAMPLES_OUTPUT_PATH,'cbor')

cbor_examples = collect_generated_examples(EXAMPLES_SOURCE_PATH, CBOR_OUTPUT_PATH, 'cbor')

def task_translate_to_cbor():
  '''Translate example files to CBOR'''
  return {
    'basename': 'cbor',
    'file_dep': source_examples,
    'targets': cbor_examples,
    'actions': [
      (create_folder, [CBOR_OUTPUT_PATH]),
      (tk205.translate_directory, [EXAMPLES_SOURCE_PATH, CBOR_OUTPUT_PATH])
      ],
    'clean': True
  }

YAML_OUTPUT_PATH = os.path.join(EXAMPLES_OUTPUT_PATH,'yaml')

yaml_examples = collect_generated_examples(EXAMPLES_SOURCE_PATH, YAML_OUTPUT_PATH, 'yaml')

def task_translate_to_yaml():
  '''Translate example files to YAML'''
  return {
    'basename': 'yaml',
    'file_dep': source_examples,
    'targets': yaml_examples,
    'actions': [
      (create_folder, [YAML_OUTPUT_PATH]),
      (tk205.translate_directory, [EXAMPLES_SOURCE_PATH, YAML_OUTPUT_PATH])
      ],
    'clean': True
  }

XLSX_OUTPUT_PATH = os.path.join(EXAMPLES_OUTPUT_PATH,'xlsx')

xlsx_examples = collect_generated_examples(EXAMPLES_SOURCE_PATH, XLSX_OUTPUT_PATH, 'xlsx')

def task_translate_to_xlsx():
  '''Translate example files to XLSX'''
  return {
    'basename': 'xlsx',
    'file_dep': source_examples + [os.path.join(TK205_SOURCE_PATH, 'xlsx.py')],
    'targets': xlsx_examples,
    'actions': [
      (create_folder, [XLSX_OUTPUT_PATH]),
      (tk205.translate_directory, [EXAMPLES_SOURCE_PATH, XLSX_OUTPUT_PATH])
      ],
    'clean': True
  }

JSON_OUTPUT_PATH = os.path.join(EXAMPLES_OUTPUT_PATH,'json')

json_examples = collect_generated_examples(EXAMPLES_SOURCE_PATH, JSON_OUTPUT_PATH, 'json')

def task_translate_to_json():
  '''Translate XLSX example files back to JSON'''
  return {
    'basename': 'json',
    'file_dep': xlsx_examples + [os.path.join(TK205_SOURCE_PATH, 'xlsx.py')],
    'targets': json_examples,
    'task_dep': ['xlsx'],
    'actions': [
      (create_folder, [JSON_OUTPUT_PATH]),
      (tk205.translate_directory, [XLSX_OUTPUT_PATH, JSON_OUTPUT_PATH])
      ],
    'clean': True
  }

template_config = tk205.load(TEMPLATE_CONFIG)
template_files = collect_template_outputs(template_config)

def task_templates():
  '''Create XLSX templates based on the schema'''
  return {
    'task_dep': ['build_schema'],
    'file_dep': [TEMPLATE_CONFIG] + collect_schema_files() + [os.path.join(TK205_SOURCE_PATH, 'xlsx.py')],
    'targets': template_files,
    'actions': [
      (create_folder, [TEMPLATE_OUTPUT_PATH]),
      (tk205.generate_templates, [TEMPLATE_OUTPUT_PATH, template_config])
      ],
    'clean': True
  }

def task_python_tests():
  '''Performs unit tests and example file validation tests'''
  return {
    'task_dep': ['build_schema','cbor','yaml','xlsx','json'],
    'file_dep': cbor_examples + yaml_examples + xlsx_examples + json_examples,
    'actions': [
      'pytest -v test',
      ]
  }

def task_libtk205():
  '''Build libtk205'''
  return {
    'task_dep': ['build_schema'],
    'actions': [
      (create_folder, [LIB_BUILD_PATH]),
      f'cmake -B {LIB_BUILD_PATH}',
      f'cmake --build {LIB_BUILD_PATH} --config Release'
      ],
  }

def task_libtk205_tests():
  '''Performs unit tests and example file validation tests'''
  return {
    'task_dep': ['libtk205'],
    'actions': [
      f'cd {LIB_BUILD_PATH} && ctest',
      ],
  }

def task_web():
  '''Generates the web contents for data.ashrae.org'''
  return {
    'task_dep': ['build_schema','cbor','yaml','xlsx','json', 'templates'],
    'file_dep': cbor_examples + yaml_examples + xlsx_examples + json_examples + template_files, # Add markdown content
    'actions': ['python web/web-content.py']
  }
