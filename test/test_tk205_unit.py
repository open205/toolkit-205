import tk205
import os

'''
Unit tests
'''

def test_resolve_ref():
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))

    node = schema.resolve_ref("ASHRAE205.schema.json#/definitions/ASHRAE205")
    assert('title' not in node)

def test_get_schema_node():
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))

    # Node in external reference
    node = schema.get_schema_node(['RS_instance','description','product_information','compressor_type'])
    assert('enum' in node)

    # Node in internal reference
    node = schema.get_schema_node(['RS_instance',  'description', 'product_information', 'impeller_type'])
    assert('enum' in node)

    # Node in nested RS
    node = schema.get_schema_node(['RS_instance', 'performance', 'fan_representation', 'RS_instance', 'description', 'product_information', 'impeller_type'])
    assert('enum' in node)

    # Array node
    node = schema.get_schema_node(['RS_instance','performance','evaporator_liquid_type','liquid_components'])
    assert('items' in node)

    # Node in array
    node = schema.get_schema_node(['RS_instance','performance','evaporator_liquid_type','liquid_components','liquid_constituent'])
    assert('enum' in node)

    # Ambiguous node (without defined options, get_schema_node will return the first match it finds)
    node = schema.get_schema_node(['RS_instance','performance','performance_map_cooling','grid_variables'])
    node2 = schema.get_schema_node(['RS_instance','performance','performance_map_cooling','grid_variables'],[3, None, None, None])
    assert(node != node2)

    # Root node
    node = schema.get_schema_node([])
    assert('required' in node)

    # Root node of nested RS
    node = schema.get_schema_node(['RS_instance','performance','fan_representation'],[1,None,None])
    assert('ASHRAE 205' not in node['description'])

def test_get_representation_node_and_rs_selections():
    rep = tk205.load('schema-205/examples/RS0002/RS0002SimpleExampleFile.a205.json')
    node, rs_selections = tk205.util.get_representation_node_and_rs_selections(rep, ['RS_instance','performance','DX_system_representation','RS_instance','performance','performance_map_cooling','grid_variables'])
    assert(len(node) == 6)
    assert(rs_selections[0] == tk205.util.get_rs_index('RS0002'))
    assert(rs_selections[3] == tk205.util.get_rs_index('RS0004'))

def test_create_grid_set():
    rep = tk205.load('schema-205/examples/RS0004/RS0004SimpleExampleFile.a205.json')
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))
    grid_set = schema.create_grid_set(rep, ['RS_instance','performance','performance_map_cooling','grid_variables'])
    table_length = 1
    grid_vars = rep['RS_instance']['performance']['performance_map_cooling']['grid_variables']
    for var in grid_vars:
        table_length *= len(grid_vars[var])

    for var in grid_vars:
        assert(table_length == len(grid_set[var]))

def test_get_grid_variable_order():
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))

    # Typical case
    grid_vars_names = ['outdoor_coil_entering_dry_bulb_temperature','indoor_coil_entering_relative_humidity', 'indoor_coil_entering_dry_bulb_temperature', 'indoor_coil_air_mass_flow_rate', 'compressor_sequence_number', 'ambient_absolute_air_pressure']
    lineage = ['RS_instance','performance','performance_map_cooling','grid_variables']
    rs_selections = [None]*len(lineage)
    rs_selections[0] = tk205.util.get_rs_index('RS0004')
    order = schema.get_grid_variable_order(rs_selections,lineage,grid_vars_names)
    assert(order == grid_vars_names)

    # "oneOf" case 1
    grid_vars_names = ['volumetric_air_flow_rate','static_pressure_difference']
    lineage = ['RS_instance','performance','performance_map','grid_variables']
    rs_selections = [None]*len(lineage)
    rs_selections[0] = tk205.util.get_rs_index('RS0003')
    order = schema.get_grid_variable_order(rs_selections,lineage,grid_vars_names)
    assert(order == grid_vars_names)

    # "oneOf" case 2
    grid_vars_names = ['speed_number','static_pressure_difference']
    lineage = ['RS_instance','performance','performance_map','grid_variables']
    rs_selections = [None]*len(lineage)
    rs_selections[0] = tk205.util.get_rs_index('RS0003')
    order = schema.get_grid_variable_order(rs_selections,lineage,grid_vars_names)
    assert(order == grid_vars_names)

def test_process_grid_set():
    rep = tk205.load('schema-205/examples/RS0004/RS0004SimpleExampleFile.a205.json')
    grid_vars = rep['RS_instance']['performance']['performance_map_cooling']['grid_variables']
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))
    grid_set = schema.create_grid_set(rep, ['RS_instance','performance','performance_map_cooling','grid_variables'])
    grid_vars2 = tk205.util.process_grid_set(grid_set)
    assert(grid_vars == grid_vars2)

def test_get_schema_rs_title():
    schema = tk205.A205Schema(os.path.join(os.path.dirname(__file__),'..','schema-205',"schema","ASHRAE205.schema.json"))

    title = schema.get_rs_title('RS0001')
    assert(title == "Liquid-Cooled Chiller")

def test_objects_near_equal():
    # Numbers
    assert(tk205.util.objects_near_equal(3.0,3.0001,abs_tol=0.01))
    assert(not tk205.util.objects_near_equal(3.0,3.0001,abs_tol=0.0000001))

    # Lists
    assert(tk205.util.objects_near_equal([3.0],[3.0001],abs_tol=0.01))

    # Dictionary
    assert(tk205.util.objects_near_equal({"this":[3.0]},{"this":[3.0001]},abs_tol=0.01))
    assert(not tk205.util.objects_near_equal({"this":[3.0]},{"not_this":[3.0001]},abs_tol=0.01))
