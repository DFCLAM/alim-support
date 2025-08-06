import pathlib
from epistolae.utils.hugo_utils import parse_hugo_front_matter, get_hugo_body
import wikidata.wikidata_utils as wd
import re
from xml.etree import ElementTree

def read_letter(path : pathlib.Path):
    """Read the woman/person metadata from the front matter
    
    Returns
    -------
    A dict with 
    `id`,
    `title`, 
    `date` (normalized where possible), 
    `path` (of the original file), 
    `url` (original url from the epistolae's website),
    `senders_ids` (list),
    `receivers_ids` (list),
    `text` (the original text of the letter)
    """

    front_matter : dict = parse_hugo_front_matter(path)

    id : int = int(front_matter.get("letter_id") or 0)
    true_id = int(path.name[:path.name.find('.')])
    if (true_id != id):
        id = true_id
    
    senders_ids = [sender["id"] for sender in front_matter.get("senders") or []]
    receivers_ids = [sender["id"] for sender in front_matter.get("receivers") or []]
    
    return {
        'id' : id, 
        'title' : front_matter['title'], 
        'path' : str(path.absolute()), 
        'url' : "https://epistolae.unisi.it" + front_matter['url'],
        'senders_ids' : senders_ids,
        'receivers_ids' : receivers_ids
        }

def populate_text(letter : dict):
    """Search the original text of the letter
    and, if found, put it in the `text` property 
    of the letter.

    Paramteres
    ----------
        a dict in the format returned by read_letter()
    """

    text = get_hugo_body(pathlib.Path(letter["path"]))
    match_from = re.compile(r'<h2[^>]*>\s*Original letter[^<]*</h2>').search(text)
    if match_from:
        text = text[match_from.span()[1]:]
        
        # The original text ends at the next <h2> section or at the end of the body
        match_to = re.compile(r'<h2').search(text)
        if match_to:
            text = text[:match_to.span()[0]]
        
        letter["text"] = text.strip()
