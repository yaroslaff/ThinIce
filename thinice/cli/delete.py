from rich.pretty import pprint
from .app import typerapp, panel_updown
from . import app
from typing_extensions import Annotated
import typer
import sys
import rich.progress
from pathlib import Path

@typerapp.command("delete", rich_help_panel=panel_updown,
            help='Delete archive from glacier',
            epilog="""~~~shell\n
# delete many files with this Description\n
thinice delete -m MyServer.tar.gz\n
\n
# delete one file with ArchiveId starting with this characters\n
thinice delete S93to\n
~~~"""
)
def delete_archive(
        arc_spec: Annotated[str, typer.Argument(help='ArchiveId (first letters) or Description')] = None,
        multiple: Annotated[bool, 
            typer.Option('--multiple', '-m', help='Request multiple files at once')] = False
    ):

    archives = app.vault.get_by_arc_spec(arc_spec)
    if not archives:
        print("No archives found")
        return
    
    if len(archives) > 1 and not multiple:
        print(f"More than one archive found ({len(archives)}), use archiveId for more accurate selection or use --multiple")
        sys.exit(1)
    
    for arc in archives:
        app.vault.delete_archive(archive_id=arc['ArchiveId'])


