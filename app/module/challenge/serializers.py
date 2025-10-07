from app.api.challenge.v1.schema import ChallengeSummary, MissionBasic, MissionSummary
from app.model.challenge import Challenge, ChallengeMission, Mission
from app.model.user_challenge import UserChallenge, UserMission
from app.module.challenge.enums import MissionStatusType


class ChallengeSerializer:
    @staticmethod
    def to_challenge_summary(
        challenge: Challenge,
        missions: list[Mission],
        challenge_missions: list[ChallengeMission],
        user_challenge: UserChallenge,
        user_missions: list[UserMission],
    ) -> ChallengeSummary:
        user_mission_dict = {um.mission_id: um for um in user_missions} if user_missions else {}

        mission_basics: list[MissionBasic] = []
        total_points = 0

        for cm in challenge_missions:
            mission = next((m for m in missions if m.id == cm.mission_id), None)
            if not mission:
                raise ValueError(f"연동 된 미션 id {cm.mission_id}을 찾는데 실패 했습니다.")

            user_mission: UserMission | None = user_mission_dict.get(mission.id, None)

            if user_mission is None:
                raise ValueError(f"유저 미션 id {mission.id}가 존재하지 않습니다.")

            mission_basics.append(
                MissionBasic(
                    id=mission.id,
                    title=mission.title,
                    step=cm.step,
                    status=user_mission.status,
                )
            )

            total_points += mission.point

        return ChallengeSummary(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            status=user_challenge.status,
            missions=mission_basics,
            total_points=total_points,
        )

    @staticmethod
    def to_current_mission_summary(
        missions: list[Mission],
        challenge_missions: list[ChallengeMission],
        user_missions: list[UserMission],
        headcount: int | None = None,
    ) -> MissionSummary | None:
        user_mission_dict = {um.mission_id: um for um in user_missions} if user_missions else {}

        for cm in challenge_missions:
            mission = next((m for m in missions if m.id == cm.mission_id), None)
            if not mission:
                raise ValueError(f"연동 된 미션 id {cm.mission_id}을 찾는데 실패 했습니다.")

            user_mission: UserMission | None = user_mission_dict.get(mission.id, None)

            if user_mission is None:
                raise ValueError(f"유저 미션 id {mission.id}가 존재하지 않습니다.")

            if user_mission.status == MissionStatusType.IN_PROGRESS:
                return MissionSummary(
                    id=mission.id,
                    title=mission.title,
                    description=mission.description,
                    step=cm.step,
                    point=mission.point,
                    status=user_mission.status,
                    type=mission.type,
                )

        return None

    @staticmethod
    def to_challenge_summary_for_completed(
        challenge: Challenge,
        missions: list[Mission],
        challenge_missions: list[ChallengeMission],
        user_challenge: UserChallenge,
        user_missions: list[UserMission],
    ) -> ChallengeSummary:
        user_mission_dict = {um.mission_id: um for um in user_missions} if user_missions else {}

        mission_basics: list[MissionBasic] = []
        total_points = 0

        for cm in challenge_missions:
            mission = next((m for m in missions if m.id == cm.mission_id), None)
            if not mission:
                raise ValueError(f"연동 된 미션 id {cm.mission_id}을 찾는데 실패 했습니다.")

            user_mission: UserMission | None = user_mission_dict.get(mission.id, None)

            if user_mission is None:
                raise ValueError(f"유저 미션 id {mission.id}가 존재하지 않습니다.")

            mission_basics.append(
                MissionBasic(
                    id=mission.id,
                    title=mission.title,
                    step=cm.step,
                    status=user_mission.status,
                )
            )
            total_points += mission.point

        return ChallengeSummary(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            status=user_challenge.status,
            missions=mission_basics,
            total_points=total_points,
        )
