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

def main():
    load_dotenv(dotenv_path=Path.home() / '.thinice' / '.env')
    typerapp.add_typer(debug_app, name='debug', help='Debugging commands')
    typerapp()