from app.api.challenge.v1.schema import ChallengeSummary, MissionSummary
from app.model.challenge import Challenge, ChallengeMission, Mission
from app.model.user_challenge import UserChallenge, UserMission
from app.module.challenge.enums import ChallengeStatusType, MissionStatusType


class ChallengeSerializer:
    @staticmethod
    def to_challenge_summary(
        challenge: Challenge,
        missions: list[Mission],
        challenge_missions: list[ChallengeMission],
        user_challenge: UserChallenge | None = None,
        user_missions: list[UserMission] | None = None,
        participant_counts: dict[int, int] | None = None,
    ) -> ChallengeSummary:
        user_mission_dict = {um.mission_id: um for um in user_missions} if user_missions else {}

        mission_summaries: list[MissionSummary] = []
        total_points = 0
        current_mission = None

        for cm in challenge_missions:
            mission = next((m for m in missions if m.id == cm.mission_id), None)
            if not mission:
                continue

            user_mission = user_mission_dict.get(mission.id)
            mission_status = user_mission.status if user_mission else MissionStatusType.NOT_STARTED

            if mission_status == MissionStatusType.IN_PROGRESS:
                current_mission = cm.step

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
                    status=mission_status,
                    participant=participant_count,
                )
            )
            total_points += mission.point

        if user_challenge:
            challenge_status = user_challenge.status
        else:
            challenge_status = ChallengeStatusType.NOT_STARTED
            current_mission = mission_summaries[0].step if mission_summaries else None

        return ChallengeSummary(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            status=challenge_status,
            current_mission_step=current_mission,
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
