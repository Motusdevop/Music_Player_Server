from flask import Flask, request, send_file, render_template
import json
import os
import load
import db
import snippets

folder = os.getcwd()
app = Flask(__name__, template_folder=folder + "/html")
app.config["UPLOAD_FOLDER"] = "loads"

db.create_table()
db.create_fts5()

snippets.clear()

snippets_dict = snippets.get_snippets()

last_id = db.get_last_id()

if last_id is None:
    pass
else:
    tracks = list(range(1, last_id[0] + 1))


@app.route('/track')
def send_track():
    track_id = request.args.get('track_id')
    if int(track_id) in tracks:
        return send_file(f"music/{track_id}.mp3", as_attachment=True)
    else:
        return None


@app.route("/json")
def send_data():
    track_id = request.args.get('track_id')
    if int(track_id) in tracks:
        db_answer = db.get_music(int(track_id))
        dictory = {"track_id": db_answer[0], "title": db_answer[1], "artist": db_answer[2], "genre": db_answer[3]}
        with open("data_file.json", "w") as write_file:
            json.dump(dictory, write_file)
        return send_file("data_file.json", as_attachment=True)
    else:
        return None


@app.route("/search")
def search_track():
    search_text = request.args.get('search_text')
    db_answer = db.search(search_text)
    return db_answer


@app.route('/admin', methods=['POST', 'GET'])
def admin_panel():
    global tracks
    if request.method == "GET":
        return render_template("admin.html")
    else:
        f = request.files['file']
        f.save("loads.mp3")
        a = "done"
        load.load_track("loads.mp3")
        tracks = list(range(1, db.get_last_id()[0] + 1))
        return render_template("admin.html", a=a)


@app.route("/get_post_snippet", methods=["GET", "POST"])
def snippet():
    track_id = request.args.get('track_id')
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

        db.update_counts_of_listen(track_id=int(track_id))

        return snippets_dict[track_id]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
