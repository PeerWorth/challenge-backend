from enum import StrEnum


class AgreeTypes(StrEnum):
    TERM_OF_USE = "term_of_use"
    PERSONAL_INFO = "personal_info"
    MARKETING = "marketing"


class GenderTypes(StrEnum):
    MAN = "man"
    WOMAN = "woman"
