from app.api.challenge.v1.schema import ChallengeSummary, MissionSummary
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
        participant_counts: dict[int, int] | None = None,
    ) -> ChallengeSummary:
        user_mission_dict = {um.mission_id: um for um in user_missions} if user_missions else {}

        mission_summaries: list[MissionSummary] = []
        total_points = 0
        current_mission_step = None

        for cm in challenge_missions:
            mission = next((m for m in missions if m.id == cm.mission_id), None)
            if not mission:
                raise ValueError("연동 된 미션 id {cm.mission_id}을 찾는데 실패 했습니다.")

            user_mission: UserMission | None = user_mission_dict.get(mission.id, None)

            if user_mission is None:
                raise ValueError("유저 미션 id {mission.id}가 존재하지 않습니다.")

            # 현재 미션 step 할당
            if user_mission.status == MissionStatusType.IN_PROGRESS:
                current_mission_step = cm.step

            participant_count = None
            if participant_counts:
                participant_count = participant_counts.get(mission.id)

            mission_summaries.append(
                MissionSummary(
                    id=mission.id,
                    title=mission.title,
                    description=mission.description,
                    step=cm.step,
                    point=mission.point,
                    status=user_mission.status,
                    participant=participant_count,
                )
            )
            total_points += mission.point

        return ChallengeSummary(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            status=user_challenge.status,
            current_mission_step=current_mission_step,
            missions=mission_summaries,
            total_points=total_points,
        )

    @staticmethod
    def to_challenge_summary_for_completed(
        challenge: Challenge,
        missions: list[Mission],
        challenge_missions: list[ChallengeMission],
        user_challenge: UserChallenge,
        user_missions: list[UserMission],
    ) -> ChallengeSummary:
        return ChallengeSerializer.to_challenge_summary(
            challenge=challenge,
            missions=missions,
            challenge_missions=challenge_missions,
            user_challenge=user_challenge,
            user_missions=user_missions,
            participant_counts=None,
        )
