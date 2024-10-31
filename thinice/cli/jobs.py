import typer
from rich.pretty import pprint
from .app import panel_main, typerapp
from . import app
from ..core.utils import td2str, iso2dt
from rich.table import Table
import rich
from rich.console import Console
import datetime
from typing_extensions import Annotated

console=Console()

def colorize_status_jobs(status: str) -> str:

    color_map = {
        'Succeeded': 'green',
        'True': 'green',
        'Expedited': 'yellow bold',
        'Standard': 'cyan'
    }

    if status in color_map:
        return f"[{color_map[status]}]{status}[/{color_map[status]}]"
    else:
        return status


@typerapp.command(rich_help_panel=panel_main,
             help='List glacier jobs',
            epilog="""~~~shell\n
thinice jobs\n
~~~
"""
)
def jobs(
    raw: Annotated[bool, typer.Option('--raw', rich_help_panel=panel_main, help='dump full raw data')] = False,
):
    jobs = app.vault.list_jobs()

    if raw:
        pprint(jobs)
        return

    table = Table(title="Jobs")
    table.add_column("Action",)
    table.add_column("Age", style="blue")
    table.add_column("Completed")
    table.add_column("StatusCode", style="dim white")
    table.add_column("Tier", style="dim white")
    table.add_column("Description")
    table.add_column("Size")
    table.add_column("ArchiveId...", style="#808080")

    now = datetime.datetime.now(datetime.timezone.utc)

    for job in app.vault.list_jobs():

        # convert to isotime string to YY-MM-DD HH:MM
        created =  iso2dt(job['CreationDate'].split('+')[0].replace('T', ' '))
        age = td2str(now - created)

        if job.get('ArchiveId'):
            field_archive_id = job['ArchiveId'][:14]

            arc = app.vault.inventory.get_archive_info(job['ArchiveId'])
            if arc:
                size = arc['sz']
                field_desc = arc['ArchiveDescription']
            else:
                size = '<no inventory>'
                field_desc = '<no inventory>'
        else:
            field_archive_id = ''
            field_desc = ''
            size = ''

        table.add_row(
            job['Action'],
            age,
            colorize_status_jobs(str(job['Completed'])),
            colorize_status_jobs(job['StatusCode']),
            colorize_status_jobs(job.get('Tier')),
            field_desc,
            size,
            field_archive_id
        )
    # rich.print(table)
    console.print(table)