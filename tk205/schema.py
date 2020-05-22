import os
import json
import posixpath
import jsonschema
from .util import create_grid_set
from .util import get_representation_node_and_rs_selections
from .util import get_rs_index


class A205Schema:
    def __init__(self, schema_path):
        with open(schema_path, "r") as schema_file:
            uri_path = os.path.abspath(os.path.dirname(schema_path))
            if os.sep != posixpath.sep:
                uri_path = posixpath.sep + uri_path

            resolver = jsonschema.RefResolver(f'file://{uri_path}/', schema_path)

            self.validator = jsonschema.Draft7Validator(json.load(schema_file), resolver=resolver)

    def process_errors(self, errors, rs_index, parent_level = 0):
        '''
        This method collects relevant error messages using recursion for 'oneOf' or 'anyOf' validations
        '''
        messages = []
        for error in errors:
            if error.validator in ['oneOf','anyOf']:
                schema_node = self.get_schema_node(list(error.absolute_path))
                if 'RS' in schema_node:
                    rs_index = get_rs_index(schema_node['RS'])
                if rs_index is not None:
                    rs_errors = []
                    for rs_error in error.context:
                        if rs_error.relative_schema_path[0] == rs_index:
                            rs_errors.append(rs_error)
                else:
                    rs_errors = error.context
                messages += self.process_errors(rs_errors, rs_index, len(error.path))
            else:
                if len(error.path) >= parent_level:
                    messages.append(f"{error.message} ({'.'.join(error.path)})")
        if len(messages) == 0 and parent_level == 0:
            for error in errors:
                messages.append(f"{error.message} ({'.'.join(error.path)})")
        return messages

    def validate(self, instance):
        errors = sorted(self.validator.iter_errors(instance), key=lambda e: e.path)
        if len(errors) == 0:
            print(f"Validation successful for {instance['description']}")
        else:
            if 'RS_ID' in instance:
                rs_id = instance['RS_ID']
                rs_index = get_rs_index(rs_id)
            else:
                rs_id = "RS????"
                rs_index = None
            messages = self.process_errors(errors, rs_index)
            messages = [f"{i}. {message}" for i, message in enumerate(messages, start=1)]
            message_str = '\n  '.join(messages)
            raise Exception(f"Validation failed for \"{instance['description']}\" ({rs_id}) with {len(messages)} errors:\n  {message_str}")

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

    def trace_lineage(self, node, lineage, options):
        '''
        Search through lineage for the schema node one generation at a time.

        node: node to trace into
        lineage: remaining lineage to trace
        options: indices for any oneOf nodes
        '''
        for item in node:
            if lineage[0] == item:
                if len(lineage) == 1:
                    # This is the last node
                    if 'oneOf' in node[item] and options[0] is not None:
                        return self.resolve(node[item]['oneOf'][options[0]],False)
                    else:
                        return self.resolve(node[item],False)
                else:
                    # Keep digging

                    if 'oneOf' in node[item]:
                        if options[0] is not None:
                            option = self.resolve(node[item]['oneOf'][options[0]])
                            return self.trace_lineage(option,lineage[1:],options[1:])
                        else:
                            # Search in all options
                            for option in node[item]['oneOf']:
                                option = self.resolve(option)
                                if lineage[1] in option:
                                    try:
                                        return self.trace_lineage(option,lineage[1:],options[1:])
                                    except KeyError:
                                        # Not in this option try the next one
                                        # TODO: Handle this better (custom exception type)
                                        pass
                            raise KeyError(f"'{lineage[1]}' not found in schema.")

                    next_node = self.resolve(node[item])
                    if 'items' in next_node:
                        next_node = self.resolve(next_node['items'])
                    return self.trace_lineage(next_node,lineage[1:],options[1:])

        raise KeyError(f"'{lineage[0]}' not found in schema.")

    def get_schema_node(self, lineage, options=None):
        if len(lineage) == 0:
            return self.resolve(self.validator.schema, step_in=False)
        if options is None:
            options = [None]*len(lineage)
        schema = self.resolve(self.validator.schema)
        try:
            return self.trace_lineage(schema, lineage, options)
        except KeyError:
            return None

    def get_schema_version(self):
        return self.validator.schema["version"]

    def get_rs_title(self, rs):
        return self.resolve_ref(f'{rs}.schema.json#/title')

    def get_grid_variable_order(self, rs_selections, lineage, grid_vars):
        '''
        Get the order of grid variables.

        TODO: Don't know if we can always rely on jsonschema always preserving order
        '''
        if lineage[-1] != 'grid_variables':
            raise Exception(f"{lineage[-1]} is not a 'grid_variables' data group.")
        parent_schema_node = self.get_schema_node(lineage[:-1], rs_selections[:-1])
        if 'oneOf' in parent_schema_node:
            # Alternate performance maps allowed. Make sure we get the right one
            for option in parent_schema_node['oneOf']:
                option = self.resolve(option)
                for var in grid_vars:
                    option_grid_vars = self.resolve(option['grid_variables'])
                    if var not in option_grid_vars:
                        schema_node = None
                        break
                    else:
                        schema_node = option_grid_vars
                if schema_node:
                    break
        else:
            schema_node = self.get_schema_node(lineage, rs_selections)['properties']
        order = []

        if not schema_node:
            raise Exception(f"Unable to find schema for grid variables: {grid_vars}")

        for item in schema_node:
            order.append(item)
        return order

    def create_grid_set(self, representation, lineage):
        grid_var_content, rs_selections = get_representation_node_and_rs_selections(representation, lineage)
        order = self.get_grid_variable_order(rs_selections, lineage,[x for x in grid_var_content])
        return create_grid_set(grid_var_content, order)
