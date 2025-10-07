from fastapi import status


class ChallengeError(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "서버 오류"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail


class ChallengeNotFoundError(ChallengeError):
    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self, challenge_id: int):
        self.challenge_id = challenge_id
        super().__init__(f"챌린지 id {challenge_id}이 존재하지 않습니다.")


class MissionDataIncompleteError(ChallengeError):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, challenge_id: int):
        self.challenge_id = challenge_id
        super().__init__(f"챌린지 {challenge_id}와 연계된 미션 데이터를 가져오는데 실패하였습니다.")


class MissionNotFoundError(ChallengeError):
    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self, mission_id: int):
        self.mission_id = mission_id
        super().__init__(f"미션 {mission_id}가 존재하지 않습니다.")


class UserChallengeNotFoundError(ChallengeError):
    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self, user_id: int, challenge_id: int):
        self.user_id = user_id
        self.challenge_id = challenge_id
        super().__init__(f"사용자 {user_id}의 챌린지 {challenge_id} 데이터를 찾을 수 없습니다.")


class UserChallengeAlreadyInProgressError(ChallengeError):
    status_code: int = status.HTTP_409_CONFLICT

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"사용자 {user_id}는 이미 진행 중인 챌린지가 있습니다.")


class UserMissionNotInProgressError(ChallengeError):
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, user_id: int, mission_id: int):
        self.user_id = user_id
        self.mission_id = mission_id
        super().__init__(f"사용자 {user_id}는 미션 {mission_id}를 진행 중이 아닙니다.")


class ChallengeAlreadyCompletedError(ChallengeError):
    status_code: int = status.HTTP_409_CONFLICT

    def __init__(self, user_id: int, challenge_id: int):
        self.user_id = user_id
        self.challenge_id = challenge_id
        super().__init__(f"사용자 {user_id}는 이미 챌린지 {challenge_id}를 완료했습니다.")
