import tk205
import os

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
    rep = tk205.load('schema-205/examples/RS0004/RS0004SimpleExampleFile.a205.json')
    grid_vars = rep['ASHRAE205']['RS_instance']['RS0004']['performance']['performance_map_cooling']['grid_variables']
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))
    grid_set = schema.create_grid_set(grid_vars, ['ASHRAE205','RS_instance','RS0004','performance','performance_map_cooling','grid_variables'])
    table_length = 1
    for var in grid_vars:
        table_length *= len(grid_vars[var])

    for var in grid_vars:
        assert(table_length == len(grid_set[var]))

def test_get_grid_variable_order():
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))

    # Typical case
    grid_vars_names = ['outdoor_coil_entering_dry_bulb_temperature','indoor_coil_entering_relative_humidity', 'indoor_coil_entering_dry_bulb_temperature', 'indoor_coil_air_mass_flow_rate', 'compressor_sequence_number', 'ambient_absolute_air_pressure']
    order = schema.get_grid_variable_order(['ASHRAE205','RS_instance','RS0004','performance','performance_map_cooling','grid_variables'],grid_vars_names)
    assert(order == grid_vars_names)

    # "oneOf" case 1
    grid_vars_names = ['volumetric_air_flow_rate','static_pressure_difference']
    order = schema.get_grid_variable_order(['ASHRAE205','RS_instance','RS0003','performance','performance_map','grid_variables'], grid_vars_names)
    assert(order == grid_vars_names)

    # "oneOf" case 2
    grid_vars_names = ['speed_number','static_pressure_difference']
    order = schema.get_grid_variable_order(['ASHRAE205','RS_instance','RS0003','performance','performance_map','grid_variables'], grid_vars_names)
    assert(order == grid_vars_names)

def test_process_grid_set():
    rep = tk205.load('schema-205/examples/RS0004/RS0004SimpleExampleFile.a205.json')
    grid_vars = rep['ASHRAE205']['RS_instance']['RS0004']['performance']['performance_map_cooling']['grid_variables']
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))
    grid_set = schema.create_grid_set(grid_vars, ['ASHRAE205','RS_instance','RS0004','performance','performance_map_cooling','grid_variables'])
    grid_vars2 = tk205.util.process_grid_set(grid_set)
    assert(grid_vars == grid_vars2)

def test_get_schema_rs_title():
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))

    title = schema.get_rs_title('RS0001')
    assert(title == "Liquid-Cooled Chiller")
