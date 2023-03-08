import os
import re
import shutil
from pathlib import Path
from typing import Dict
from typing import List
from urllib.parse import urlparse

import requests
from mangadex import Api
from mangadex import Chapter
from mangadex import Manga
from rich.progress import track

from ronpari.store import get_path
from ronpari.store import get_user
from ronpari.terminal import console

api: Api = Api()
auth: Dict[str, str] = {}


def get_client():
    auth = get_user()
    api.login(auth.get("user", ""), auth.get("password", ""))
    return api


def search_manga(title: str) -> List[Manga] | None:
    with console.status(f"Searching {title}..."):
        return get_client().get_manga_list(title=title)


def get_manga_by_id(manga_id: str) -> Manga | None:
    with console.status("Getting manga info..."):
        found_manga = get_client().get_manga_list(manga_id=manga_id)
        if found_manga:
            return found_manga[0]


def get_volumes(manga_id: str) -> dict:
    return api.get_manga_volumes_and_chapters(
        manga_id=manga_id, translatedLanguage="en"
    )


def get_chapter(chapter_id: str) -> Chapter:
    return api.get_chapter(chapter_id)


def download_chapter(manga: str, chapter: Chapter):
    images = chapter.fetch_chapter_images()
    if not images:
        console.print("[yellow]Could not get manga images![/yellow]")
        return

    path = get_path()

    chapter_path = Path(path) / manga / str(chapter.chapter)
    chapter_path.mkdir(parents=True, exist_ok=True)

    # TODO: move to downloader
    for image_url in track(images, description=f"Downloading to\n{str(chapter_path)}"):
        res = requests.get(image_url, stream=True)

        if res.status_code == 200:
            # TODO: optionally include chapter name, e.g. 26.0 ~ Chapter Name [volume?]

            url = urlparse(image_url)
            name = os.path.basename(url.path)
            number, postfix = name.split("-")
            _, extension = postfix.split(".")
            number = int(re.sub(r"\D", "", number))

            # Prefix number
            with open(str(chapter_path / f"{number:04}.{extension}"), "wb") as f:
                shutil.copyfileobj(res.raw, f)
