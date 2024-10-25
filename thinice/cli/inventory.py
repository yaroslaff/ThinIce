from rich.pretty import pprint
from .app import typerapp, panel_main
from . import app
from ..core.utils import td2str
from pathlib import Path
from typing_extensions import Annotated
import typer
import datetime
from rich import print as rprint
from rich.text import Text


@typerapp.command("inventory", rich_help_panel=panel_main,
             help='Request inventory from glacier vault',
            epilog="""~~~shell\n
thinice inventory\n
~~~
"""
)
def request_inventory(
    force: Annotated[bool, typer.Option('--force', rich_help_panel=panel_main, help='Force request even if requested recently')] = False,
    ):

    if force:
        app.vault.request_inventory(force=force)
        rprint(Text(f"Requested new inventory from glacier (because --force)", style="yellow"))    
        return


    # do we have ongoing job?
    jobs = app.vault.list_jobs()
    
    active_job = next((item for item in jobs if item.get('Action') == 'InventoryRetrieval' and item.get('StatusCode') == 'InProgress'), None)

    completed_jobs = [ item for item in jobs if item.get('Action') == 'InventoryRetrieval' and item.get('StatusCode') == 'Succeeded' ]

    if completed_jobs:
        accepted = False
        # there could be more then one inventories
        for job in completed_jobs:
            if app.vault.accept_inventory(job=job):
                accepted = True
        if accepted:
            rprint(f"Accepted inventory from glacier. Do [dim white]thinice ls[/dim white] to list archives")
            return

    if active_job:
        # get age of job as HH:MM, difference between now and lastjob['CreationDate'] e.g. 2024-10-25T12:59:35.451Z
        age = td2str(datetime.datetime.now(tz=datetime.timezone.utc) - datetime.datetime.fromisoformat(active_job['CreationDate']))
        rprint(Text(f"Ongoing job found (started {age}). Use --force to repeat", style="yellow"))
        return

    # if we are here, request new inventory
    app.vault.request_inventory(force=force)
    print(f"Requested new inventory from glacier")
    
