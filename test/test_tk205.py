import tk205
import os
import pytest
from tk205.util import create_grid_set, process_grid_set

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

def perform_translations(source_dir, output_dir):
    output_extension = '.' + os.path.split(output_dir)[-1]
    tk205.file_io.clear_directory(output_dir)
    for source in os.listdir(source_dir):
        if '~$' not in source:  # Ignore temporary Excel files
            source_path = os.path.join(source_dir,source)
            base_name = os.path.basename(source_path)
            file_name = os.path.splitext(base_name)[0]
            output_path = os.path.join(output_dir,file_name + output_extension)
            tk205.translate(source_path, output_path)

def perform_validations(example_dir):
    for example in os.listdir(example_dir):
        if '~$' not in example:  # Ignore temporary Excel files
            tk205.validate(os.path.join(example_dir,example))

def test_json_validation():
    perform_validations('schema-205/examples/json')

def test_bad_examples_validation():
    example_dir = 'test/bad-examples'
    for example in os.listdir(example_dir):
        with pytest.raises(Exception):
            tk205.validate(os.path.join(example_dir,example))

def test_json_to_cbor_translation():
    perform_translations('schema-205/examples/json', 'build/examples/cbor')

def test_cbor_validation():
    perform_validations('build/examples/cbor')

def test_json_to_xlsx_translation():
    perform_translations('schema-205/examples/json', 'build/examples/xlsx')

def test_xlsx_to_json_translation():
    perform_translations('build/examples/xlsx', 'build/examples/json')

def test_json_round_trip():
    origin_dir = 'schema-205/examples/json'
    product_dir = 'build/examples/json'
    for example in (os.listdir(origin_dir)):
        origin_path = os.path.join(origin_dir,example)
        product_path = os.path.join(product_dir,example)
        assert(tk205.load(origin_path) == tk205.load(product_path))

def test_xlsx_validation():
    perform_validations('build/examples/xlsx')

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

'''
Unit tests
'''

def test_get_schema_node():
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))

    # Node in external reference
    node = schema.get_schema_node(['ASHRAE205','RS_instance','RS0001','description','product_information','compressor_type'])
    assert('enum' in node)

    # Node in internal reference
    node = schema.get_schema_node(['ASHRAE205', 'RS_instance', 'RS0003', 'description', 'product_information', 'impeller_type'])
    assert('enum' in node)

    # Node in nested RS
    node = schema.get_schema_node(['ASHRAE205', 'RS_instance', 'RS0002', 'performance', 'fan_representation', 'ASHRAE205','RS_instance', 'RS0003', 'description', 'product_information', 'impeller_type'])
    assert('enum' in node)

    # Array node
    node = schema.get_schema_node(['ASHRAE205','RS_instance','RS0001','performance','evaporator_liquid_type','liquid_components'])
    assert('items' in node)

    # Node in array
    node = schema.get_schema_node(['ASHRAE205','RS_instance','RS0001','performance','evaporator_liquid_type','liquid_components','liquid_constituent'])
    assert('enum' in node)

def test_create_grid_set():
    rep = tk205.load('schema-205/examples/json/RS0002SimpleExampleFile.a205.json')
    grid_vars = rep['ASHRAE205']['RS_instance']['RS0002']['performance']['performance_map_cooling']['grid_variables']
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))
    grid_set = schema.create_grid_set(grid_vars, ['ASHRAE205','RS_instance','RS0002','performance','performance_map_cooling','grid_variables'])
    table_length = 1
    for var in grid_vars:
        table_length *= len(grid_vars[var])

    for var in grid_vars:
        assert(table_length == len(grid_set[var]))

def test_get_grid_variable_order():
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))

    # Typical case
    grid_vars_names = ['outdoor_coil_entering_dry_bulb_temperature','indoor_coil_entering_wet_bulb_temperature', 'indoor_coil_entering_dry_bulb_temperature', 'indoor_coil_volumetric_flow_ratio', 'compressor_sequence_number', 'ambient_absolute_air_pressure']
    order = schema.get_grid_variable_order(['ASHRAE205','RS_instance','RS0002','performance','performance_map_cooling','grid_variables'],grid_vars_names)
    assert(order == grid_vars_names)

    # "oneOf" case 1
    grid_vars_names = ['impeller_speed','static_pressure_difference']
    order = schema.get_grid_variable_order(['ASHRAE205','RS_instance','RS0003','performance','performance_map','grid_variables'], grid_vars_names)
    assert(order == grid_vars_names)

    # "oneOf" case 2
    grid_vars_names = ['speed_number','static_pressure_difference']
    order = schema.get_grid_variable_order(['ASHRAE205','RS_instance','RS0003','performance','performance_map','grid_variables'], grid_vars_names)
    assert(order == grid_vars_names)

def test_process_grid_set():
    rep = tk205.load('schema-205/examples/json/RS0002SimpleExampleFile.a205.json')
    grid_vars = rep['ASHRAE205']['RS_instance']['RS0002']['performance']['performance_map_cooling']['grid_variables']
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))
    grid_set = schema.create_grid_set(grid_vars, ['ASHRAE205','RS_instance','RS0002','performance','performance_map_cooling','grid_variables'])
    grid_vars2 = process_grid_set(grid_set)
    assert(grid_vars == grid_vars2)

def test_get_schema_rs_title():
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))

    title = schema.get_rs_title('RS0001')
    assert(title == "Liquid-Cooler Chillers")
