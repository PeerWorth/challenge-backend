from enum import StrEnum


class BadgeTypes(StrEnum):
    INITIAL = "initial"
    STREAK = "streak"
    COMPOUND = "compound"
    TIME = "time"


class BadgeNames(StrEnum):
    FIRST_STEP = "첫걸음"
    THREE_DAY_STREAK = "작심삼일 탈출"
    SEVEN_DAY_STREAK = "꾸준러"
    FIFTEEN_DAY_STREAK = "철벽 의지"
    THIRTY_DAY_STREAK = "갓생러"
    TEN_MISSIONS = "열정 만렙"
    THIRTY_MISSIONS = "절약 고수"
    FRIDAY = "불금엔 절약"
    EARLY_MORNING = "미라클 모닝"
