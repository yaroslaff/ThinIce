from rich.pretty import pprint
from .app import typerapp, panel_updown
from . import app
from typing_extensions import Annotated
import typer
import rich.progress
from pathlib import Path


@typerapp.command("upload", rich_help_panel=panel_updown,
             help='Upload file',
            epilog="""~~~shell\n
thinice complete\n
~~~
"""
)
def upload_file(path: Annotated[
    Path, 
    typer.Argument(file_okay=True, dir_okay=False, readable=True, exists=True)],
    description: Annotated[str, typer.Argument(help='Description (default and empty replaced to filename)')] = None,
    localdesc: Annotated[str, typer.Option('-l', help='Local description/comment (stored only locally, can be JSON)')] = None
    ):
    if description is None:
        description = path.name
    
    if path.stat().st_size < 4*1024*1024*1024:
        # simple upload
        with rich.progress.open(path, 'rb', description=f'upload {path}') as file_data:
                archive_id = app.vault.upload_stream(
                    stream=file_data,
                    description=description,
                    localdesc=localdesc
                    )
                print(f"Uploaded, archiveId is {archive_id!r}")
    else:
        # multipart upload for large file
        with rich.progress.open(path, 'rb', description=f'MP upload {path}') as file_data:
                archive_id = app.vault.upload_stream_multipart(
                    stream=file_data,
                    description=description,
                    localdesc=localdesc
                    )
                print(f"Uploaded, archiveId is {archive_id!r}")




