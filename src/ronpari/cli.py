import re
import subprocess
import threading
from pathlib import Path

# import rich_click as click
import click
import pretty_errors

# from rich.panel import Panel
from rich.prompt import Confirm
from rich.prompt import IntPrompt
from rich.prompt import Prompt

# from rich.tree import Tree
from rich.table import Table

# from ronpari.dex import download_manga
from ronpari.dex import download_chapter
from ronpari.dex import get_chapter
from ronpari.dex import get_manga_by_id
from ronpari.dex import get_volumes
from ronpari.store import get_manga
from ronpari.store import get_path
from ronpari.store import update_manga
from ronpari.store import update_user

from . import console
from . import search_manga

# from ronpari.viewer import view_image


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
@click.argument("title", required=False)
@click.option("-n", "--number", type=int)
def download(title, number):
    """
    Download specified chapter(s)
    """
    # TODO: fix
    if number:
        manga_list = get_manga()
        if number not in range(1, len(manga_list) + 1):
            console.print("[yellow]No such manga[/yellow]")
            return

        selected_manga = manga_list[number - 1]
        manga_title = selected_manga.get("title", "none")
        manga_id = selected_manga.get("manga_id", None)
        if manga_id is None:
            console.print(
                "[yellow]Download one chapter of this manga to update local data[/yellow]"
            )
            return
        selected_manga = get_manga_by_id(manga_id)
        if selected_manga is None:
            console.print("[yellow]No manga found![/yellow]")
            return

    else:

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
        manga_id=selected_manga.manga_id,
        total_chapters=len(chapter_map.keys()),
        current_chapter=numbers[0],
        last_downloaded=numbers[-1],
        chapter_map=chapter_map,
    )


@manga_cli.command()
@click.option("-r", "--refresh", is_flag=True, help="Fetch latest information")
def status(refresh):
    """
    Show active manga [marked so via download|search commands]
    """
    manga_list = get_manga()

    if refresh:
        # TODO: fetch latest manga chapter_map
        ...

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
@click.option(
    "-p",
    "--proceed",
    is_flag=True,
    help="Try to open next chapter when closing the image viewer",
)
@click.option(
    "-p", "--auto", is_flag=True, help="Automatically proceed to next chapter"
)
def read(number, chapter=None, proceed=False, auto=False):
    """
    Open next manga chapter in image viewer [optionally download]
    """

    # Select manga by number
    manga_list = get_manga()
    if number not in range(1, len(manga_list) + 1):
        console.print("[yellow]No such manga[/yellow]")
        return

    selected_manga = manga_list[number - 1]
    title = selected_manga.get("title", "none")
    chapter_map: dict = selected_manga.get("chapter_map", {})

    # Get latest chapter from config or cli argument
    active_chapter = selected_manga.get("current_chapter", "1.0")
    manga_path = Path(get_path()) / title
    console.print(manga_path)

    if chapter is not None:
        active_chapter = chapter

    # View active chapter, download next, exit
    if not proceed:
        _view_chapter(title, active_chapter, chapter_map)
        return

    # Open next chapter until prompted to quit
    next_chapter = active_chapter
    loop = True
    while loop:
        if auto:
            open_next_next_chapter = True
        else:
            open_next_next_chapter = Confirm.ask(
                f"Read chapter [red]{next_chapter}[/red]?"
            )

        if open_next_next_chapter:
            # Read next chapter (initially set to active chapter saved in config)
            next_chapter = _view_chapter(title, next_chapter, chapter_map)
        else:
            loop = False

    return
    # selected_chapter = _get_chapter(active_chapter, chapter_map)
    # path = Path(get_path()) / title / str(float(selected_chapter.get("chapter")))

    # Check if active chapter is downloaded and download if required
    path = _check_and_download(title, active_chapter, chapter_map)

    # # TODO: fix last downloaded
    # # last_downloaded = None
    # # Try to download next chapter
    # if not path.exists():
    #     selected_chapter = _get_chapter(active_chapter, chapter_map)
    #     manga_chapter = get_chapter(selected_chapter.get("id"))
    #     download_chapter(title, manga_chapter)
    #     # last_downloaded = chapter

    # Download next chapter in background
    console.print(path)
    threading.Thread(
        target=_download_in_background,
        name="Fetching next chapter",
        args=[title, active_chapter, chapter_map],
    ).start()

    # Open image viewer for current chapter path
    cmd = ["imv", str(path)]
    subprocess.Popen(cmd).wait()

    # To the next chapter!
    if proceed:
        open_next_next_chapter = Confirm.ask("Next chapter?")
        if open_next_next_chapter:
            cmd = ["imv", str(path)]
            subprocess.Popen(cmd).wait()

    return

    # next_chapter = _get_chapter(active_chapter, chapter_map)
    # available_chapters = sorted(
    #     chapter_map.keys(), key=lambda c: float(c) if c != "none" else 0.0
    # )
    # try:
    #     current_chapter_index = available_chapters.index(next_chapter.get("chapter"))
    #     next_chapter = available_chapters[current_chapter_index + 1]
    #     console.print(f"Next chapter is {next_chapter}")
    # except (ValueError, IndexError) as e:
    #     # TODO: print "NO NEXT CHAPTER" or something
    #     console.print(e)

    # Increment chapter according to chapter_map IF POSSIBLE
    next_chapter = _get_next_chapter(active_chapter, chapter_map)

    # When finished: update manga -> increment current chapter
    update_manga(
        title=title,
        current_chapter=next_chapter,
        # last_downloaded=last_downloaded,
    )


###################
# Utility methods #
###################


