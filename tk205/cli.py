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
@cli.command('translate', help="Translate a representation specification between file formats.")
@click.option('-i', '--input', help="Input file with extension.", type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
@click.option('-o', '--output', help="Output file with extension.",  type=click.File(mode='w', encoding=None, errors='strict', lazy=None, atomic=False))
def translate(input, output):
    tk205.translate(input.name, output.name)

# Report
@cli.command('report', help="Create human-readable report based on input representation.")
@click.option('-i', '--input', help="Input file with extension.", type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
@click.option('-o', '--output', help="Output report path WITHOUT extension (pdf implied).",  type=click.File(mode='w', encoding=None, errors='strict', lazy=None, atomic=False))
def report(input, output):
    print("Report functionality not yet implemented.")

# Document Schema
@cli.command('docschema', help="Generate repspec-style documentation from schema information.")
@click.option('-o', '--output', help="Output document path WITHOUT extension (docx implied?).",  type=click.File(mode='w', encoding=None, errors='strict', lazy=None, atomic=False))
def docschema(output):
    print("Doc Schema functionality not yet implemented.")

# XLSX Template
@cli.command('template', help="Generate an XLSX template based on the schema for a given repspec.", context_settings=dict(ignore_unknown_options=True,allow_extra_args=True))
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

    tk205.template(repspec, output.name, **kwargs)

# Validate
@cli.command('validate', help="Perform all validation tests and generate text report to stdout.")
@click.option('-i', '--input', help="Input file with extension.", type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
def validate(input):
    tk205.validate(input.name)

# Export
@cli.command('export', help="Generate simulation input models in specific simulation tool syntax (not yet functional).")
@click.option('-s', '--syntax', help="Choice of simulation tool syntax.", type=click.Choice(['DOE-2','EnergyPlus','TRNSYS']))
@click.option('-i', '--input', help="Input file with extension.", type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
@click.option('-o', '--output', help="Output report path WITHOUT extension (implied by style).",  type=click.File(mode='w', encoding=None, errors='strict', lazy=None, atomic=False))
def export(syntax, input, output):
    print("Export functionality not yet implemented.")
