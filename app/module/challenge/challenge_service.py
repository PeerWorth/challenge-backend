from app.database.generic_repository import GenericRepository
from app.model.challenge import Challenge


class ChallengeService:
    def __init__(self):
        self.challenge_repository = GenericRepository(Challenge)
