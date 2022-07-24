import os
import shutil
from pathlib import Path
from typing import List
from urllib.parse import urlparse

# TODO: move to downloader?
import requests
from mangadex import Api
from mangadex import Chapter
from mangadex import Manga

# from MangaDexPy import Chapter
# from MangaDexPy import Manga
from MangaDexPy import MangaDex
from MangaDexPy import downloader
from rich.progress import track

from ronpari.store import get_user
from ronpari.terminal import console

api: Api = Api()
auth = {}


def get_client():
    # client = MangaDex()
    auth = get_user()
    # client.login(auth.get("user"), auth.get("password"))
    # return client
    # TODO: optionally login (get from ENV: login|passwd, if available -> login)

    # Another mangadex
    api.login(auth.get("user"), auth.get("password"))
    return api


def search_manga(title: str) -> List[Manga]:
    with console.status(f"Searching {title}..."):
        # return get_client().search(obj="manga", params={"title": title})
        return get_client().get_manga_list(title=title)


def get_volumes(manga: Manga) -> dict:
    # return api.get_manga_volumes_and_chapters(manga_id=manga.manga_id,
    #         kwargs={'translatedLanguage':'en'})
    return api.get_manga_volumes_and_chapters(
        manga_id=manga.manga_id, translatedLanguage="en"
    )


def get_chapter(chapter_id: str) -> Chapter:
    return api.get_chapter(chapter_id)


# def download_manga(manga: Manga) -> bool:
#     downloader.dl_manga(manga, base_path="/home/xifax/Downloads/test/")
#     # TODO: save status to DB if download is complete
#     return True


def download_chapter(manga: str, chapter: Chapter):
    images = chapter.fetch_chapter_images()
    if not images:
        console.print("[yellow]Could not get manga images![/yellow]")
        return

    # print(images)
    # return

    # TODO: refactor!
    auth = get_user()

    # TODO: check/create path
    chapter_path = Path(auth.get("path")) / manga / str(chapter.chapter)
    chapter_path.mkdir(parents=True, exist_ok=True)

    # TODO: sort by chapters or just get names from url?
    # images = sorted(images, key=lambda )

    # counter = 0
    for image_url in track(
        images, description=f"Downloading images to {str(chapter_path)}"
    ):
        res = requests.get(image_url, stream=True)

        if res.status_code == 200:
            # TODO: check extension!
            # TODO: optionally include chapter name, e.g. 26.0 ~ Chapter Name [volume?]

            url = urlparse(image_url)
            name = os.path.basename(url.path)
            number, postfix = name.split("-")
            _, extension = postfix.split(".")

            with open(str(chapter_path / f"{number}.{extension}"), "wb") as f:
                shutil.copyfileobj(res.raw, f)
            # counter += 1


# def download_chapter(chapter: Chapter) -> bool:
#     # TODO: get path from env
#     # downloader.threaded_dl_chapter(chapter, path="/home/xifax/Downloads/test/")
#     downloader.dl_chapter(chapter, path="/home/xifax/Downloads/test/")
#     # TODO: save status to DB if download is complete
#     return True
