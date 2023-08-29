import json
from datetime import timedelta


def save_json_file(filename, json_content):
    with open(filename, 'w', encoding='utf8') as outfile:
        #json.dump(json_content, outfile, indent=4, sort_keys=True)
        json.dump(json_content, outfile, indent=4, sort_keys=True, ensure_ascii=False)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)
