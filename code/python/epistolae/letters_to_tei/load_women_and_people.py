import pathlib
from epistolae.utils.hugo_utils import parse_hugo_front_matter
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

def get_unique_result(label: str, woman: bool):
    """Search Wikidata for a person (wd:Q5) by english label,
    obtaining the record and optionally the VIAF and ISNI records.

    Parameters
    ----------
    label : str
        The english label of the Wikidata record to search.
    woman : bool
        If True, add the constraint for the person to be a woman (wd:Q6581072).
    """
    is_female_clause = "?item wdt:P21 wd:Q6581072 . # is female" if woman else ""
    response = wd.wd_query(search_human_by_title_sprql % (label, is_female_clause))
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
                comma_index = label.find(',')
                if comma_index > -1:
                    return get_unique_result(label[0:comma_index], woman)
    return None

def read_person(path : pathlib.Path):
    """Read the woman/person metadata from the front matter.
    
    Returns
    -------
    A dict with 
    `type` ("woman"|"person"), 
    `id`, 
    `title`, 
    `birthdate`, 
    `deathdate`, 
    `path` (of the original file), 
    `url` (original url from the epistolae's website),
    `proposed_idnos` (empty dict)
    """
    type : str = None
    id : int = None
    front_matter = parse_hugo_front_matter(path)
    if 'woman_id' in front_matter:
        type = "woman"
        id = front_matter['woman_id']
    elif 'people_id' in front_matter:
        type = "person"
        id = front_matter['people_id']
    else:
        return None
    true_id = int(path.name[:path.name.find('.')])
    if (true_id != id):
        id = true_id
    return {
        'type' :type, 
        'id' : id, 
        'title' : front_matter['title'], 
        'path' : str(path.absolute()), 
        'url' : "https://epistolae.unisi.it" + front_matter['url'],
        'birthdate' : front_matter.get('birthdate'),
        'deathdate' : front_matter.get('deathdate'),
        'proposed_idnos' : dict()
        }

def populate_idnos(person : dict):
    """Populate the person with their Authority IDs if able to find them

    Parameters
    ----------
    person : dict
        a dict in the format returned by read_person()
    """
    wikidata_binding = get_unique_result(person['title'], person['type'] == "woman")
    if wikidata_binding:
        person['proposed_idnos']['Wikidata'] = wikidata_binding['item']['value']
        if 'viaf' in wikidata_binding:
            person['proposed_idnos']['VIAF'] = wikidata_binding['viaf']['value']
        if 'isni' in wikidata_binding:
            person['proposed_idnos']['ISNI'] = wikidata_binding['isni']['value']      

