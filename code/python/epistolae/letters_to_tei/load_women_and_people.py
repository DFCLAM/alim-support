import pathlib
from epistolae.utils.hugo_utils import parse_hugo_front_matter
from epistolae.letters_to_tei.dto.person import Person, PersonType
from epistolae.letters_to_tei.dto.idno import IdNo, IdNoType
import wikidata.wikidata_utils as wd

search_human_by_title_sprql = """
SELECT distinct ?item ?itemLabel ?itemDescription ?viaf ?isni WHERE{  
  ?item ?label "%s"@en .  
  ?item wdt:P31 wd:Q5 . # instance of human
  %s
  ?article schema:about ?item .
  ?article schema:inLanguage "en" .
  OPTIONAL { ?item wdt:P214 ?viaf . }
  OPTIONAL { ?item wdt:P213 ?isni . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
}
"""

def get_unique_result(title: str, woman: bool):
    is_female_clause = "?item wdt:P21 wd:Q6581072 . # is female" if woman else ""
    response = wd.wd_query(search_human_by_title_sprql % (title, is_female_clause))
    if (response.status_code == 200):
        responseObj = response.json()
        if ('results' in responseObj):
            results = responseObj['results']
            if ('bindings' in results):
                bindings = results['bindings']
                # avoid multiple, ambiguous results
                if len(bindings) == 1: 
                    if 'itemDescription' in bindings[0] and not 'disambiguation' in bindings[0]['itemDescription']['value']:
                        return bindings[0]
                comma_index = title.find(',')
                if comma_index > -1:
                    return get_unique_result(title[0:comma_index], woman)
    return None

def read_person(path : pathlib.Path):
    type : PersonType = None
    id : int = None
    front_matter = parse_hugo_front_matter(path)
    if 'woman_id' in front_matter:
        type = PersonType.WOMAN
        id = front_matter['woman_id']
    elif 'people_id' in front_matter:
        type = PersonType.PERSON
        id = front_matter['people_id']
    else:
        return None
    true_id = int(path.name[:path.name.find('.')])
    if (true_id != id):
        id = true_id
    return Person(type, id, front_matter['title'], path, "https://epistolae.unisi.it" + front_matter['url'], dict())

def populate_idnos(person : Person):
    wikidata_binding = get_unique_result(person.title, person.type == PersonType.WOMAN)
    if wikidata_binding:
        person.proposed_idnos[IdNoType.WIKIDATA] = IdNo(IdNoType.WIKIDATA, wikidata_binding['item']['value'], None)
        if 'viaf' in wikidata_binding:
            person.proposed_idnos[IdNoType.VIAF] = IdNo(IdNoType.VIAF, None, wikidata_binding['viaf']['value'])
        if 'isni' in wikidata_binding:
            person.proposed_idnos[IdNoType.VIAF] = IdNo(IdNoType.ISNI, None, wikidata_binding['isni']['value'])      

