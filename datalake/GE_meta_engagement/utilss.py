import json
from datetime import timedelta, date


def save_json_file(filename, json_content):
    with open(filename, 'w', encoding='utf8') as outfile:
        #json.dump(json_content, outfile, indent=4, sort_keys=True)
        json.dump(json_content, outfile, indent=4, sort_keys=True, ensure_ascii=False)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def get_initial_date(start, frequency):
    if frequency == "WEEK":
        initial_date = start - timedelta(days=6)
    elif frequency == "MONTH":
        initial_date = date(start.year, start.month, 1)
    elif frequency == "QUARTER":
        start = start - timedelta(days=84)
        initial_date = date(start.year, start.month, 1)
    elif frequency == "YEAR":
        initial_date = date(start.year, 1, 1)
    else:
        pass  # TODO throw error

    return initial_date
