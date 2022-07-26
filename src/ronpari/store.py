from tinydb import Query
from tinydb import TinyDB

db = TinyDB("db.json")


def update_user(user, password, path):
    User = Query()
    user_table = db.table("user")
    user_table.upsert(
        {"user": user, "password": password, "path": path}, User.user == user
    )


def get_user():
    user = db.table("user")
    results = user.all()
    if results:
        return results[0]


def get_path() -> str:
    user = get_user()
    if user:
        return user.get("path", "")
    return ""


def update_manga(
    title,
    total_chapters=None,
    current_chapter=None,
    last_downloaded=None,
    chapter_map=None,
):
    Manga = Query()
    manga_table = db.table("manga")
    data = {
        "title": title,
        "current_chapter": current_chapter,
    }
    if chapter_map is not None:
        data["chapter_map"] = chapter_map

    if total_chapters is not None:
        data["total_chapters"] = total_chapters

    if last_downloaded is not None:
        data["last_downloaded"] = last_downloaded

    manga_table.upsert(data, Manga.title == title)


def get_manga():
    manga_table = db.table("manga")
    return manga_table.all()
