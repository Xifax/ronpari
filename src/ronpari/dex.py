from typing import List

from MangaDexPy import Chapter
from MangaDexPy import Manga
from MangaDexPy import MangaDex
from MangaDexPy import downloader

from ronpari.store import get_user
from ronpari.terminal import console


def get_client():
    client = MangaDex()
    auth = get_user()
    client.login(auth.get("user"), auth.get("password"))
    return client
    # TODO: optionally login (get from ENV: login|passwd, if available -> login)


def search_manga(title: str) -> List[Manga]:
    with console.status(f"Searching {title}..."):
        return get_client().search(obj="manga", params={"title": title})


def download_manga(manga: Manga) -> bool:
    downloader.dl_manga(manga, base_path="/home/xifax/Downloads/test/")
    # TODO: save status to DB if download is complete
    return True


def download_chapter(chapter: Chapter) -> bool:
    # TODO: get path from env
    # downloader.threaded_dl_chapter(chapter, path="/home/xifax/Downloads/test/")
    downloader.dl_chapter(chapter, path="/home/xifax/Downloads/test/")
    # TODO: save status to DB if download is complete
    return True
