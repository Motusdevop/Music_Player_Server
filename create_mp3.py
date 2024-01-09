from pydub import AudioSegment


def create(path_to_track: str, start: int, end: int, path_to_snippets: str):
    audio_file = AudioSegment.from_file(path_to_track)
    start_time = start * 1000  # начало обрезки в миллисекундах
    end_time = end * 1000  # конец обрезки в миллисекундах

    filename = path_to_track.split("/")[-1]

    print(id)

    trimmed_audio = audio_file[start_time:end_time]
    trimmed_audio.export(path_to_snippets + "snippet_" + filename, format="mp3")


if __name__ == '__main__':
    create("music/1.mp3", 15, 30, "../snippets/")
