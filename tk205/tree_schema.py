import os
import json
import posixpath
import jsonschema
from .util import create_grid_set

class TreeSchema:
    def __init__(self, schema_path):
        with open(schema_path, "r") as schema_file:
            uri_path = os.path.abspath(os.path.dirname(schema_path))
            if os.sep != posixpath.sep:
                uri_path = posixpath.sep + uri_path

            resolver = jsonschema.RefResolver(f'file://{uri_path}/', schema_path)

            self.validator = jsonschema.Draft7Validator(json.load(schema_file), resolver=resolver)


    def resolve(self, node, step_in=True):
        if '$ref' in node:
            resolution = self.resolve_ref(node['$ref'])
            # # If this node is a reference to a nested representation, append the required RS_ID
            # if 'RS' in node:
            #     resolution['RS'] = node['RS']
        else:
            resolution = node

        if step_in and 'properties' in resolution:
            return resolution['properties']
        else:
            return resolution

    def resolve_ref(self, ref):
        return '$ref:TBD'
        # scope, resolution = self.validator.resolver.resolve(ref)
        # self.validator.resolver.push_scope(scope)
        # return resolution

    def get_schema(self):
        return self.validator.schema

    def trace_lineage(self, node, lineage):
        '''
        Search through lineage for the schema node one generation at a time.

        node: node to trace into
        lineage: remaining lineage to trace
        '''
        print('trace_lineage; lineage =', lineage)
        #print('trace_lineage; node =', node)
        if not len(lineage): # i.e. []
            print('Root level; returning whole schema.')
            next_node = self.validator.schema
            return next_node

        for item in node:
            if lineage[0] == item:
                if len(lineage) == 1:
                    # This is the last node
                    last_node = self.resolve(node[item],False) # get the value associated with key:node
                    return last_node
                else:
                    # Keep digging

                    next_node = self.resolve(node[item],False)
                    # if 'items' in next_node:
                    #     next_node = self.resolve(next_node['items'])
                    return self.trace_lineage(next_node,lineage[1:])

        raise KeyError(f"'{lineage[0]}' not found in schema.")

    def get_schema_node(self, lineage):
        schema = self.validator.schema
        try:
            return self.trace_lineage(schema, lineage)
        except KeyError as ke:
            print('KeyError',ke)
            return None

    def get_grid_variable_order(self, lineage, grid_vars):
        '''
        Get the order of grid variables.

        TODO: Don't know if we can always rely on jsonschema always preserving order
        '''
        if lineage[-1] != 'grid_variables':
            raise Exception(f"{lineage[-1]} is not a 'grid_variables' data group.")
        parent_schema_node = self.get_schema_node(lineage[:-1], [None]*(len(lineage) - 1))
        if 'oneOf' in parent_schema_node:
            # Alternate performance maps allowed. Make sure we get the right one
            for option in parent_schema_node['oneOf']:
                option = self.resolve(option)
                for var in grid_vars:
                    if var not in option['grid_variables']['properties']:
                        schema_node = None
                        break
                    else:
                        schema_node = option['grid_variables']['properties']
                if schema_node:
                    break
        else:
            schema_node = self.get_schema_node(lineage,[None]*len(lineage))['properties']
        order = []

        if not schema_node:
            raise Exception(f"Unable to find schema for grid variables: {grid_vars}")

        for item in schema_node:
            order.append(item)
        return order

    def create_grid_set(self, grid_var_content, lineage):
        order = self.get_grid_variable_order(lineage,[x for x in grid_var_content])
        return create_grid_set(grid_var_content, order)
