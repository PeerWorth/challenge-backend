from app.module.challenge.enums import MissionType

CHALLENGES_DATA = [
    {
        "id": 1,
        "title": "첫 걸음 챌린지",
        "description": "서비스 첫 시작을 위한 기본 챌린지입니다",
        "goal": 3,
        "missions": [
            {
                "title": "프로필 설정하기",
                "description": "나의 프로필 정보를 입력하고 사진을 등록해보세요",
                "type": MissionType.SERVICE,
                "point": 100,
                "step": 1,
            },
            {
                "title": "첫 게시물 작성하기",
                "description": "나의 첫 번째 게시물을 작성해보세요",
                "type": MissionType.PHOTO,
                "point": 200,
                "step": 2,
            },
        ],
    },
    {
        "id": 2,
        "title": "일주일 도전 챌린지",
        "description": "7일 동안 매일 활동하는 챌린지입니다",
        "goal": 7,
        "missions": [
            {
                "title": "Day 1: 오늘의 목표 설정",
                "description": "오늘 하루 달성하고 싶은 목표를 작성하세요",
                "type": MissionType.EVENT,
                "point": 100,
                "step": 1,
            },
            {
                "title": "Day 2: 감사 일기 쓰기",
                "description": "오늘 감사했던 세 가지를 기록해보세요",
                "type": MissionType.PHOTO,
                "point": 100,
                "step": 2,
            },
        ],
    },
    {
        "id": 3,
        "title": "전문가 되기 챌린지",
        "description": "특정 분야의 전문성을 쌓아가는 챌린지입니다",
        "goal": 5,
        "missions": [
            {
                "title": "관심 분야 선정",
                "description": "전문가가 되고 싶은 분야를 선정하고 공유하세요",
                "type": MissionType.PHOTO,
                "point": 100,
                "step": 1,
            }
        ],
    },
]
