import typer
from typer.core import TyperGroup
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from typing_extensions import Annotated
from typing import Optional

from ..core.credentials import AWSCredentials
from ..core.vault  import GlacierVault


typerapp = typer.Typer(pretty_exceptions_show_locals=False, 
    # rich_markup_mode="rich"
    no_args_is_help=True,                
    rich_markup_mode="markdown",
    )
err_console = Console(stderr=True)

vault: GlacierVault = None

# panels
panel_main="Main commands, each has its own help, e.g. `thinice jobs -h`"
panel_env = "Global options (/etc/thinice.env, ~/.config/thinice/thinice.env)"
panel_updown = "Upload/Download"

@typerapp.callback(
        context_settings={"help_option_names": ["-h", "--help"]})
def callback(ctx: typer.Context,
    key_id: Annotated[str, typer.Option(envvar='AWS_ACCESS_KEY_ID', show_default=False, show_envvar=True, rich_help_panel=panel_env, help='AWS key id')],
    secret_key: Annotated[str, typer.Option(envvar='AWS_SECRET_ACCESS_KEY', show_default=False, rich_help_panel=panel_env, help='AWS secret key')],
    region: Annotated[str, typer.Option(envvar='AWS_REGION', show_default=False, rich_help_panel=panel_env, help='region')],
    vault_name: Annotated[str, typer.Option('--vault',envvar='AWS_GLACIER_VAULT', show_default=False, rich_help_panel=panel_env, help='Vault Name')] = None,
    verbose: Annotated[bool, typer.Option('-v', '--verbose', show_default=False, rich_help_panel=panel_env, help='verbose mode')] = False
    ):
    """
    Client for Amazon Glacier
    """
    global vault
    credentials = AWSCredentials(key_id=key_id, secret_key=secret_key, region=region)
    vault = GlacierVault(credentials=credentials, vault_name=vault_name, verbose=verbose)
