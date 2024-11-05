import typer
import os
from rich.pretty import pprint
from . import app
from typing_extensions import Annotated
panel_debug = 'Debugging'

debug_app = typer.Typer()
@debug_app.command(rich_help_panel=panel_debug,
             help='Dump local inventory',
            epilog="""~~~shell\n
thinice debug dump\n
~~~
"""
)
def dump():
    app.vault.inventory.dump()

@debug_app.command(rich_help_panel=panel_debug,
             help='Ignore hash (job)',
            epilog="""~~~shell\n
thinice debug ignore JnNqXl\n
~~~
"""
)
def ignore(
    hash: Annotated[str, typer.Argument(help='Hash prefix (or full hash)')] = None,
):
    
    if hash is None:
        jobs = app.vault.list_jobs(noignore=True)
        print(f"Jobs for THINICE_IGN=\"{' '.join(job['JobId'][:5] for job in jobs)}\"")

        return

    # direct access here!
    app.vault.inventory.inventory['_debug']['ignore'].append(hash)
    app.vault.inventory.save()

@debug_app.command(rich_help_panel=panel_debug,
             help='Ignore hash (job)',
            epilog="""~~~shell\n
thinice debug ignore JnNqXl\n
~~~
"""
)
def clear():
    # direct access here!
    app.vault.inventory.inventory['_debug']['ignore'] = list()
    app.vault.inventory.save()

    if os.getenv('THINICE_IGN'):
        print('THINICE_IGN = ', os.getenv('THINICE_IGN'))

