from jinja2 import Environment, FileSystemLoader
import os
from functools import reduce
from glob import glob
paths = glob('*/')

def get_directory_structure(rootdir):
    """
    Recursively creates a nested dictionary that represents the folder structure of rootdir
    """
    directory_dict = {}
    contents = []
    for item in os.listdir(rootdir):
        if not item.startswith('.') and os.path.isfile(os.path.join(rootdir, item)):
            contents.append(item)
        elif not item.startswith('.') and os.path.isdir(os.path.join(rootdir, item)):
            directory_dict[item] = get_directory_structure(os.path.join(rootdir, item))
    if contents:
        return contents
    return directory_dict

def generate_page(env, template_name, file_name, headline, content):
    template = env.get_template(template_name)
    with open(file_name, 'w+') as f:
        f.write(template.render(
            nav = file_name,
            headline = headline,
            content = content
        )) 
    f.close()

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    env = Environment( loader = FileSystemLoader(templates_dir) )
    
    content_directory = 'assets'
    assets_dir = os.path.join(root, content_directory)
    content_dictionary = get_directory_structure(assets_dir)


    test_examples = [y for x,y in content_dictionary['examples'].items()]
    print(test_examples)
    test_examples_format = [
        ['RS0001ExampleFile', "Chill to the max", ['RS0001ExampleFile.cbor', 'RS0001ExampleFile.json']], 
        ['RS0001ExampleFile', "Chill to the max", ['RS0001ExampleFile.cbor', 'RS0001ExampleFile.json']], 
        ['RS0001ExampleFile', "Chill to the max", ['RS0001ExampleFile.cbor', 'RS0001ExampleFile.json']]
    ] 
    generate_page(env, 'examples_template.html', 'examples.html', 'Example Files', test_examples_format)

    test_schema =  content_dictionary['schema']
    print(test_schema)
    test_schema_format = [
        ['ASHRAE205', "Base schema for ASHRAE 205 representations", 'ASHRAE205.schema.json'], 
        ['RS0001: Liquid-Cooled Chillers', "Chill to the max", 'RS0001.schema.json'], 
    ] 
    generate_page(env, 'schema_template.html', 'schema.html', 'JSON Schema (Normative)', test_schema_format)

if __name__ == '__main__':
	main()
