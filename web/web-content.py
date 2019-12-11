import sys
import git
import os
import json
from collections import OrderedDict
from distutils.dir_util import copy_tree
from jinja2 import Environment, FileSystemLoader
import tk205

root_dir = os.path.dirname(os.path.abspath(__file__))

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


def create_files(web_dir):
    """
    Create or replace the example and template files inside of open205.github.io
    """
    assets_dir = os.path.join(web_dir, 'assets')
    if not os.path.isdir(assets_dir):
        os.mkdir(assets_dir)

    examples_dir = os.path.join(assets_dir, 'examples')
    if not os.path.isdir(examples_dir):
        os.mkdir(examples_dir)

    json_dir = os.path.join(examples_dir, 'json')
    if not os.path.isdir(json_dir):
        os.mkdir(json_dir)

    cbor_dir = os.path.join(examples_dir, 'cbor')
    if not os.path.isdir(cbor_dir):
        os.mkdir(cbor_dir)

    xlsx_dir = os.path.join(examples_dir, 'xlsx')
    if not os.path.isdir(xlsx_dir):
        os.mkdir(xlsx_dir)

    yaml_dir = os.path.join(examples_dir, 'yaml')
    if not os.path.isdir(yaml_dir):
        os.mkdir(yaml_dir)

    templates_dir = os.path.join(assets_dir, 'templates')
    if not os.path.isdir(templates_dir):
        os.mkdir(templates_dir)

    schema_dir = os.path.join(assets_dir, 'schema')
    if not os.path.isdir(schema_dir):
        os.mkdir(schema_dir)

    tk205.translate_directory('schema-205/examples/json', json_dir)
    tk205.translate_directory('schema-205/examples/json', cbor_dir)
    tk205.translate_directory('schema-205/examples/json', xlsx_dir)
    tk205.translate_directory('schema-205/examples/json', yaml_dir)
    copy_tree('schema-205/schema', schema_dir)

    # xlsx_template_creation
    tk205.file_io.clear_directory(templates_dir)
    template_content = tk205.load(os.path.join(root_dir, "..", "config", "templates.json"))
    for template in template_content:
        file_name_components = [template["RS"]]
        if template["file-name-suffix"]:
            file_name_components.append(template["file-name-suffix"])
        file_name_components.append("template.a205.xlsx")
        file_name = '-'.join(file_name_components)
        tk205.template(template["RS"],os.path.join(templates_dir,file_name), **template["keywords"])


def clone():
    """
    Clone open205.github.io website repository into the build directory.
    """
    build_dir = os.path.join(root_dir, '..', 'build')
    if not os.path.isdir(build_dir):
        os.mkdir(build_dir)
    web_dir = os.path.join(build_dir, 'web')
    if not os.path.isdir(web_dir):
        git.Repo.clone_from("https://github.com/open205/open205.github.io.git", web_dir, branch='master')
    assets_dir = os.path.join(web_dir, 'assets')
    if not os.path.isdir(assets_dir):
        os.mkdir(assets_dir)
    return web_dir


def generate(web_dir):
    """
    Generate all content for the open205.github.io repository
    """
    # Setup for Jinja2
    jinja_templates_dir = os.path.join(root_dir, 'templates')
    env = Environment( loader = FileSystemLoader(jinja_templates_dir) )

    schema_directory = os.path.join(root_dir, "..", "schema-205", "schema")
    examples_directory = os.path.join(web_dir, "assets", "examples")
    templates_directory = os.path.join(web_dir, "assets", "templates")

    schema_dictionary = get_directory_structure(schema_directory)
    examples_dictionary = get_directory_structure(examples_directory)
    templates_dictionary = get_directory_structure(templates_directory)

    # Create schema.html
    schema_page_data = OrderedDict()
    for schema_file in sorted(schema_dictionary):
        title, description = get_title_and_description(schema_file, schema_directory)
        schema_page_data[title] = {'title': title, 'description': description, 'schema_file': schema_file}
    generate_page(env, 'schema_template.html', 'schema.html', web_dir, 'JSON Schema (Normative)', schema_page_data)

    # Create examples.html
    examples_page_data = OrderedDict()
    for index, example_file in enumerate(sorted(examples_dictionary['json'])):
        file_list = []
        title, description = get_title_and_description(example_file, os.path.join(examples_directory, "json"))

        base_name = os.path.splitext(example_file)[0]
        for keys, example_types in examples_dictionary.items():
            for example in example_types:
                if base_name in example:
                    file_list.append(example)
        examples_page_data[example_file]={'title': title, 'description': description, 'file_list': file_list}
    generate_page(env, 'examples_template.html', 'examples.html', web_dir, 'Example Files', examples_page_data)

    # Create templates.html
    template_content = tk205.load(os.path.join(root_dir, "..", "config", "templates.json"))

    templates_page_data = OrderedDict()
    for index, template_file in enumerate(templates_dictionary):
        templates_page_data[template_file] = {'title':template_content[index]['RS'], 'description':template_content[index]['description'], 'template_file':template_file}
    generate_page(env, 'templates_template.html', 'templates.html', web_dir, 'XLSX Templates', templates_page_data)

    # Create index.html AKA about page
    generate_page(env, 'about_template.html', 'index.html', web_dir, '', None)

    # Create toolkit205.html
    generate_page(env, 'tk205_template.html', 'tk205.html', web_dir, '', None)


def main():
    web_dir = clone()
    create_files(web_dir)
    generate(web_dir)


if __name__ == '__main__':
	main()
