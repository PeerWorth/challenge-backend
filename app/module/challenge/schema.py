from pydantic import BaseModel

from app.model.challenge import Challenge, ChallengeMission, Mission
from app.model.user_challenge import UserChallenge, UserMission


class CurrentChallengeData(BaseModel):
    challenge: Challenge
    missions: list[Mission]
    challenge_missions: list[ChallengeMission]
    user_challenge: UserChallenge
    user_missions: list[UserMission]
    headcount: int | None

    class Config:
        from_attributes = True
