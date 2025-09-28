"""챌린지 도메인 예외 정의"""


class ChallengeError(Exception):
    """챌린지 도메인 기본 예외"""

    pass


class ChallengeNotFoundError(ChallengeError):
    """챌린지를 찾을 수 없는 경우"""

    def __init__(self, challenge_id: int):
        self.challenge_id = challenge_id
        super().__init__(f"챌린지 {challenge_id}가 존재하지 않습니다.")


class MissionDataIncompleteError(ChallengeError):
    """미션 데이터가 불완전한 경우"""

    def __init__(self, challenge_id: int):
        self.challenge_id = challenge_id
        super().__init__(f"챌린지 {challenge_id}와 연계된 미션 데이터를 가져오는데 실패하였습니다.")


class MissionNotFoundError(ChallengeError):
    """미션을 찾을 수 없는 경우"""

    def __init__(self, mission_id: int):
        self.mission_id = mission_id
        super().__init__(f"미션 {mission_id}가 존재하지 않습니다.")


class UserChallengeNotFoundError(ChallengeError):
    """사용자 챌린지를 찾을 수 없는 경우"""

    def __init__(self, user_id: int, challenge_id: int):
        self.user_id = user_id
        self.challenge_id = challenge_id
        super().__init__(f"사용자 {user_id}의 챌린지 {challenge_id} 데이터를 찾을 수 없습니다.")
