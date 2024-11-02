from rich.pretty import pprint
import rich
from rich import print as rprint
from rich.table import Table
from pathlib import Path
from .app import typerapp, panel_main
from . import app
import json
from typing_extensions import Annotated
import typer
import sys

panel_list = "Options"

def colorize_status_list(status: str) -> str:

    color_map = {
        'Cold': 'white',
        'Deleted': 'red',
        'Requested': 'cyan',
        'Warm': 'green'
    }

    if status in color_map:
        return f"[{color_map[status]}]{status}[/{color_map[status]}]"
    else:
        return status

@typerapp.command("ls", rich_help_panel=panel_main,
             help='List glacier files',
            epilog="""~~~shell\n
thinice list\n
thinice list --format _raw\n
thinice list --format "{ArchiveDescription}: {ArchiveId}"\n
~~~

for all available fields, use `--format _raw`
"""
)
def ls_archives(
    fmt: Annotated[str, typer.Option(
        '-f', '--format',
        rich_help_panel=panel_list, help='Format (_brief, _raw, _json or format string)')] = '_brief',
    pattern: Annotated[str, typer.Argument(help='Desc pattern, e.g. "*gz" or "server1*"')] = None,
    size: Annotated[str, typer.Option(help='size, e.g. "10G" or "-1G"')] = None,
    age: Annotated[int, typer.Option(help='age in days, e.g. "30" or "-30"')] = None,
    warm: Annotated[bool, typer.Option(
        '-w', '--warm',
        rich_help_panel=panel_list, help='Display only warm archives')] = False,
    no_jobs: Annotated[bool, typer.Option(
        '-n', '--no-jobs',
        rich_help_panel=panel_list, help='Do NOT update jobs from glacier, use latest cached')] = False):


    inv_date = app.vault.inventory.inventory_date()

    if not inv_date:
        rprint("No local inventory, to request inventory run: [dim white]thinice inventory[/dim white]")

    if not no_jobs:
        app.vault.list_jobs()

    if fmt == '_brief':
        if inv_date:
            table_title = f"Archives (Inventory: {inv_date.strftime('%Y/%m/%d %H:%M')})"
        else:
            table_title = "Archives (No local inventory)"

        table = Table(title=table_title)
        table.add_column("Description")
        table.add_column("Size")
        table.add_column("Date", style="cyan")
        table.add_column("Age", style="cyan")
        table.add_column("Status", style="dim white")
        table.add_column("Id...", style="#808080")

        for file_rec in app.vault.list_archives(pattern=pattern, sizespec=size, agespec=age, warm=warm):

            table.add_row(
                file_rec['ArchiveDescription'], 
                file_rec['sz'], 
                file_rec['date'], 
                str(file_rec['age']), 
                colorize_status_list(file_rec['status']),
                file_rec['ArchiveId'][:5] 
            )
        rich.print(table)

    elif fmt == '_raw':
        for file_rec in app.vault.list_archives():
            pprint(file_rec)
    elif fmt == '_json':
        print(json.dumps(app.vault.list_archives(), indent=4))
    else:        
        for file_rec in app.vault.list_archives():
            print(fmt.format(**file_rec))


""" list - alias for ls """

@typerapp.command("list", hidden=True)
def list_archives(
    fmt: Annotated[str, typer.Option(
        '-f', '--format',
        rich_help_panel=panel_list, help='Format (_brief, _raw, _json or format string)')] = '_brief',
    no_jobs: Annotated[bool, typer.Option(
        '-n', '--no-jobs',
        rich_help_panel=panel_list, help='Do NOT update jobs from glacier, use latest cached')] = False):
    return ls_archives(fmt=fmt, no_jobs=no_jobs)