#!/usr/bin/env python
"""
챌린지 시드 데이터를 DB에 추가하는 스크립트

사용법:
    python scripts/seed_challenges.py              # 모든 데이터 추가
    python scripts/seed_challenges.py --clear      # 기존 데이터 삭제 후 추가
    python scripts/seed_challenges.py --dry-run    # 실행 시뮬레이션 (DB 변경 없음)
"""

import asyncio
import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import delete, select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.data.challenge.challenges import CHALLENGES_DATA  # noqa: E402
from app.database.config import get_async_session_maker  # noqa: E402
from app.model.challenge import Challenge, ChallengeMission, Mission  # noqa: E402


class ChallengeSeedRunner:
    def __init__(self, session: AsyncSession, dry_run: bool = False):
        self.session = session
        self.dry_run = dry_run
        self.created_challenges: list[Challenge] = []
        self.created_missions: list[Mission] = []
        self.created_mappings: list[ChallengeMission] = []

    async def clear_existing_data(self):
        """기존 챌린지 데이터 삭제"""
        if self.dry_run:
            print("[DRY RUN] 기존 데이터 삭제 생략")
            return

        print("기존 데이터 삭제 중...")

        # 순서 중요: 참조 관계 때문에 역순으로 삭제
        await self.session.execute(delete(ChallengeMission))
        await self.session.execute(delete(Mission))
        await self.session.execute(delete(Challenge))
        await self.session.commit()

        print("기존 데이터 삭제 완료")

    async def seed_challenges(self):
        """챌린지 데이터 시드"""
        print(f"\n총 {len(CHALLENGES_DATA)}개의 챌린지를 추가합니다...")

        for challenge_data in CHALLENGES_DATA:
            await self._create_challenge_with_missions(challenge_data)

        if not self.dry_run:
            await self.session.commit()
            print("\n✅ 데이터베이스 커밋 완료")

        # 결과 요약
        print("\n" + "=" * 50)
        print("📊 시드 결과 요약")
        print("=" * 50)
        print(f"✅ 생성된 챌린지: {len(self.created_challenges)}개")
        print(f"✅ 생성된 미션: {len(self.created_missions)}개")
        print(f"✅ 생성된 연결: {len(self.created_mappings)}개")

    async def _create_challenge_with_missions(self, data: dict):
        """챌린지와 미션들을 생성하고 연결"""
        # 1. 챌린지 생성
        challenge = Challenge(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            goal=data["goal"],
        )

        if self.dry_run:
            print(f"\n[DRY RUN] 챌린지 생성: {challenge.title}")
        else:
            self.session.add(challenge)
            await self.session.flush()
            print(f"\n✅ 챌린지 생성: {challenge.title}")

        self.created_challenges.append(challenge)

        # 2. 미션들 생성 및 연결
        for mission_data in data["missions"]:
            mission = await self._create_mission(mission_data)
            await self._link_challenge_mission(challenge.id, mission.id, mission_data["step"])

    async def _create_mission(self, mission_data: dict) -> Mission:
        """개별 미션 생성"""
        mission = Mission(
            title=mission_data["title"],
            description=mission_data["description"],
            type=mission_data["type"],
            point=mission_data["point"],
        )

        if self.dry_run:
            print(f"  [DRY RUN] 미션 생성: {mission.title} ({mission.point}P)")
        else:
            self.session.add(mission)
            await self.session.flush()
            print(f"  ✅ 미션 생성: {mission.title} ({mission.point}P)")

        self.created_missions.append(mission)
        return mission

    async def _link_challenge_mission(self, challenge_id: int, mission_id: int, step: int):
        """챌린지-미션 연결"""
        mapping = ChallengeMission(
            challenge_id=challenge_id,
            mission_id=mission_id,
            step=step,
        )

        if self.dry_run:
            print(f"    [DRY RUN] 연결: Step {step}")
        else:
            self.session.add(mapping)
            print(f"    ✅ 연결: Step {step}")

        self.created_mappings.append(mapping)

    async def verify_seeded_data(self):
        """시드된 데이터 검증"""
        if self.dry_run:
            print("\n[DRY RUN] 데이터 검증 생략")
            return

        print("\n" + "=" * 50)
        print("🔍 데이터 검증")
        print("=" * 50)

        # 챌린지 확인
        result = await self.session.execute(select(Challenge))

        # 미션 수 확인
        result = await self.session.execute(select(Mission))
        missions = result.scalars().all()
        print(f"\n📌 저장된 미션: 총 {len(missions)}개")

        # 연결 확인
        result = await self.session.execute(select(ChallengeMission))
        mappings = result.scalars().all()
        print(f"📌 챌린지-미션 연결: 총 {len(mappings)}개")


async def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="챌린지 시드 데이터 추가")
    parser.add_argument("--clear", action="store_true", help="기존 데이터 삭제 후 추가")
    parser.add_argument("--dry-run", action="store_true", help="실행 시뮬레이션 (DB 변경 없음)")
    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN 모드: 실제 DB 변경 없이 시뮬레이션합니다.")

    # DB 세션 생성
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        runner = ChallengeSeedRunner(session, dry_run=args.dry_run)

        try:
            # 기존 데이터 삭제 (옵션)
            if args.clear:
                await runner.clear_existing_data()

            # 시드 데이터 추가
            await runner.seed_challenges()

            # 데이터 검증
            await runner.verify_seeded_data()

            print("\n✨ 시드 작업 완료!")

        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            if not args.dry_run:
                await session.rollback()
                print("롤백 완료")
            raise


if __name__ == "__main__":
    # 환경변수 설정 확인
    if not os.getenv("ENVIRONMENT"):
        print("⚠️  ENVIRONMENT 환경변수를 설정해주세요 (dev/prod)")
        sys.exit(1)

    asyncio.run(main())
