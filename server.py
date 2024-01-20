from flask import Flask, request, send_file, render_template, redirect, session
import json
import os
import load
import db
import snippets
import create_mp3

from config import ADMIN_PASSWORD, SECRET_KEY, MIN_COUNT_OF_PLAYS_TO_CREATE_SNIPPET, MIN_MEDIAN_OF_PLAYS_TO_CREATE_SNIPPET

folder = os.getcwd()
app = Flask(__name__, template_folder=folder + "/html", static_folder=folder + "/css")

app.config["UPLOAD_FOLDER"] = "loads"
app.config['SECRET_KEY'] = SECRET_KEY


db.create_table()
db.create_fts5()

snippets_dict = snippets.get_snippets()

last_id = db.get_last_id()

if last_id is None:
    tracks = list(0)
else:
    tracks = list(range(1, last_id[0] + 1))

path_to_snippets_json = 'snippets.json'
path_to_music = 'music/'
path_to_snippets_dict = 'snippets/'



def snippets_work(track_id: int) -> tuple:
    snippet_list = snippets.get_snippet_list(track_id, path_to_snippets_json=path_to_snippets_json)
    print(snippet_list)
    if snippet_list is None:
        return tuple()

    zone = snippets.create_seconds_zone(snippet_list,
                                        MIN_COUNT_OF_PLAYS_TO_CREATE_SNIPPET=MIN_COUNT_OF_PLAYS_TO_CREATE_SNIPPET,
                                        MIN_MEDIAN_OF_PLAYS_TO_CREATE_SNIPPET=MIN_MEDIAN_OF_PLAYS_TO_CREATE_SNIPPET)
    
    print(zone)
    
    return zone




@app.route('/')
def index():
    try:
        session['ADMIN']
    except KeyError:
        session['ADMIN'] = False
        
    return render_template('index.html', count=len(tracks))


@app.route('/track')
def send_track():
    track_id = request.args.get('track_id')
    if not track_id is None:
        try:
            return send_file(f"music/{track_id}.mp3", as_attachment=True)
        except FileNotFoundError:
            return '<link rel="stylesheet" href="../css/style.css"><h2>Такого трека нет</h2>'


@app.route("/json")
def send_data():
    track_id = request.args.get('track_id')
    if track_id:
        if int(track_id) in tracks:
            db_answer = db.get_music(int(track_id))
            dictory = {"track_id": db_answer[0], "title": db_answer[1], "artist": db_answer[2], "genre": db_answer[3]}
            with open("data_file.json", "w") as write_file:
                json.dump(dictory, write_file)
            return send_file("data_file.json", as_attachment=True)
        else:
            return None
    else:
        return None


@app.route("/search")
def search_track():
    search_text = request.args.get('search_text')
    db_answer = db.search(search_text)
    return db_answer


@app.route('/admin', methods=['POST', 'GET'])
def admin_panel():
    try:
        if session['ADMIN']:
            global tracks
            if request.method == "GET":
                return render_template("admin.html")
            else:
                try:
                    f = request.files['file']
                    f.save("loads.mp3")
                    a = "done"
                    load.load_track("loads.mp3")
                    tracks = list(range(1, db.get_last_id()[0] + 1))
                except:
                    a = 'error'
                return render_template("admin.html", a=a)
        else:
            return redirect('/auth')
    except KeyError:
        return redirect('/auth')


@app.route("/get_post_snippet", methods=["GET", "POST"])
def snippet():
    track_id = request.args.get('track_id')
    if track_id:
        if request.method == "GET":
            try:
                return snippets_dict[track_id]
            except KeyError:
                return "None"
        else:
            new_snippet = request.get_json()
            for key in new_snippet.keys():
                snippets_dict[key] = new_snippet[key]

            print(snippets_dict[track_id])

            snippets.update_json(snippets_dict)

            # db.update_counts_of_listen(track_id=int(track_id))

            return snippets_dict[track_id]
    else:
        return None

@app.route('/auth', methods=["GET", "POST"])
def auth():
    if request.method == 'GET':
        return render_template('auth.html', alert='')
    
    else:
        password = request.form.get('password')

        if password == ADMIN_PASSWORD:
            session['ADMIN'] = True
            return redirect('/admin')
        
        else:
            session['ADMIN'] = False
            return render_template('auth.html', alert='Неверный пароль')

@app.route('/get_snippet')
def get_snippet_file():
    try:
        track_id = request.args.get('track_id')
        if int(track_id) in tracks:
            zone = snippets_work(track_id=int(track_id))

            if zone:

                print('zone 0:', zone[0])
                print('zone 1:', zone[1])

                create_mp3.create(path_to_music + track_id + ".mp3", zone[0], zone[1], path_to_snippets_dict)

                return send_file(f"snippets/snippet_{track_id}.mp3", as_attachment=True)

            else:
                return '<link rel="stylesheet" href="../css/style.css"><h2>Сниппет не готов</h2>'

        else:
            return '<link rel="stylesheet" href="../css/style.css"><h2>Такого трека нет</h2>'
    except ValueError:
        return '<link rel="stylesheet" href="../css/style.css"><h2>Такого трека нет</h2>'



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
