from epistolae.letters_to_tei.env import *
from epistolae.letters_to_tei.load_women_and_people import read_person
from itertools import chain
import json
import csv

results = []

for path in epistolae_women_path.iterdir():
    person = read_person(path)
    if person:
        csv_row = {
            'label' : person['title'],
            'url' : person['url'],
            'date_of_birth' : person.get('birthdate'),
            'date_of_death' : person.get('deathdate')
        }
        results.append(csv_row)

with output_base_path.joinpath('openrefine.csv').open('w', newline='') as csv_fp:
    writer = csv.DictWriter(csv_fp, fieldnames=['url','label','date_of_birth','date_of_death'])
    writer.writeheader()
    writer.writerows(sorted(results, key = lambda row : row['label']))
