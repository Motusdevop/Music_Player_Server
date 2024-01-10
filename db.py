import sqlite3


def create_table(path_to_db: str = "Music_db.db"):
    try:
        con = sqlite3.connect(path_to_db)
        cursor = con.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Music (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        genre TEXT,
        count_listens INT
        )
        ''')

        con.commit()
    except sqlite3.Error as er:
        print(f"Error: {er}")
    finally:
        con.close()
        print("connection closed")


def create_fts5(path_to_db: str = "Music_db.db") -> None:
    try:
        con = sqlite3.connect(path_to_db)
        cursor = con.cursor()

        cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS Music_fts5 USING fts5 (
        id,
        title
        )
        ''')

        con.commit()
    except sqlite3.Error as er:
        print(f"Error: {er}")
    finally:
        con.close()
        print("connection closed")


def add_fts5(track_id: int, title: str, path_to_db: str = "Music_db.db"):
    try:
        con = sqlite3.connect(path_to_db)
        cursor = con.cursor()

        cursor.execute('INSERT INTO Music_fts5 (id, title) VALUES (?, ?)', (track_id, title))
        con.commit()
    except sqlite3.Error as er:
        print(f"Error: {er}")
    finally:
        con.close()
        print("connection closed")


def add_music(title: str, artist: str, genre="NS", path_to_db: str = "Music_db.db"):
    try:
        con = sqlite3.connect(path_to_db)
        cursor = con.cursor()

        cursor.execute('INSERT INTO Music (title, artist, genre) VALUES (?, ?, ?, ?)', (title, artist, genre, 0))
        con.commit()
        cursor.execute('SELECT id FROM Music ORDER BY id DESC LIMIT 1')
        return cursor.fetchone()
    except sqlite3.Error as er:
        print(f"Error: {er}")
    finally:
        con.close()
        print("connection closed")


def update_counts_of_listen(path_to_db: str = "Music_db.db", track_id: int = 0) -> None:
    try:
        con = sqlite3.connect(path_to_db)
        cursor = con.cursor()

        cursor.execute('SELECT count_listens FROM Music WHERE id = ?', (track_id,))
        count_listens = cursor.fetchone()[0]

        count_listens += 1

        cursor.execute('UPDATE Music SET count_listens = ? WHERE id = ?', (count_listens, track_id))
        con.commit()

    except sqlite3.Error as er:
        print(f"Error: {er}")
    finally:
        con.close()
        print("connection closed")


def get_last_id(path_to_db: str = "Music_db.db"):
    try:
        con = sqlite3.connect(path_to_db)
        cursor = con.cursor()
        cursor.execute('SELECT id FROM Music ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        if result is None:
            return (1,)
        return result
    except sqlite3.Error as er:
        print(f"Error: {er}")
    finally:
        con.close()
        print("connection closed")


def get_music(track_id: int, path_to_db: str = "Music_db.db") -> None:
    try:
        con = sqlite3.connect(path_to_db)
        cursor = con.cursor()

        cursor.execute('SELECT * FROM Music WHERE id = ?', (track_id,))
        return cursor.fetchone()
    except sqlite3.Error as er:
        print(f"Error: {er}")
    finally:
        con.close()
        print("connection closed")


def search(search_text: str, path_to_db: str = "Music_db.db"):
    try:
        con = sqlite3.connect(path_to_db)
        cursor = con.cursor()

        cursor.execute('SELECT * FROM Music_fts5 WHERE title MATCH ? ORDER BY rank', (search_text,))
        return cursor.fetchall()
    except sqlite3.Error as er:
        print(f"Error: {er}")
    finally:
        con.close()
        print("connection closed")


if __name__ == "__main__":
    create_table()
    # add_music("Track-1", "NONAME", "POP")
    print(get_music(1))
