import pathlib
from epistolae.letters_to_tei.load_women_and_people import read_person, populate_idnos
from epistolae.letters_to_tei.load_letter import read_letter_body, read_letter_front_matter
from itertools import chain
import json
import time
import re

# initialize common local paths for data input and output results

# the directory the epistolae's repo (https://github.com/DFCLAM/epistolae-hugo or https://github.com/ccnmtl/epistolae-hugo) is cloned to
epistolae_base_path = pathlib.Path.home().joinpath('tmp/epistolae')
epistolae_base_path = pathlib.Path(input("Epistolae path (defaults to %s): " % str(epistolae_base_path)) or str(epistolae_base_path))
if not epistolae_base_path.is_dir():
    raise  FileNotFoundError(epistolae_base_path)

epistolae_letters_path = epistolae_base_path.joinpath('content/letter')
epistolae_women_path = epistolae_base_path.joinpath('content/woman')
epistolae_people_path = epistolae_base_path.joinpath('content/people')

for testee_path in (epistolae_letters_path, epistolae_women_path, epistolae_people_path):
    if not testee_path.is_dir():
        raise FileNotFoundError(testee_path)
    
# the directory where results (TEI files) will be generated
output_base_path = pathlib.Path.home().joinpath('tmp/epistolae-alim')
output_base_path = pathlib.Path(input("Epistolae path (defaults to %s): " % str(output_base_path)) or str(output_base_path))
if not output_base_path.is_dir():
    raise FileNotFoundError(output_base_path)

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
        letter_dir = output_dir.joinpath(str(letter['id']))
        letter_dir.mkdir(exist_ok = True)
        output_file = letter_dir.joinpath('letter.json')
        with output_file.open('w') as output_fp:
            json.dump(letter, output_fp, indent = 4)
        