from epistolae.letters_to_tei.env import *
from epistolae.letters_to_tei.load_women_and_people import read_person, populate_idnos
from epistolae.letters_to_tei.load_letter import read_letter_body, read_letter_front_matter
from itertools import chain
import json
import time
import re
import csv

for path in chain(epistolae_women_path.iterdir(), epistolae_people_path.iterdir()):
    person = read_person(path)
    if person:
        match person['type']:
            case "woman":
                output_dir = output_base_path.joinpath('women')
            case "person":
                output_dir = output_base_path.joinpath('people')
        output_dir = output_dir.joinpath(str(person['id']))
        if not output_dir.exists():
            populate_idnos(person)
            time.sleep(1) # to avoid HTTP 429 Too Many Requests from wikidata
            output_dir.mkdir()
            output_file = output_dir.joinpath('metadata.json')
            with output_file.open('w') as output_fp:
                json.dump(person, output_fp, indent = 4)

output_dir = output_base_path.joinpath('letters')
file_filter = re.compile(r'[0-9]+\.html\.md')
for path in epistolae_letters_path.iterdir():
    if (file_filter.match(path.name)):
        # print (path)
        letter = read_letter_front_matter(path)
        read_letter_body(letter)
        # print (letter)
        # if not letter.get("original_letter"):
        #     print(letter.get("url"))
        letter_dir = output_dir.joinpath(str(letter['id']))
        letter_dir.mkdir(exist_ok = True)
        output_file = letter_dir.joinpath('letter.json')
        with output_file.open('w') as output_fp:
            json.dump(letter, output_fp, indent = 4)
        
results = []
for path in chain(output_base_path.joinpath('women').iterdir(), output_base_path.joinpath('people').iterdir()):
    with path.joinpath('metadata.json').open('r') as json_fp:
        json_obj = json.load(json_fp)
        if 'proposed_idnos' in json_obj:
            if 'Wikidata' in json_obj['proposed_idnos']:
                csv_row = {'URL' : json_obj['url'], 'Wikidata' : json_obj['proposed_idnos']['Wikidata']}
                if 'VIAF' in json_obj['proposed_idnos']:
                    csv_row['VIAF'] = json_obj['proposed_idnos']['VIAF']
                if 'ISNI' in json_obj['proposed_idnos']:
                    csv_row['ISNI'] = json_obj['proposed_idnos']['ISNI']
                results.append(csv_row)
                # print(json_obj['proposed_idnos']['Wikidata'])

with output_base_path.joinpath('idnos.csv').open('w', newline='') as csv_fp:
    writer = csv.DictWriter(csv_fp, fieldnames=['URL','Wikidata','VIAF','ISNI'])
    writer.writeheader()
    writer.writerows(results)

"""
original_dates = set()
date_formats = dict()
for path in output_base_path.joinpath('letters').iterdir():
    with path.joinpath('letter.json').open('r') as json_fp:
        json_obj = json.load(json_fp)
        if 'date' in json_obj:
            original_dates.add(json_obj['date'])
for original_date in original_dates:
    original_date = str(original_date).strip().lower()
    original_date = re.sub('[0-9]', 'x', original_date)
    original_date = re.sub('january|february|march|april|may|june|july|august|september|october|november|december', 'MONTH', original_date)
    date_formats[original_date] = date_formats.get(original_date, 0) + 1
with output_base_path.joinpath('date_formats.txt').open('w', newline='') as date_formats_fp:
    date_formats_fp.writelines(str(date_formats[date_format]) + " : " + date_format + "\n" for date_format in sorted(date_formats, key = date_formats.get, reverse = True))
"""
