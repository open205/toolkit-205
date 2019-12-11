import sys
import git
import os
import json
from collections import OrderedDict
from distutils.dir_util import copy_tree
from jinja2 import Environment, FileSystemLoader
import tk205

def get_title_and_description(json_file, path):
    """
    Open an ASHRAE205 json schema or example file and return the title and description.
    """
    with open(os.path.join(path, json_file), 'r')as input_file:
        input_json = json.load(input_file)
        if "title" in input_json:
            title = input_json["title"]
            description = input_json["description"]
        elif "ASHRAE205" in input_json:
            title = input_json["ASHRAE205"]["RS_ID"]
            description = input_json["ASHRAE205"]["description"]
        return title, description


def get_directory_structure(rootdir):
    """
    Recursively creates a nested dictionary that represents the folder structure of rootdir.
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


def generate_page(env, template_name, file_name, destination, headline, content):
    """
    Create a specific html page of the open205.github.io website from a Jinja2 template.
    """
    template = env.get_template(template_name)
    html_file = os.path.join(destination, file_name)
    with open(html_file, 'w+') as f:
        f.write(template.render(
            nav = file_name,
            headline = headline,
            content = content
        )) 
    f.close()


def create_files(rss, open205_dir):
    """
    Create or replace the example and template files inside of open205.github.io 
    """
    assets_dir = os.path.join(open205_dir, 'assets')
    if not os.path.isdir(assets_dir):
        os.mkdir(assets_dir)

    examples_dir = os.path.join(open205_dir, 'assets', 'examples')
    if not os.path.isdir(examples_dir):
        os.mkdir(examples_dir)

    json_dir = os.path.join(open205_dir, 'assets', 'examples', 'json')
    if not os.path.isdir(json_dir):
        os.mkdir(json_dir)

    cbor_dir = os.path.join(open205_dir, 'assets', 'examples', 'cbor')
    if not os.path.isdir(cbor_dir):
        os.mkdir(cbor_dir)

    xlsx_dir = os.path.join(open205_dir, 'assets', 'examples', 'xlsx')
    if not os.path.isdir(xlsx_dir):
        os.mkdir(xlsx_dir)

    yaml_dir = os.path.join(open205_dir, 'assets', 'examples', 'yaml')
    if not os.path.isdir(yaml_dir):
        os.mkdir(yaml_dir)

    templates_dir = os.path.join(open205_dir, 'assets', 'templates')
    if not os.path.isdir(templates_dir):
        os.mkdir(templates_dir)

    schema_dir = os.path.join(open205_dir, 'assets', 'schema')
    if not os.path.isdir(schema_dir):
        os.mkdir(schema_dir)

    tk205.translate_directory('schema-205/examples/json', json_dir)
    tk205.translate_directory('schema-205/examples/json', cbor_dir)
    tk205.translate_directory('schema-205/examples/json', xlsx_dir)
    tk205.translate_directory('schema-205/examples/json', yaml_dir)
    copy_tree('schema-205/schema', schema_dir)

    # xlsx_template_creation
    tk205.file_io.clear_directory(templates_dir)
    for rs in rss:
        file_name_components = [rs["RS"]]
        if rs["file-name-suffix"]:
            file_name_components.append(rs["file-name-suffix"])
        file_name_components.append("template.a205.xlsx")
        file_name = '-'.join(file_name_components)
        tk205.template(rs["RS"],os.path.join(templates_dir,file_name), **rs["keywords"])


def clone(root_dir):
    """
    Clone open205.github.io website repository into the build directory.
    """
    open205_destination = os.path.join(root_dir, '..', 'build')
    if not os.path.isdir(open205_destination):
        os.mkdir(open205_destination)
    open205_dir = os.path.join(open205_destination, 'open205.github.io')
    if not os.path.isdir(open205_dir):
        git.Repo.clone_from("https://github.com/open205/open205.github.io.git", open205_dir, branch='master')
    open205_assets_dir = os.path.join(open205_dir, 'assets')
    if not os.path.isdir(open205_assets_dir):
        os.mkdir(open205_assets_dir)
    return open205_dir


def generate(params, root, open205_dir):
    """
    Generate all content for the open205.github.io repository
    """
    # Setup for Jinja2
    jinja_templates_dir = os.path.join(root, 'templates')
    env = Environment( loader = FileSystemLoader(jinja_templates_dir) )

    schema_directory = os.path.join(root, "..", "schema-205", "schema")
    examples_directory = os.path.join(open205_dir, "assets", "examples")
    templates_directory = os.path.join(open205_dir, "assets", "templates")

    schema_dictionary = get_directory_structure(schema_directory)
    examples_dictionary = get_directory_structure(examples_directory)
    templates_dictionary = get_directory_structure(templates_directory)

    # Create schema.html
    schema_page_data = OrderedDict() 
    for schema_file in sorted(schema_dictionary):
        title, description = get_title_and_description(schema_file, schema_directory)
        schema_page_data[title] = {'title':title, 'description':description, 'schema_file':schema_file}
    generate_page(env, 'schema_template.html', 'schema.html', open205_dir, 'JSON Schema (Normative)', schema_page_data)

    # Create examples.html
    examples_page_data = OrderedDict()
    for index, example_file in enumerate(sorted(examples_dictionary['json'])):
        file_list = []
        base_name = os.path.splitext(example_file)[0]
        for keys, example_types in examples_dictionary.items():
            for example in example_types:
                if base_name in example:
                    file_list.append(example)
        examples_page_data[example_file]={'title':params[index]['RS'], 'description':params[index]['description'], 'file_list':file_list}
    generate_page(env, 'examples_template.html', 'examples.html', open205_dir, 'Example Files', examples_page_data)

    # Create templates.html
    templates_page_data = OrderedDict()
    for index, template_file in enumerate(templates_dictionary):
        templates_page_data[template_file] = {'title':params[index]['RS'], 'description':params[index]['description'], 'template_file':template_file}
    generate_page(env, 'templates_template.html', 'templates.html', open205_dir, 'XLSX Templates', templates_page_data)

    # Create index.html AKA about page
    generate_page(env, 'about_template.html', 'index.html', open205_dir, '', None)

    # Create toolkit205.html
    generate_page(env, 'tk205_template.html', 'tk205.html', open205_dir, '', None)


def main():
    if len(sys.argv) != 2:
        print("Param file required.")
        exit()

    paramfile = sys.argv[1]
    if (tk205.get_extension(paramfile).lower() == '.json'):
        with open(paramfile) as json_file:
            params = (json.load(json_file))
        json_file.close()
    root = os.path.dirname(os.path.abspath(__file__))

    open205_dir = clone(root)
    create_files(params, open205_dir)
    generate(params, root, open205_dir)


if __name__ == '__main__':
	main()
