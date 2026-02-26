from epistolae.letters_to_tei.env import *
from epistolae.utils.file_utils import detox
from pathlib import Path
import chevron, json, re
from datetime import date
from babel.dates import format_date

tei_template = None # cache
def load_tei_template():
    global tei_template
    if not tei_template:
        with resources_base_path.joinpath('TEI_template_02.xml').open('r') as fp:
            tei_template = fp.read()
    return tei_template

women_authority_ids = None # cache
def load_woman_authority_ids(epistolae_id):
    global women_authority_ids
    if not women_authority_ids:
        with resources_base_path.joinpath('wikidata-matches').joinpath('women_authority_ids.json').open('r') as fp:
            women_authority_ids = json.load(fp)
    if epistolae_id in women_authority_ids:
        return women_authority_ids[epistolae_id]
    return None

def build_person(path : str) -> dict:

    with output_base_path.joinpath(path).open('r') as fp:
        person_json : dict = json.load(fp)
        url = person_json['url']
        idno = {}

        if 'woman' == person_json['type']:
            woman_authority_ids = load_woman_authority_ids(str(person_json['id']))
            if woman_authority_ids:
                if 'wikidata_url' in woman_authority_ids:
                    url = woman_authority_ids['wikidata_url']
                    idno['Wikidata'] = woman_authority_ids['Wikidata']
                if 'ISNI' in woman_authority_ids:
                    url = 'https://isni.org/isni/' + woman_authority_ids['ISNI'] # deliberately overwrite url
                    idno['ISNI'] = woman_authority_ids['ISNI']
                if 'VIAF' in woman_authority_ids:
                    url = 'http://viaf.org/viaf/' + woman_authority_ids['VIAF'] # deliberately overwrite url
                    idno['VIAF'] = woman_authority_ids['VIAF']

        return {
            'name' : person_json['title'],
            'url' : url,
            'idno' : idno,
        }

def measures(text : str) -> dict:

    # Strip xml tags out from words and characters count
    text = re.sub(r'<[^>]+>', ' ', text)

    words = text.split()
    characters_without_spaces = 0
    for word in words: characters_without_spaces += len(word)

    return {
        'words' : len(words),
        'characters_without_spaces' : characters_without_spaces
    }

def normalize(text : str):
    return re.sub(r'\s+', ' ', (text or '').strip())

def add_newlines(text : str, max_length : int):
    """Improve readability, avoiding single long lines"""

    last_index = 0
    def newline(match : re.Match):
        nonlocal last_index
        if (match.start() - last_index) >= max_length:
            last_index = match.end()
            return '\r\n        '
        return match.group()

    return re.sub(r'\s+', newline, text)

def add_paragraph_if_needed(text : str):
    """Add <p> tagg if absent, to produce a legal body content"""
    if not text.startswith('<p'):
        return '<p>\r\n        ' + text + '\r\n        </p>'
    return text

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
            'original_letter' : add_paragraph_if_needed(add_newlines(normalize(str(letter_json.get('original_letter'))), 120)),
            'printed_source' : normalize(str(letter_json.get('printed_source')).strip()),
        },
        'elab' : {
            'date' : {
                'iso' : todaysdate.isoformat(),
                'fmt_ita' : todaysdate.strftime(f'%d/%m/%Y')
            },
            'measures' : measures(letter_json.get('original_letter'))
        }
    }

def create_tei(letter_path : Path, tei_base_path : Path):

    hash = build_data(letter_path)
    
    with tei_base_path.joinpath('Epistola_' + str(hash['front']['id']) + '_' + detox(hash['front']['title']) + '.tei.xml').open('w') as fp:
        fp.write(chevron.render(load_tei_template(), hash))
        pass

tei_base_path = output_base_path.joinpath('TEI')
for path in output_base_path.joinpath('letters').iterdir():
    create_tei(path.joinpath('letter.json'), tei_base_path)