def _view_chapter(title, active_chapter, chapter_map) -> str | int | float:
    """
    View active chapter:
    1. Download if does not exist
    2. Try to download next one, if possible
    3. Open image viewer for the chapter files
    4. Increment active chapter according to chapter map
    """
    # Check if current chapter is available
    path = _check_and_download(title, active_chapter, chapter_map)

    # Download next one in background
    threading.Thread(
        target=_download_in_background,
        name="Fetching next chapter",
        args=[title, active_chapter, chapter_map],
    ).start()

    # Open image viewer for current chapter path
    cmd = ["imv", str(path)]
    subprocess.Popen(cmd).wait()

    # Increment chapter according to chapter_map IF POSSIBLE
    next_chapter = _get_next_chapter(active_chapter, chapter_map)

    # When finished: update manga -> increment current chapter
    update_manga(
        title=title,
        current_chapter=next_chapter,
    )

    return next_chapter


def _get_chapter(number: float | int | str, chapter_map: dict) -> dict:
    """
    Get chapter data as dict, check if key is something like 23 or 23.0 or 23.5
    """
    try:
        if number == int(number):
            number = int(number)
    except ValueError:
        ...
    return chapter_map[str(number)]


def _get_next_chapter(active_chapter, chapter_map) -> str | int | float:
    """
    Get next chapter number based on chapter map: [12, 13, 13.5, 14.0]
    """
    next_chapter = _get_chapter(active_chapter, chapter_map)
    available_chapters = sorted(
        chapter_map.keys(), key=lambda c: float(c) if c != "none" else 0.0
    )
    next_chapter_number: str | int | float = next_chapter.get("chapter", "0")

    try:
        current_chapter_index = available_chapters.index(next_chapter.get("chapter"))
        next_chapter_number = available_chapters[current_chapter_index + 1]
        # console.print(f"Next chapter is {next_chapter}")
    except (ValueError, IndexError) as e:
        # TODO: print "NO NEXT CHAPTER" or something
        console.print(e)

    return next_chapter_number


def _download_in_background(title, active_chapter, chapter_map):
    """
    Get next chapter and download it
    """
    # # TODO: move to separate function and refactor
    # next_chapter = _get_chapter(active_chapter, chapter_map)
    # available_chapters = sorted(
    #     chapter_map.keys(), key=lambda c: float(c) if c != "none" else 0.0
    # )
    # next_chapter_number: str|int|float = next_chapter.get('chapter', '0')
    #
    # # TODO: move into separate function!
    # try:
    #     current_chapter_index = available_chapters.index(next_chapter.get("chapter"))
    #     next_chapter_number = available_chapters[current_chapter_index + 1]
    #     # console.print(f"Next chapter is {next_chapter}")
    # except (ValueError, IndexError) as e:
    #     # TODO: print "NO NEXT CHAPTER" or something
    #     console.print(e)

    next_chapter_number = _get_next_chapter(active_chapter, chapter_map)

    _check_and_download(title, next_chapter_number, chapter_map)

    # # TODO: move to seprate function and refactor
    # selected_chapter = _get_chapter(next_chapter_number, chapter_map)
    # path = Path(get_path()) / title / str(float(selected_chapter.get("chapter", '')))
    #
    # # last_downloaded = None
    # # Try to download next chapter
    # if not path.exists():
    #     manga_chapter = get_chapter(selected_chapter.get("id", ''))
    #     download_chapter(title, manga_chapter)
    #     # last_downloaded = chapter


def _check_and_download(title, chapter_number, chapter_map) -> Path:
    """
    If no chapter data -> download it
    """
    selected_chapter = _get_chapter(chapter_number, chapter_map)
    path = Path(get_path()) / title / str(float(selected_chapter.get("chapter", "")))

    if not path.exists():
        manga_chapter = get_chapter(selected_chapter.get("id", ""))
        download_chapter(title, manga_chapter)

    return path


######################
# Additional methods #
######################


# @manga_cli.command()
# @click.argument("title")
# @click.option(
#     "--download",
#     default=False,
#     is_flag=True,
#     help="Prompt for downloading whole manga after search results",
# )
# @click.option(
#     "--read",
#     default=False,
#     is_flag=True,
#     help="Prompt for chapters to read after search results",
# )
# def search(title, download, read):
#     """
#     Search and optionally download|read manga
#     """
#     # TODO: move to separate function (modularize!)
#     found = search_manga(title)
#     for number, item in enumerate(found):
#         console.print(
#             f'[red]#{number+1}[/red] [bold]{item.title.get("en", "")}[/bold] '
#             f"[italic]{item.status}[/italic]"
#         )
#
#     if download:
#         number = IntPrompt.ask("Enter number to download")
#         if number not in range(1, len(found)):
#             console.print("[yellow]No such manga[/yellow]")
#             return
#
#         selected_manga = found[number - 1]
#         console.print(selected_manga)
#
#         # TODO: check that chapters are in english
#         chapters = list(
#             filter(lambda c: c.language == "en", selected_manga.get_chapters())
#         )
#         chapters = list(sorted(chapters, key=lambda c: c.published_at))
#
#         # download_chapter(chapters[0])
#         # download_manga(selected_manga)
#
#     if read:
#         number = IntPrompt.ask("Enter number to download")
#         if number not in range(1, len(found)):
#             console.print("[yellow]No such manga[/yellow]")
#             return
#
#         selected_manga = found[number - 1]
#
#         # Get available chapters
#         with console.status("Getting chapter list"):
#             chapters = list(
#                 filter(lambda c: c.language == "en", selected_manga.get_chapters())
#             )
#             console.print(f"Total chapters: {len(chapters)}")
#
#         chapter_number = IntPrompt.ask("Chapter to start at")
#
#         # TODO: create entry in db
#         update_manga(selected_manga.title.get("en"), len(chapters), chapter_number)
#
#         # TODO: optionally download said chapter
#         download_chapter(chapters[chapter_number - 1])


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
