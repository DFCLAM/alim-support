from enum import Enum

class Type(Enum):
    VIAF = "VIAF"
    ISNI = "ISNI"
    WIKIDATA = "Wikidata"

class IdNo:
    def __init__(self, type : Type, uri : str, code : str):
        self.type = type
        self.uri = uri
        self.code = code