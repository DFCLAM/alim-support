from dataclasses import dataclass
import enum
import pathlib

class PersonType(enum.Enum):
    WOMAN = "WOMAN"
    PERSON = "PERSON"

@dataclass(frozen=True)
class Person:
    type : PersonType
    id : int
    title : str
    path : pathlib.Path
    url : str
    proposed_idnos : dict
