import rich_click as click
from rich.panel import Panel
from rich.prompt import IntPrompt

from ronpari.dex import download_chapter
from ronpari.dex import download_manga
from ronpari.store import get_manga
from ronpari.store import update_manga
from ronpari.store import update_user

from . import console
from . import search_manga


@click.group()
def manga_cli():
    pass


@manga_cli.command()
@click.argument("title")
@click.option(
    "--download",
    default=False,
    is_flag=True,
    help="Prompt for downloading whole manga after search results",
)
@click.option(
    "--read",
    default=False,
    is_flag=True,
    help="Prompt for chapters to read after search results",
)
def search(title, download, read):
    found = search_manga(title)
    for number, item in enumerate(found):
        console.print(
            f'[red]#{number+1}[/red] [bold]{item.title.get("en", "")}[/bold] '
            f"[italic]{item.status}[/italic]"
        )

    if download:
        number = IntPrompt.ask("Enter number to download")
        if number not in range(1, len(found)):
            console.print("[yellow]No such manga[/yellow]")
            return

        selected_manga = found[number - 1]
        console.print(selected_manga)

        # TODO: check that chapters are in english
        # chapters = list(filter(lambda c: c.language == "en", selected_manga.get_chapters()))
        # download_chapter(chapters[0])
        download_manga(selected_manga)

    if read:
        number = IntPrompt.ask("Enter number to download")
        if number not in range(1, len(found)):
            console.print("[yellow]No such manga[/yellow]")
            return

        selected_manga = found[number - 1]

        # Get available chapters
        with console.status("Getting chapter list"):
            chapters = list(
                filter(lambda c: c.language == "en", selected_manga.get_chapters())
            )
            console.print(f"Total chapters: {len(chapters)}")

        number = IntPrompt.ask("Chapter to start at")

        # TODO: create entry in db
        update_manga(selected_manga.title.get("en"), len(chapters), number)

        # TODO: optionally download said chapter


@manga_cli.command()
def status():
    click.echo("Info from DB")
    manga_list = get_manga()
    for manga in manga_list:
        console.print(Panel(manga.get("title")))


@manga_cli.command()
def read():
    click.echo("Reading manga")


@manga_cli.command()
def download():
    # TODO: download manga or chapter
    click.echo("Downloading manga")


@manga_cli.command()
def path():
    click.echo("Set|get download path")


@manga_cli.command()
@click.argument("user")
@click.argument("password")
@click.argument("path")
def config(user, password, path):
    if user and password and path:
        update_user(user, password, path)
    else:
        console.print("[yellow]Please specify user+password+path[/yellow]")
