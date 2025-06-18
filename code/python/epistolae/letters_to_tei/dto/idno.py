from dataclasses import dataclass
from enum import Enum

class IdNoType(Enum):
    VIAF = "VIAF"
    ISNI = "ISNI"
    WIKIDATA = "Wikidata"
    EP_WOMAN = "Epistolae woman_id"
    EP_PEOPLE = "Epistolae people_id"
    EP_LETTER = "Epistolae letter_id"

@dataclass(frozen=True)
class IdNo:
    type : IdNoType
    uri : str
    code : str
