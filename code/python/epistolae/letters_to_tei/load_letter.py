from pathlib import Path
from epistolae.utils.hugo_utils import parse_hugo_front_matter, read_hugo_body
import wikidata.wikidata_utils as wd
import re
from enum import Enum
from io import StringIO
from html.parser import HTMLParser
from xml.etree import ElementTree
from datetime import date

def read_letter_front_matter(path : Path):
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
    `printed_source` (the original printed_source of the letter)
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
        'created' : front_matter.get('created'), 
        'modified' : front_matter.get('modified'), 
        'path' : str(path.absolute()), 
        'url' : "https://epistolae.unisi.it" + front_matter['url'],
        'senders_ids' : senders_ids,
        'receivers_ids' : receivers_ids
        }

class BodyParser(HTMLParser):
    """Parse the body extracting relevant information, 
    transforming or removing HTML to achieve TEI compliance.
    
    References
    ----------
    https://docs.python.org/3/library/html.parser.html#html.parser.HTMLParser
    https://stackoverflow.com/a/925630
    """

    class FSA(Enum):
        NONE = 1
        H2_START = 2
        H2_END = 3
        ORIGINAL_LETTER_WORKING = 4
        PRINTED_SOURCE_WORKING = 5
        DATE_WORKING = 6

    def __init__(self, letter : dict):
        super().__init__()
        self.reset()
        self.letter = letter
        self.strict = False
        self.convert_charrefs = True
        self.original_letter = StringIO()
        self.printed_source = StringIO()
        self.date = ''
        self.fsa = self.FSA.NONE

    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
        fsa = self.fsa
        match (tag, fsa):
            case ("h2", _):
                self.fsa = self.FSA.H2_START
            case ("p", self.FSA.ORIGINAL_LETTER_WORKING):
                # maintains the <p> tag because it is supported by TEI
                self.original_letter.write("<p>")
            case ("br", self.FSA.ORIGINAL_LETTER_WORKING):
                # convert <br/> to TEI's <lb/>
                self.original_letter.write("<lb/>")

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        fsa = self.fsa
        match (tag, fsa):
            case ("p", self.FSA.ORIGINAL_LETTER_WORKING):
                # maintains the <p> tag because it is supported by TEI
                self.original_letter.write("</p>")
            case ("h2", self.FSA.H2_START):
                self.fsa = self.FSA.H2_END

    def handle_data(self, data):
        # print("Encountered some data  :", data)
        fsa = self.fsa
        match (fsa, data):
            case (self.FSA.H2_START, _) if "original letter" in data.lower():
                self.fsa = self.FSA.ORIGINAL_LETTER_WORKING
            case (self.FSA.H2_START, _) if "printed source" in data.lower():
                self.fsa = self.FSA.PRINTED_SOURCE_WORKING
            case (self.FSA.H2_START, _) if "date" in data.lower():
                self.fsa = self.FSA.DATE_WORKING
            case (self.FSA.ORIGINAL_LETTER_WORKING, _):
                self.original_letter.write(data)
            case (self.FSA.PRINTED_SOURCE_WORKING, _):
                self.printed_source.write(data)
            case (self.FSA.DATE_WORKING, _):
                self.date = data

    def close(self):
        super().close()
        self.letter["original_letter"] = self.original_letter.getvalue()
        self.letter["printed_source"] = self.printed_source.getvalue()
        self.letter["date"] = self.date

class DateParser:
    """A class representing the best effort result of the parsing of the date
    declared in a letter.
    """

    MONTHS_MAP = {
        "january" : "01", 
        "february" : "02", 
        "march" : "03", 
        "april" : "04", 
        "may" : "05", 
        "june" : "06",
        "july" : "07",  
        "august" : "08", 
        "september" : "09", 
        "october" : "10", 
        "november" : "11", 
        "december" : "12"
        }

    def __init__(self, original_value : str, value : date):
        self.original_value : str = original_value
        self.value : str = value

    def is_successfully_parsed() -> bool:
        return self.value is not None

def read_letter_body(letter : dict):
    """Search the original text of the letter
    and, if found, put it in the `text` property 
    of the letter.

    Paramteres
    ----------
        a dict in the format returned by read_letter_front_matter()
    """

    body_parser = BodyParser(letter)
    with Path(letter["path"]).open('r') as file:
        for line in read_hugo_body(file):
            body_parser.feed(line)
    body_parser.close()
