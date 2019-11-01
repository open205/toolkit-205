import os
import json
import posixpath
import jsonschema


class A205Schema:
    def __init__(self, schema_path):
        with open(schema_path, "r") as schema_file:
            uri_path = os.path.abspath(os.path.dirname(schema_path))
            if os.sep != posixpath.sep:
                uri_path = posixpath.sep + uri_path

            resolver = jsonschema.RefResolver(f'file://{uri_path}/', None)

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

    def resolve(self, node):
        if '$ref' in node:
            return self.resolve_ref(node['$ref'])[1]['properties']
        else:
            return node['properties']

    def resolve_ref(self, ref):
        return self.validator.resolver.resolve(ref)

    def get_schema(self):
        return self.validator.schema

    def trace_lineage(self, node, lineage):
        for item in node:
            if lineage[0] == item:
                if len(lineage) == 1:
                    # This is the last node
                    return node[item]
                else:
                    # Keep digging
                    
                    if 'oneOf' in node[item]:
                        # Search in all options
                        for option in node[item]['oneOf']:
                            option = self.resolve(option)
                            if lineage[1] in option:
                                return self.trace_lineage(option,lineage[1:])
                        raise KeyError(f"'{lineage[1]}' not found in schema.")  

                    return self.trace_lineage(self.resolve(node[item]),lineage[1:])

        raise KeyError(f"'{lineage[0]}' not found in schema.")

    def get_schema_node(self, lineage):
        schema = self.validator.schema['properties']
        try:
            return self.trace_lineage(schema, lineage)
        except KeyError:
            return None

    def get_schema_version(self):
        return self.validator.schema["version"]