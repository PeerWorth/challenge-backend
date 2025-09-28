from app.api.challenge.v1.schema import ChallengeSummary, MissionSummary
from app.model.challenge import Challenge, ChallengeMission, Mission
from app.model.user_challenge import UserChallenge, UserMission
from app.module.challenge.enums import ChallengeStatusType, MissionStatusType


class ChallengeSerializer:
    @staticmethod
    def to_challenge_summary_for_current(
        challenge: Challenge,
        missions: list[Mission],
        challenge_missions: list[ChallengeMission],
        user_challenge: UserChallenge,
        user_missions: list[UserMission],
        participant_counts: dict[int, int] | None = None,
    ) -> ChallengeSummary:
        user_mission_dict = {um.mission_id: um for um in user_missions}

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

            # 현재 진행 중인 미션(IN_PROGRESS)에만 참여 인원 할당
            participant_count = None
            if mission_status == MissionStatusType.IN_PROGRESS and participant_counts:
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

        return ChallengeSummary(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            status=user_challenge.status,
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
        user_mission_dict = {um.mission_id: um for um in user_missions}

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

            mission_summaries.append(
                MissionSummary(
                    id=mission.id,
                    title=mission.title,
                    description=mission.description,
                    step=cm.step,
                    point=mission.point,
                    status=mission_status,
                    participant=None,  # 완료된 챌린지는 참여자 수 비표시
                )
            )
            total_points += mission.point

        return ChallengeSummary(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            status=user_challenge.status,
            current_mission_step=current_mission,
            missions=mission_summaries,
            total_points=total_points,
        )

    @staticmethod
    def to_initial_challenge_summary(
        challenge: Challenge,
        missions: list[Mission],
        challenge_missions: list[ChallengeMission],
        first_mission_participant_count: int | None = None,
    ) -> ChallengeSummary:
        mission_summaries: list[MissionSummary] = []
        total_points = 0

        for cm in challenge_missions:
            mission = next((m for m in missions if m.id == cm.mission_id), None)
            if not mission:
                continue

            # 첫 번째 미션(step=1)에만 참여 인원 수 할당
            participant_count = None
            if cm.step == 1:
                participant_count = first_mission_participant_count

            mission_summaries.append(
                MissionSummary(
                    id=mission.id,
                    title=mission.title,
                    description=mission.description,
                    step=cm.step,
                    point=mission.point,
                    status=MissionStatusType.NOT_STARTED,
                    participant=participant_count,
                )
            )
            total_points += mission.point

        current_mission_step = mission_summaries[0].step if mission_summaries else None

        return ChallengeSummary(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            status=ChallengeStatusType.NOT_STARTED,
            current_mission_step=current_mission_step,
            missions=mission_summaries,
            total_points=total_points,
        )
