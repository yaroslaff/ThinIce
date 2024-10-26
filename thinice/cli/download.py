from rich.pretty import pprint
from .app import typerapp, panel_updown
from . import app
from typing_extensions import Annotated
import typer
import sys
from rich.progress import Progress
from pathlib import Path


@typerapp.command("request", rich_help_panel=panel_updown,
             help='Request file to download (from Cold to Warm)',
            epilog="""~~~shell\n
            # many files with this Description\n
            thinice request -m MyServer.tar.gz\n
            \n
            # one file with ArchiveId starting with this characters\n
            thinice request S93to\n
~~~
"""
)
def request_file(
        arc_spec: Annotated[str, typer.Argument(help='ArchiveId (first letters) or Description')] = None,
        multiple: Annotated[bool, 
            typer.Option('--multiple', '-m', help='Request multiple files at once')] = False,
        tier: Annotated[str, 
            typer.Option('--tier', '-t', help='Retrieval tier: Expedited (1-5min) / Standard (3-5hr, default) / Bulk (5-12hr)')] = "Standard"
    ):

    tier = tier.capitalize()

    if tier not in ['Expedited', 'Standard', 'Bulk']:
        print("Invalid tier, use Expedited / Standard / Bulk", file=sys.stderr)
        sys.exit(1)

    archives = app.vault.get_by_arc_spec(arc_spec)
    if not archives:
        print("No archives found")
        return
    
    if len(archives) > 1 and not multiple:
        print("More than one archive found, use archiveId for more accurate selection or use --multiple")
        sys.exit(1)
    
    for arc in archives:
        app.vault.request_download(archive_id=arc['ArchiveId'], tier=tier)

@typerapp.command("download", rich_help_panel=panel_updown,
             help='Download warm file',
            epilog="""~~~shell\n
            # file with this description MyServer.tar.gz will be saved as MyServer.tar.gz\n
            thinice download MyServer.tar.gz\n
            \n
            # one file with ArchiveId starting with this characters\n
            thinice download S93to myarchive.zip\n
~~~
"""
)
def download_file(
        arc_spec: Annotated[str, typer.Argument(help='ArchiveId (first letters) or Description or _all')] = None,
        path: Annotated[Path, typer.Argument(help='Download to this file')] = None,
        overwrite: Annotated[bool, 
            typer.Option('--overwrite', '-o', help='Overwrite if file exists')] = False
    ):


    def make_file_path(archive, path):
        if path:
            if path.is_dir():
                return path / archive['ArchiveDescription']
            else:
                return path
        else:
            return archive['ArchiveDescription']
        

    if arc_spec == "_all":
        archives = app.vault.list_archives()
    else:        
        if arc_spec:
            archives = app.vault.get_by_arc_spec(arc_spec)
        else:
            print("Need either archive specification (Description or first part of ArchiveId) or --all", file=sys.stderr)
            sys.exit(1)
    warm_archives = [item for item in archives if item.get("status") == "Warm"]
    
    if not warm_archives:
        print("No warm archives found")
        return


    if len(warm_archives) == 1:
        if path:
            if path.exists() and path.is_file() and not overwrite:
                print(f"File {path} exists, use --overwrite to overwrite")
                sys.exit(1)
        else:
            pass

    if len(warm_archives) > 1:
        # many archives, need sanity checks
        if path:
            print(f"Can not download {len(archives)} archives into one file. Download one by one.", 
                  file=sys.stderr)
        else:
            # path not given, check descriptions for all
            if any(item.get('desc', '') == '' for item in warm_archives):
                print(f"Can not download {len(archives)} archives, at least one has no description. Download one by one.",
                      file=sys.stderr)
                sys.exit(1)
    
    for archive in warm_archives:
        if path is None:
            path = Path(archive['ArchiveDescription'])
        if path.is_dir():
            path = path / archive['ArchiveDescription']
        
        if path.exists() and not overwrite:
            print(f"File {path} exists, use --overwrite to overwrite")
            sys.exit(1)

        #with Progress() as progress:
        #    task = progress.add_task(path, total=archive['Size'])

        with open(path, 'wb') as stream:
            with Progress() as progress:
                task = progress.add_task(path.name, total=archive['Size'])
                app.vault.download_job(job_id=archive['ArchiveRetrievalJob']['JobId'], stream=stream, 
                                       update_fn=lambda cnt: progress.update(task, completed=cnt))


        #app.vault.download_archive(archive_id=warm_archives[0]['ArchiveId'], path=path)