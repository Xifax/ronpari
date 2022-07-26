import re
from pathlib import Path

# import rich_click as click
import click
import pretty_errors

# from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.prompt import Prompt

# from rich.tree import Tree
from rich.table import Table

# from ronpari.dex import download_manga
from ronpari.dex import download_chapter
from ronpari.dex import get_chapter
from ronpari.dex import get_volumes
from ronpari.store import get_manga
from ronpari.store import get_path
from ronpari.store import update_manga
from ronpari.store import update_user
from ronpari.viewer import view_image

from . import console
from . import search_manga

# from rich import inspect


@click.group(invoke_without_command=True)
@click.pass_context
def manga_cli(ctx):
    # Show status if no argument provided
    if ctx.invoked_subcommand is None:
        status()
    # Otherwise call the specified subcommand
    else:
        pass


###################
# Primary methods #
###################


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

    chapter_number = Prompt.ask("Chapter(s) to download (1 2 5 or 2..10)")

    # Fill chapter numbers from X..Y
    if ".." in chapter_number:
        start, end = re.split(r"\.\.", chapter_number)
        # TODO: how to populate chapters like '31.5'?
        # TODO: Consult with chapter_map?
        numbers = list(range(int(start), int(end) + 1))
        # Convert to string for convenience
        numbers = list(map(str, numbers))
    # Otherwise separate by delimeters
    elif "," in chapter_number:
        numbers = chapter_number.split(",")
    elif " " in chapter_number:
        numbers = chapter_number.split()
    # Or consider it single chapter
    else:
        numbers = [chapter_number]

    for n in numbers:
        selected_chapter = chapter_map[n.strip()]
        chapter = get_chapter(selected_chapter.get("id"))
        download_chapter(manga_title, chapter)

    update_manga(
        manga_title,
        total_chapters=len(chapter_map.keys()),
        current_chapter=numbers[0],
        last_downloaded=numbers[-1],
        chapter_map=chapter_map,
    )


@manga_cli.command()
def status():
    """
    Show active manga [marked so via download|search commands]
    """
    manga_list = get_manga()

    # TODO: included downloaded [from file system] + current chapter
    for i, manga in enumerate(manga_list):
        chapter_map = manga.get("chapter_map", {})
        if chapter_map:
            last_chapter = list(chapter_map.keys())[0]
        else:
            last_chapter = "???"

        console.print(
            f"[red]#{i+1}[/red] {manga.get('title')} "
            f"[italic]{manga.get('current_chapter')}[/italic] / {last_chapter} [black][{manga.get('total_chapters')}][/black]"
        )


@manga_cli.command()
@click.argument("number", type=int)
@click.argument("chapter", type=float, required=False)
# @click.option("-i", "--imv", is_flag=True)
def read(number, chapter=None):
    """
    Open next manga chapter in image viewer [optionally download]
    """
    # TODO: read next or current chapter (logic?)

    manga_list = get_manga()
    if number not in range(1, len(manga_list) + 1):
        console.print("[yellow]No such manga[/yellow]")
        return

    selected_manga = manga_list[number - 1]
    title = selected_manga.get("title", "none")
    active_chapter = selected_manga.get("current_chapter", "1.0")
    console.print(title, active_chapter)

    if chapter is not None:
        active_chapter = chapter

    print(chapter)

    path = Path(get_path()) / title / str(active_chapter)

    last_downloaded = None
    # Try to download next chapter
    if not path.exists():
        chapter_map: dict = selected_manga.get("chapter_map", {})
        if active_chapter == int(active_chapter):
            active_chapter = int(active_chapter)
        selected_chapter = chapter_map[str(active_chapter)]
        manga_chapter = get_chapter(selected_chapter.get("id"))
        download_chapter(title, manga_chapter)
        last_downloaded = chapter

    # if imv:
    import subprocess

    cmd = ["imv", str(path)]
    subprocess.Popen(cmd).wait()

    # TODO: when finished: update manga -> increment current chapter
    update_manga(
        title=title,
        # TODO: increment according to chapter_map IF POSSIBLE
        current_chapter=active_chapter,
        last_downloaded=last_downloaded,
    )

    # image_path = str(path / "0001.png")
    # view_image(image_path)


###################
# Utility methods #
###################


######################
# Additional methods #
######################


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
    """
    Search and optionally download|read manga
    """
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
def path():
    """
    Get path to chapters for specified manga or root folder
    """
    ...


@manga_cli.command()
@click.argument("user")
@click.argument("password")
@click.argument("path")
def config(user, password, path):
    if user and password and path:
        update_user(user, password, path)
    else:
        console.print("[yellow]Please specify user+password+path[/yellow]")
