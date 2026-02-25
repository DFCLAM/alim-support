from epistolae.letters_to_tei.env import *
import wikidata.wikidata_utils as wd
from pyexcel_ods3 import get_data
import time, json

ods_path = resources_base_path.joinpath('wikidata-matches').joinpath('OpenRefine_Epistolae-women-to-authority-ID_copy_01.ods')
with ods_path.open('rb') as ods_fp:
    ods_obj = get_data(ods_fp)

get_viaf_isni_byentity_id_sprql = """
SELECT DISTINCT ?viaf ?isni WHERE {
  OPTIONAL { wd:%s wdt:P214 ?viaf . }
  OPTIONAL { wd:%s wdt:P213 ?isni . }
}
"""

json_path = output_base_path.joinpath('women_authority_ids.json')
womans_authority_ids = {}
if json_path.exists():
    with json_path.open('r') as json_fp:
        womans_authority_ids = json.load(json_fp)

for (_, rows) in ods_obj.items():
    for row in rows:
        if (len(row) > 6):
            epistolae_url = row[0]
            epistolae_id = None
            if ('/' in epistolae_url):
                woman_filename = epistolae_url.split('/')[-1]
                if '.' in woman_filename:
                    epistolae_id = woman_filename.split('.')[0]

                    if not epistolae_id in womans_authority_ids: # incremental update

                        wikidata_url = None
                        if 'SÌ' != row[6].strip():
                            wikidata_url = row[7].strip() # Found by human (if any)
                        else:
                            wikidata_url = row[4].strip() # precedence to exact match
                            if not wikidata_url:
                                wikidata_url = row[5].strip()

                        if wikidata_url:

                            print (epistolae_url, wikidata_url)
                            
                            wikidata_entity_id = wikidata_url.split('/')[-1]
                            sprql = get_viaf_isni_byentity_id_sprql % (wikidata_entity_id, wikidata_entity_id)
                            # print (sprql)
                            
                            womans_authority_ids[epistolae_id] = {
                                'epistolae_url' : epistolae_url,
                                'wikidata_url' : wikidata_url,
                                'Wikidata' : wikidata_entity_id
                            }

                            response = wd.wd_query(sprql)
                            response.raise_for_status()
                            response_obj = response.json()
                            # print (response_obj)
                            if 'results' in response_obj and 'bindings' in response_obj['results']:
                                viafs = set()
                                isnis = set()
                                for binding in response_obj['results']['bindings']:
                                    if 'viaf' in binding:
                                        viafs.add(binding['viaf']['value'])
                                    if 'isni' in binding:
                                        isnis.add(binding['isni']['value'])

                            if len(viafs) == 1:
                                womans_authority_ids[epistolae_id]['VIAF'] = viafs.pop()
                            if len(isnis) == 1:
                                womans_authority_ids[epistolae_id]['ISNI'] = isnis.pop()

                            with output_base_path.joinpath('women_authority_ids.json').open('w') as json_fp:
                                json.dump(womans_authority_ids, json_fp, indent = 4)

                            time.sleep(1) # to avoid HTTP 429 Too Many Requests from wikidata