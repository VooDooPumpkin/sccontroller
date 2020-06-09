from .template import Template


import os
import click
from flask import current_app, g, json
from flask.cli import with_appcontext

def add_template(name, description, sol_filename, contract_name, creator_guide_filename,
                 users_guide_filename, statuses_list_filename, parameters_list_filename):
    message = ""

    templates_path = os.path.join(current_app.root_path, 'templates')

    with open(os.path.join(templates_path, creator_guide_filename), 'rb') as f:
        creator_guide = json.loads(f.read().decode('utf8'))
    with open(os.path.join(templates_path, users_guide_filename), 'rb') as f:
        users_guide = json.loads(f.read().decode('utf8'))
    with open(os.path.join(templates_path, statuses_list_filename), 'rb') as f:
        statuses_list = json.loads(f.read().decode('utf8'))
    with open(os.path.join(templates_path, parameters_list_filename), 'rb') as f:
        parameters_list = json.loads(f.read().decode('utf8'))

    try:
        Template(name, description, sol_filename, contract_name, creator_guide, users_guide, statuses_list,
                 parameters_list, id=None, exist=False)
        message = "Template was successfully added"
    except Exception as err:
        message = " Error: parameters are invalid or this template already exists"
    finally:
        return message

def add_default_templates():
    name = "ToktoTok"
    description = "Token fo Token contract"
    sol_filename = "TtoT_contract.sol"
    contract_name = "TokToTokContract"
    creator_guide_filename = "TtoT_contract_cguide.json"
    users_guide_filename = "TtoT_contract_uguide.json"
    statuses_list_filename = "TtoT_contract_statuses.json"
    parameters_list_filename = "TtoT_contract_params.json"
    return add_template(name, description, sol_filename, contract_name, creator_guide_filename,
                 users_guide_filename, statuses_list_filename, parameters_list_filename)


@click.command('add-template')
@click.option('--name', prompt='Template name', help='Name for template to add')
@click.option('--desc', prompt='Description', help='Description for template to add')
@click.option('--sol', prompt='Code filename', help='Filename of template code .sol')
@click.option('--cname', prompt='Contract name', help='Name of contract in template code')
@click.option('--cguide', prompt='Creator guide filename', help='Filename of creator\'s guide in json')
@click.option('--uguide', prompt='Users guide filename', help='Filename of users\' guide in json')
@click.option('--statuses', prompt='Statuses filename', help='Filename of statuses\' list in json')
@click.option('--params', prompt='Parameters filename', help='Filename of parameters list in json')
@with_appcontext

def add_template_comand(name, desc, sol, cname, cguide, uguide, statuses, params):
    """Add new template"""
    click.echo(add_template(name, desc, sol, cname, cguide, uguide, statuses, params))

@click.command('add-default-templates')
@with_appcontext
def add_default_templates_comand():
    """Add default templates to database"""
    click.echo(add_default_templates())


def init_app(app):
    app.cli.add_command(add_template_comand)
    app.cli.add_command(add_default_templates_comand)