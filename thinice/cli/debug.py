import typer
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
    hash: Annotated[str, typer.Argument(help='Hash prefix (or full hash)')],
):
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

