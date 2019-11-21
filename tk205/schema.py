import os
import json
import posixpath
import jsonschema
from .util import create_grid_set

class A205Schema:
    def __init__(self, schema_path):
        with open(schema_path, "r") as schema_file:
            uri_path = os.path.abspath(os.path.dirname(schema_path))
            if os.sep != posixpath.sep:
                uri_path = posixpath.sep + uri_path

            resolver = jsonschema.RefResolver(f'file://{uri_path}/', schema_path)

            self.validator = jsonschema.Draft7Validator(json.load(schema_file), resolver=resolver)

    def validate(self, instance):
        errors = sorted(self.validator.iter_errors(instance), key=lambda e: e.path)
        for error in errors:
            for suberror in sorted(error.context, key=lambda e: e.schema_path):
                print(list(suberror.schema_path), suberror.message, sep=", ")
        if len(errors) == 0:
            print(f"Validation Successful for {instance['ASHRAE205']['description']}")
        else:
            raise Exception(f"Validation failed.")

    def resolve(self, node, step_in=True):
        if '$ref' in node:
            resolution = self.resolve_ref(node['$ref'])
            # If this node is a reference to a nested representation, append the required RS_ID
            if 'RS' in node:
                resolution['RS'] = node['RS']
        else:
            resolution = node

        if step_in and 'properties' in resolution:
            return resolution['properties']
        else:
            return resolution

    def resolve_ref(self, ref):
        scope, resolution = self.validator.resolver.resolve(ref)
        self.validator.resolver.push_scope(scope)
        return resolution

    def get_schema(self):
        return self.validator.schema

    def trace_lineage(self, node, lineage):
        for item in node:
            if lineage[0] == item:
                if len(lineage) == 1:
                    # This is the last node
                    return self.resolve(node[item],False)
                else:
                    # Keep digging

                    if 'oneOf' in node[item]:
                        # Search in all options
                        for option in node[item]['oneOf']:
                            option = self.resolve(option)
                            if lineage[1] in option:
                                try:
                                    return self.trace_lineage(option,lineage[1:])
                                except KeyError:
                                    # Not in this option try the next one
                                    # TODO: Handle this better (custom exception type)
                                    pass
                        raise KeyError(f"'{lineage[1]}' not found in schema.")

                    next_node = self.resolve(node[item])
                    if 'items' in next_node:
                        next_node = self.resolve(next_node['items'])
                    return self.trace_lineage(next_node,lineage[1:])

        raise KeyError(f"'{lineage[0]}' not found in schema.")

    def get_schema_node(self, lineage):
        schema = self.validator.schema['properties']
        try:
            return self.trace_lineage(schema, lineage)
        except KeyError:
            return None

    def get_schema_version(self):
        return self.validator.schema["version"]

    def get_rs_title(self, rs):
        return self.resolve_ref(f'{rs}.schema.json#/title')

    def get_grid_variable_order(self, lineage, grid_vars):
        '''
        Get the order of grid variables.

        TODO: Don't know if we can always rely on jsonschema always preserving order
        '''
        if lineage[-1] != 'grid_variables':
            raise Exception(f"{lineage[-1]} is not a 'grid_variables' data group.")
        parent_schema_node = self.get_schema_node(lineage[:-1])
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
            schema_node = self.get_schema_node(lineage)['properties']
        order = []

        if not schema_node:
            raise Exception(f"Unable to find schema for grid variables: {grid_vars}")

        for item in schema_node:
            order.append(item)
        return order

    def create_grid_set(self, grid_var_content, lineage):
        order = self.get_grid_variable_order(lineage,[x for x in grid_var_content])
        return create_grid_set(grid_var_content, order)
