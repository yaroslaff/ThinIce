import typer
from rich.pretty import pprint
from . import app

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
             help='List glacier jobs',
            epilog="""~~~shell\n
thinice debug jobs\n
~~~
"""
)
def jobs():
    jobs = app.vault.list_jobs()
    pprint(jobs)
