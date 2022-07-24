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


def update_manga(title, total_chapters, current_chapter, last_downloaded):
    Manga = Query()
    manga_table = db.table("manga")
    manga_table.upsert(
        {
            "title": title,
            "total_chapters": total_chapters,
            "current_chapter": current_chapter,
            "last_downloaded": last_downloaded,
        },
        Manga.title == title,
    )


def get_manga():
    manga_table = db.table("manga")
    return manga_table.all()
