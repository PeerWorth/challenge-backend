from enum import StrEnum


class MissionStatusType(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    @classmethod
    def get_status(cls, mission_step: int, current_mission_step: int) -> "MissionStatusType":
        if mission_step < current_mission_step:
            return cls.COMPLETED
        elif mission_step == current_mission_step:
            return cls.IN_PROGRESS
        else:
            return cls.NOT_STARTED


class ChallengeStatusType(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class MissionType(StrEnum):
    PHOTO = "photo"
    EVENT = "event"
    SERVICE = "service"
