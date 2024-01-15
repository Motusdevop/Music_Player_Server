import json
from statistics import median


def get_snippets(path_to_snippets_json: str = "snippets.json") -> dict:
    try:
        with open(path_to_snippets_json) as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return dict()


def update_json(dictory: dict) -> None:
    try:
        with open("snippets.json", 'w') as f:
            f.write(json.dumps(dictory, indent=1))
    except:
        print("Error Update snippet json")


def clear() -> None:
    with open("snippets.json", 'w'):
        print("{}")


def create_seconds_zone(snippet_list: list[int], MIN_COUNT_OF_PLAYS_TO_CREATE_SNIPPET: int = 10,
                        MIN_MEDIAN_OF_PLAYS_TO_CREATE_SNIPPET: int = 1) -> tuple:  # Получаем зону сниппета
    if max(snippet_list) < MIN_COUNT_OF_PLAYS_TO_CREATE_SNIPPET or median(
            snippet_list) < MIN_MEDIAN_OF_PLAYS_TO_CREATE_SNIPPET:  # Условия создания сниппета
        return tuple()

    median_count = median(snippet_list)
    # print("median", median_count)

    zone = list()

    for i in range(len(snippet_list)):  # Ищем где кол-во прослушиваний больше медианного
        if snippet_list[i] > median_count:
            zone.append(i)

    # print(zone)

    zones = [list() for _ in range(5)]  # Создаём список зон с ограничение до 5 возможных

    count_zones = 0

    for i in range(len(zone)):

        if i + 1 == len(zone) or count_zones > 4:  # Если прошли весь список или кол-во зон слишком большое ломаем цикл
            break

        if zone[i] + 1 == zone[i + 1]:  # Если зона не прырывается то добавляем
            zones[count_zones].append(zone[i])

        else:
            count_zones += 1

    maximum_len = 0
    index = 0

    for i in zones:  # Ищем самую большую зону. Это и есть наш сниппет
        if len(i) > maximum_len:
            maximum_len = len(i)
            index = zones.index(i)

    Len: int = zones[index][-1] - zones[index][1]

    if Len > 60:
        zones[index][-1] = zones[index][0] + 60

    # print(index)

    return zones[index][0], zones[index][-1]


def get_snippet_list(id: int, path_to_snippets_json: str = "snippets.json") -> list[int]:
    snippet_dict = get_snippets(path_to_snippets_json=path_to_snippets_json)

    try:
        return snippet_dict[str(id)]
    except KeyError:
        return None
