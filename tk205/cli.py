import tk205
import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def print_version():
    click.echo(f'{__name__}, version {__version__}')

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(None,'-v','--version')
def cli():
    """tk205.

    ASHRAE 205 Representation Specification Toolkit.
    """

# Translate
short_help_text = "Translate a representation specification between file formats."
help_text = short_help_text
@cli.command('translate', short_help=short_help_text, help=help_text)
@click.option('-i', '--input', help="Input file with extension.", type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
@click.option('-o', '--output', help="Output file with extension.",  type=click.File(mode='w', encoding=None, errors='strict', lazy=None, atomic=False))
def translate(input, output):
    tk205.translate(input.name, output.name)

# Report
short_help_text = "Create human-readable report based on input representation."
help_text = short_help_text
@cli.command('report', short_help=short_help_text, help=help_text, hidden=True)
@click.option('-i', '--input', help="Input file with extension.", type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
@click.option('-o', '--output', help="Output report path WITHOUT extension (pdf implied).",  type=click.File(mode='w', encoding=None, errors='strict', lazy=None, atomic=False))
def report(input, output):
    print("Report functionality not yet implemented.")

# Document Schema
short_help_text = "Generate repspec-style documentation from schema information."
help_text = short_help_text
@cli.command('docschema', short_help=short_help_text, help=help_text, hidden=True)
@click.option('-o', '--output', help="Output document path WITHOUT extension (docx implied?).",  type=click.File(mode='w', encoding=None, errors='strict', lazy=None, atomic=False))
def docschema(output):
    print("Doc Schema functionality not yet implemented.")

# XLSX Template
short_help_text = "Generate an XLSX template based on the schema for a given repspec."
help_text = "\n\n".join([short_help_text] + [
    "Specific data elements may be set within the template using additional options. For example:",
    "  --notes=\"Generated from template.\"",
    "Where repspecs use alternatives, a keyword must be provided to define which alternative to use. For example:",
    "  --performance_map_type=DISCRETE",
    "generates a DISCRETE performance map for RS0003."
    ])
@cli.command('template', short_help=short_help_text, help=help_text, context_settings=dict(ignore_unknown_options=True,allow_extra_args=True))
@click.option('-r', '--repspec', help="Representation Specification ID.",  type=click.Choice(['RS0001','RS0002','RS0003']))
@click.option('-o', '--output', help="Output template path.",  type=click.File(mode='w', encoding=None, errors='strict', lazy=None, atomic=False))
@click.pass_context
def template(ctx, repspec, output):
    kwargs = {}
    for i, arg in enumerate(ctx.args):
        if '=' in arg:
            new_arg = arg.split('=')
            key = new_arg[0].lstrip('-')
            value = new_arg[1]
            kwargs[key] = value
        else:
            if arg[0] == '-':
                key = arg.lstrip('-')
                value = ctx.args[i+1]
                kwargs[key] = value

    try:
        tk205.template(repspec, output.name, **kwargs)
    except Exception as e:
        print(e)

# Validate
short_help_text = "Perform all validation tests and generate text report to stdout."
help_text = short_help_text
@cli.command('validate', short_help=short_help_text, help=help_text)
@click.option('-i', '--input', help="Input file with extension.", type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
def validate(input):
    tk205.validate(input.name)

# Export
short_help_text = "Generate simulation input models in specific simulation tool syntax."
help_text = short_help_text
@cli.command('export', short_help=short_help_text, help=help_text, hidden=True)
@click.option('-s', '--syntax', help="Choice of simulation tool syntax.", type=click.Choice(['DOE-2','EnergyPlus','TRNSYS']))
@click.option('-i', '--input', help="Input file with extension.", type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
@click.option('-o', '--output', help="Output report path WITHOUT extension (implied by style).",  type=click.File(mode='w', encoding=None, errors='strict', lazy=None, atomic=False))
def export(syntax, input, output):
    print("Export functionality not yet implemented.")
