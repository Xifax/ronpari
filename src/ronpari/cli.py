import rich_click as click
from rich import inspect

# import click
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.prompt import Prompt

# from rich.tree import Tree
from rich.table import Table

# from ronpari.dex import download_manga
from ronpari.dex import download_chapter
from ronpari.dex import get_chapter
from ronpari.dex import get_volumes
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
    # TODO: move to separate function (modularize!)
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
        chapters = list(
            filter(lambda c: c.language == "en", selected_manga.get_chapters())
        )
        chapters = list(sorted(chapters, key=lambda c: c.published_at))

        # download_chapter(chapters[0])
        # download_manga(selected_manga)

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

        chapter_number = IntPrompt.ask("Chapter to start at")

        # TODO: create entry in db
        update_manga(selected_manga.title.get("en"), len(chapters), chapter_number)

        # TODO: optionally download said chapter
        download_chapter(chapters[chapter_number - 1])


@manga_cli.command()
def status():
    click.echo("Info from DB")
    manga_list = get_manga()
    # TODO: included downloaded [from file system] + current chapter
    for manga in manga_list:
        console.print(
            Panel(manga.get("title"), subtitle=str(manga.get("current_chapter")))
        )


@manga_cli.command()
def read():
    # TODO: show manga with numbers and exit
    # TODO: select manga by number (separate command)
    # TODO: read next or current chapter (logic?)
    # TODO: download if required
    click.echo("Reading manga")


@manga_cli.command()
@click.argument("title")
def download(title):
    """
    Download specified chapter(s)
    """
    found = search_manga(title)
    for number, item in enumerate(found):
        console.print(
            f'[red]#{number+1}[/red] [bold]{item.title.get("en", "")}[/bold] '
            f"[italic]{item.status}[/italic]"
        )

    if not found:
        console.print("[yellow]No manga found![/yellow]")
        return

    if len(found) > 1:
        number = IntPrompt.ask("Select manga")
        if number not in range(1, len(found)):
            console.print("[yellow]No such manga[/yellow]")
            return

        selected_manga = found[number - 1]
    # Skip prompt if only one manga found
    else:
        selected_manga = found[0]

    manga_title = selected_manga.title.get("en", "No Title")

    # Get available chapters
    with console.status("Getting chapter list"):

        # chapters = list(
        #     filter(lambda c: c.language == "en", selected_manga.get_chapters())
        # )

        # Or just count keys?
        volumes = get_volumes(selected_manga)
        # last_volume = max(map(lambda n: int(n) if n.isdigit() else 0, volumes.keys()))

        # TODO: variant with just last chapter?
        # all_chapters = []

        # tree = Tree(selected_manga.title.get("en"))
        table = Table(title=manga_title)
        table.add_column("Volume", style="magenta", justify="right")
        table.add_column("Chapters", style="cyan", justify="left")

        chapter_map = {}

        # TODO: maybe some other way?
        # volumes.pop("none")
        # for v in volumes.values():
        for k, v in volumes.items():
            # all_chapters.extend(list(v.get("chapters").keys()))
            # branch = tree.add(k)

            # chapters = ""
            chapters = []
            for chapter, contents in v.get("chapters").items():
                # branch.add(chapter)
                chapters.append(chapter)
                chapter_map[chapter] = contents
                # chapters += f"{chapter} "

            chapters = " ".join(reversed(chapters))
            table.add_row(k, chapters)

        # console.print(f"Total volumes: {last_volume}")
        # console.print(f"Available chapters: {all_chapters}")

        # console.print(tree)
        console.print(table)

    chapter_number = Prompt.ask("Chapter to download")
    selected_chapter = chapter_map[chapter_number]

    chapter = get_chapter(selected_chapter.get("id"))
    inspect(chapter)
    # console.print(chapter.fetch_chapter_images())

    # chapters = list(sorted(chapters, key=lambda c: c.published_at))

    # ch = chapters[chapter_number - 1]
    # inspect(ch)

    # TODO: maybe add last chapter?
    update_manga(manga_title, len(chapter_map.keys()), chapter.chapter)

    # TODO: allow to download range of chapters
    download_chapter(manga_title, chapter)


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
