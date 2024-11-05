from rich.pretty import pprint
from .app import typerapp, panel_main
from . import app
from ..core.utils import td2str, iso2dt
from ..core.exceptions import InventoryJobActive, InventoryIsOlder, InventoryIsSame
from pathlib import Path
from typing_extensions import Annotated
import typer
import datetime
from rich import print as rprint
from rich.text import Text
import sys


def request_inventory(force: bool=False):
    # if we are here, request new inventory
    try:
        app.vault.request_inventory(force=force)
        print(f"Requested new inventory from glacier")
    except InventoryJobActive as e:
        rprint(Text(str(e), style="yellow"), file=sys.stderr)
        rprint('Run [code]thinice jobs[/code] to see jobs, or [code]thinice inventory request --force[/code] to force request new inventory', file=sys.stderr)        
    

def accept_inventory(force: bool=False) -> bool:
    jobs = app.vault.list_jobs()
    completed_jobs = [ item for item in jobs if item.get('Action') == 'InventoryRetrieval' and item.get('StatusCode') == 'Succeeded' ]
    
    if completed_jobs:
        accepted = False
        # there could be more then one inventories
        for job in completed_jobs:
            if app.vault.inventory.is_ignored(hash=job['JobId']):                
                continue

            try:
                if app.vault.accept_inventory(job=job):
                    print(f"Accepted inventory from glacier")
                    return True
            except InventoryIsOlder as e:
                rprint(Text(str(f"Do not accept inventory job {job['JobId'][:5]} from WWWWW: it's old"), style="yellow"), file=sys.stderr)
                return False
            except InventoryIsSame as e:
                rprint(Text(str(e), style="yellow"), file=sys.stderr)
                return False

    else:
        rprint(Text(str("No completed inventory jobs found"), style="yellow"), file=sys.stderr)
        rprint('Run [code]thinice jobs[/code] to see jobs, or [code]thinice inventory --force[/code] to force request new inventory', file=sys.stderr)
        return False


@typerapp.command("inventory", rich_help_panel=panel_main,
             help='request/accept inventory from glacier vault',
            epilog="""~~~shell\n
thinice inventory\n
~~~
"""
)
def inventory_command(
    subcommand: Annotated[str, typer.Argument(help='subcommand: auto/request/accept (default: auto)')] = "auto",
    force: Annotated[bool, typer.Option('--force', help='Force request even if requested recently')] = False,
    ):


    if subcommand not in ['auto', 'request', 'accept']:
        rprint(f"Unknown subcommand {subcommand}, use one of [code]auto[/code] (default), [code]request[/code], [code]accept[/code]")
        return

    if subcommand == 'request':
        request_inventory(force=force)
        return
    
    if subcommand == 'accept':
        accept_inventory(force=force)
        return


    # here we should autodetect
  
    if accept_inventory(force=force):
        return
    
    # do we have ongoing job?
    jobs = app.vault.list_jobs()    
    active_job = next((item for item in jobs if item.get('Action') == 'InventoryRetrieval' and item.get('StatusCode') == 'InProgress'), None)

    if active_job:
        # get age of job as HH:MM, difference between now and lastjob['CreationDate'] e.g. 2024-10-25T12:59:35.451Z
        age = td2str(datetime.datetime.now(tz=datetime.timezone.utc) - iso2dt(active_job['CreationDate']))
        rprint(Text(f"Ongoing job {active_job['JobId'][:5]}... found (started {age} ago). Use --force to repeat", style="yellow"))
        return
    else:
        request_inventory(force=force)

