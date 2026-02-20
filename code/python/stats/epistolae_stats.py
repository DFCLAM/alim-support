from env import *
from pathlib import Path
import mariadb
import json
import csv
import re
from xml.etree import ElementTree
from saxonche import PySaxonProcessor

def generate_documents():
  letters_path = Path(EPISTOLAE_LETTERS_BASE_PATH)
  for letter_path in letters_path.iterdir():
      json_path = letter_path.joinpath('letter.json')
      with json_path.open('r') as json_fp:
        yield json.load(json_fp)

def measure(letter_json : dict):
        
    # Calculate measures from text
    # Simplest way of tokenization using split
    text = letter_json['original_letter']
    tokens = text.strip().split()
    computed_words = len(tokens)
    computed_characters_without_spaces = 0
    for token in tokens:
        computed_characters_without_spaces += len(token)

    return {
        'computed_words' : computed_words,
        'computed_characters_without_spaces' : computed_characters_without_spaces
    }

csv_letters_path = Path(ALIM_STATS_OUTPUT_BASE_PATH + '/epistolae_letters.csv')
fieldnames = ['id','url','title','computed_words','computed_characters_without_spaces']

with csv_letters_path.open('w') as csv_letters_fp:
    writer = csv.DictWriter(csv_letters_fp, fieldnames = fieldnames)
    writer.writeheader()
    for result in generate_documents():
        # print('\n##########################################################################################')
        # print(result['id'], result['title'])
        # print(measure(result['text'], result['xml_obj'], result['consistenza'], result['metadata']))
        result = result | measure(result)
        result = {k: v for k, v in result.items() if k in fieldnames}
        writer.writerow(result)
