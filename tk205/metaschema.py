import json
import yaml
from tk205.file_io import load
import os

# -------------------------------------------------------------------------------------------------
class DataElement:

    def __init__(self):
        self._Description = ''
        self._DataType    = 'String'
        self._Units       = 'h-ft2-F/Btu'
        self._Range       = '>0'
        self._Required    = True
        self._Notes       = ''


# -------------------------------------------------------------------------------------------------
class DataGroup:

    def __init__(self):
        self._data_elements = list()


# -------------------------------------------------------------------------------------------------
class Enumeration:

    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.enumerants = list() # list of tuple:[value, description, display_text, notes]

    def __str__(self):
        key_line = '"' + self.name + '": {\n'
        conclusion = '}'
        descr = '\t"description":' + self.description + ',\n' if self.description else ''
        typ   = '\t"type": "string",\n'
        enum = ''
        enumtext = ''
        enumdesc = ''
        notes = ''
        z = list(zip(*self.enumerants))
        if len(z) == 4:
            if any(z[0]):
                enum  = '\t"enum: [\n'
                for e in z[0]:
                    enum += 2*'\t' + '"' + (e if e else '') + '",\n'
                enum += 2*'\t' + '],\n'
            if any(z[1]):
                enumdesc  = '\t"descriptions: [\n'
                for e in z[1]:
                    enumdesc += 2*'\t' + '"' + (e if e else '') + '",\n'
                enumdesc += 2*'\t' + '],\n'
            if any(z[2]):
                enumtext  = '\t"enum_text: [\n'
                for e in z[2]:
                    enumtext += 2*'\t' + '"' + (e if e else '') + '",\n'
                enumtext += 2*'\t' + '],\n'
            if any(z[3]):
                notes  = '\t"notes: [\n'
                for e in z[3]:
                    notes += 2*'\t' + '"' + (e if e else '') + '",\n'
                notes += 2*'\t' + '],\n'
        return (key_line + descr + typ + enum + enumtext + enumdesc + notes + conclusion)

    def add_enumerator(self, value, description=None, display_text=None, notes=None):
        self.enumerants.append((value, description, display_text, notes))

# -------------------------------------------------------------------------------------------------
class JSON_translator:
    def __init__(self):
        self._heading = {"$schema": "http://json-schema.org/draft-07/schema#",
                   "title": "Liquid-Cooled Chiller",
                   "description": "Schema for ASHRAE 205 annex RS0001: Liquid-Cooled Chiller",
                   "definitions" : None}
        self._data_groups = list()
        self._enumerations = list()
        self._ref_declarations = list()

    def load_metaschema(self, input_file_path):
        self._contents = load(input_file_path)
        # Iterate through the dictionary, looking for fixed types
        for base_level_tag in self._contents:
            # try/except here instead of checking for 'type'?
            if ('type' in self._contents[base_level_tag] and 
                self._contents[base_level_tag]['type'] == 'Enumeration'):
                self._process_enumerations(base_level_tag, 
                                           self._contents[base_level_tag]['Enumerators'])

    def _process_enumerations(self, name_key, subdict):
        definition = Enumeration(name_key)
        enums = self._contents[name_key]['Enumerators']
        for key in enums:
            try: #if enums[key]:
                descr = enums[key]['Description']  if 'Description'  in enums[key] else None
                displ = enums[key]['Display Text'] if 'Display Text' in enums[key] else None
                notes = enums[key]['Notes']        if 'Notes'        in enums[key] else None
                definition.add_enumerator(key, descr, displ, notes)
            except TypeError: # key's value is None
                definition.add_enumerator(key)
        self._enumerations.append(definition)


# -------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    j = JSON_translator()
    j.load_metaschema(os.path.join('..', 'schema-205', 'src', 'ASHRAE205.schema.yml'))
    for e in j._enumerations:
        print(e)



