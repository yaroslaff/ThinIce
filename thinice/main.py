from dotenv import load_dotenv
import os
from pathlib import Path
from rich.console import Console
import typer
from typing_extensions import Annotated
from typing import Optional
from rich.pretty import pprint

from .core.credentials import AWSCredentials
from .core.vault  import GlacierVault

app = typer.Typer(pretty_exceptions_show_locals=False, 
    # rich_markup_mode="rich"
    no_args_is_help=True,                
    rich_markup_mode="markdown"
    )
err_console = Console(stderr=True)

vault: GlacierVault

# panels
panel_main="Main commands, each has its own help, e.g. sashimi upload --help"
panel_env = "Config (.env file)"

@app.callback(
        context_settings={"help_option_names": ["-h", "--help"]})
def callback(ctx: typer.Context,
    key_id: Annotated[str, typer.Option(envvar='AWS_ACCESS_KEY_ID', rich_help_panel=panel_env, help='AWS key id')],
    secret_key: Annotated[str, typer.Option(envvar='AWS_SECRET_ACCESS_KEY', rich_help_panel=panel_env, help='AWS secret key')],
    vault_name: Annotated[str, typer.Option('--vault',envvar='AWS_GLACIER_VAULT', rich_help_panel=panel_env, help='Vault Name')] = None
    ):
    """
    Client for Amazon Glacier
    """
    global vault
    credentials = AWSCredentials(key_id=key_id, secret_key=secret_key)
    vault = GlacierVault(credentials=credentials, vault_name=vault_name)
    print("INIT", vault)

@app.command(rich_help_panel=panel_main,
             help='List available glacier vaults',
            epilog="""~~~shell\n
thinice vaults\n
~~~
"""
)
def vaults():
    vaults = vault.list_vaults()
    pprint(vaults)

@app.command(rich_help_panel=panel_main,
             help='List glacier jobs',
            epilog="""~~~shell\n
thinice jobs\n
~~~
"""
)
def jobs():
    jobs = vault.list_jobs()
    pprint(jobs)


def main():
    load_dotenv()
    app()