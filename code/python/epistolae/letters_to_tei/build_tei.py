from epistolae.letters_to_tei.env import *
from epistolae.utils.file_utils import detox
from pathlib import Path
import chevron, json, re
from datetime import date
from babel.dates import format_date, format_datetime, format_time

tei_template_file = resources_base_path.joinpath('TEI_template_01.xml')
# print(tei_template_file.absolute)

with tei_template_file.open('r') as fp:
    template = fp.read()

def build_person(path : str) -> dict:
    with output_base_path.joinpath(path).open('r') as fp:
        person_json : dict = json.load(fp)
        return {
            'name' : person_json['title'],
            'url' : person_json['url'],
            'idno' : person_json['proposed_idnos'],
        }
        pass
    pass

def build_data(letter_path : Path) -> dict:

    with letter_path.open('r') as fp:
        letter_json : dict = json.load(fp)

    todaysdate : date = date.today()

    return {
        'front' : {
            'id' : letter_json['id'],
            'title' : letter_json['title'],
            'created' : {
                'iso' : letter_json['created'],
                'fmt_ita' : format_date(date.fromisoformat(letter_json['created']), locale = 'it'),
                'year' : date.fromisoformat(letter_json['created']).year
            },
            'modified' : {
                'iso' : letter_json['modified'],
                'fmt_ita' : format_date(date.fromisoformat(letter_json['modified']), locale = 'it')
            },
            'url' : letter_json['url'],
            'date' : letter_json.get('date'),
            'senders' : [build_person(path) for path in letter_json.get('senders') or []],
            'receivers' : [build_person(path) for path in letter_json.get('receivers') or []],
        },
        'body' : {
            'original_letter' : letter_json.get('original_letter'),
            'printed_source' : letter_json.get('printed_source'),
        },
        'elab' : {
            'date' : {
                'iso' : todaysdate.isoformat()
            }
        }
    }

def create_tei(letter_path : Path, tei_base_path : Path):

    hash = build_data(letter_path)
    
    with tei_base_path.joinpath('Epistola_' + str(hash['front']['id']) + '_' + detox(hash['front']['title']) + '.tei.xml').open('w') as fp:
        fp.write(chevron.render(template, hash))
        pass

tei_base_path = output_base_path.joinpath('TEI')
for path in output_base_path.joinpath('letters').iterdir():
    create_tei(path.joinpath('letter.json'), tei_base_path)
