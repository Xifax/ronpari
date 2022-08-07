from pathlib import Path

from appdirs import AppDirs
from tinydb import Query
from tinydb import TinyDB

# Initialize user config
dirs = AppDirs("ronpari")
config = Path(dirs.user_config_dir)
if not config.exists():
    config.mkdir()

db = TinyDB(config / "db.json")


def update_user(user, password, path):
    User = Query()
    user_table = db.table("user")
    user_table.upsert(
        {"user": user, "password": password, "path": path}, User.user == user
    )


def get_user() -> dict:
    user = db.table("user")
    results = user.all()
    if results:
        return results[0]
    return {}


def get_path() -> str:
    user = get_user()
    if user:
        return user.get("path", "")
    return "~/Downloads"


def update_manga(
    title,
    manga_id=None,
    total_chapters=None,
    current_chapter=None,
    last_downloaded=None,
    chapter_map=None,
):
    Manga = Query()
    manga_table = db.table("manga")
    data = {
        "title": title,
    }

    if current_chapter is not None:
        data["current_chapter"] = current_chapter

    if chapter_map is not None:
        data["chapter_map"] = chapter_map

    if total_chapters is not None:
        data["total_chapters"] = total_chapters

    if last_downloaded is not None:
        data["last_downloaded"] = last_downloaded

    if manga_id is not None:
        data["manga_id"] = manga_id

    manga_table.upsert(data, Manga.title == title)


def get_manga() -> list:
    manga_table = db.table("manga")
    return manga_table.all()
