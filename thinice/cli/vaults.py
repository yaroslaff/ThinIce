import typer
from rich.pretty import pprint
from .app import panel_main, typerapp
from . import app
from ..core.utils import td2str, kmgt
from rich.table import Table
import rich
import datetime

@typerapp.command(rich_help_panel=panel_main,
             help='List available glacier vaults',
            epilog="""~~~shell\n
thinice vaults\n
~~~
"""
)
def vaults():
    vaults = app.vault.list_vaults()
    table = Table(title="Vaults")
    table.add_column("VaultName", style="bright_white")
    table.add_column("Created", style="dim white")
    table.add_column("LastInventory")
    table.add_column("Archives", style="dim white")
    table.add_column("Size", style="white")

    for vault in vaults:
        table.add_row(
            vault['VaultName'],
            datetime.datetime.fromisoformat(vault['CreationDate']).strftime('%d/%m/%Y'),
            datetime.datetime.fromisoformat(vault['LastInventoryDate']).strftime('%d/%m/%Y'),
            str(vault['NumberOfArchives']),
            kmgt(vault['SizeInBytes'])
        )

    rich.print(table)


def colorize_status_jobs(status: str) -> str:

    color_map = {
        'Succeeded': 'green',
        'True': 'green'
    }

    if status in color_map:
        return f"[{color_map[status]}]{status}[/{color_map[status]}]"
    else:
        return status
