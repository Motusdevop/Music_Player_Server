import db
from mutagen.easyid3 import EasyID3
import os


def load_track(path: str):
    global id
    try:
        mutagenfile = EasyID3(path)
        print(f"loading: {mutagenfile['title'][0]}")

        title = mutagenfile["title"][0]
        artist = mutagenfile["artist"][0]
        genre = mutagenfile["genre"][0].lower()

        result = db.add_music(title, artist, genre=genre)
        id = result[0]

        db.add_fts5(id, title + " - " + artist)

    except:
        pass

    with open(f"music/{id}.mp3", "wb") as f:
        with open(path, "rb") as old_file:
            f.write(old_file.read())

    os.remove(path)


if __name__ == '__main__':
    load_track("music/lol.mp3")
