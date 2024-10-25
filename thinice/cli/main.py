from dotenv import load_dotenv
import os
from pathlib import Path
import typer
from typing_extensions import Annotated
from typing import Optional
from rich.pretty import pprint

from .app import typerapp, panel_env, panel_main, vault
from . import delete, inventory, app, upload, download, list, jobs, vaults
from .debug import debug_app

def dotenv_location():
    locations = [
        '~/.config/thinice/thinice.env',
        '~/.thinice.env',
        '/etc/thinice.env',
    ]
    return next((os.path.expanduser(loc) for loc in locations if os.path.exists(os.path.expanduser(loc))), None)


def main():

    dotenv_file = dotenv_location()
    load_dotenv(dotenv_path=dotenv_file)
    typerapp.add_typer(debug_app, name='debug', help='Debugging commands')
    typerapp()