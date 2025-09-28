"""
챌린지 시드 데이터
PM이 관리하는 챌린지와 미션 데이터
"""

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
                "type": "onboarding",
                "point": 100,
                "step": 1,
            },
            {
                "title": "첫 게시물 작성하기",
                "description": "나의 첫 번째 게시물을 작성해보세요",
                "type": "posting",
                "point": 200,
                "step": 2,
            },
            {
                "title": "친구 3명 추가하기",
                "description": "다른 사용자 3명과 친구를 맺어보세요",
                "type": "social",
                "point": 150,
                "step": 3,
            },
            {
                "title": "첫 댓글 작성하기",
                "description": "다른 사용자의 게시물에 댓글을 달아보세요",
                "type": "engagement",
                "point": 100,
                "step": 4,
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
                "type": "daily",
                "point": 100,
                "step": 1,
            },
            {
                "title": "Day 2: 감사 일기 쓰기",
                "description": "오늘 감사했던 세 가지를 기록해보세요",
                "type": "daily",
                "point": 100,
                "step": 2,
            },
            {
                "title": "Day 3: 운동 인증",
                "description": "30분 이상 운동하고 인증샷을 올려보세요",
                "type": "daily",
                "point": 150,
                "step": 3,
            },
            {
                "title": "Day 4: 독서 기록",
                "description": "오늘 읽은 책이나 글의 인상깊은 구절을 공유하세요",
                "type": "daily",
                "point": 100,
                "step": 4,
            },
            {
                "title": "Day 5: 요리 도전",
                "description": "새로운 요리에 도전하고 결과를 공유하세요",
                "type": "daily",
                "point": 200,
                "step": 5,
            },
            {
                "title": "Day 6: 봉사 활동",
                "description": "작은 선행이나 봉사활동을 하고 경험을 나눠보세요",
                "type": "daily",
                "point": 250,
                "step": 6,
            },
            {
                "title": "Day 7: 일주일 회고",
                "description": "일주일 동안의 챌린지를 돌아보고 느낀점을 작성하세요",
                "type": "daily",
                "point": 150,
                "step": 7,
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
                "type": "learning",
                "point": 100,
                "step": 1,
            },
            {
                "title": "기초 지식 습득",
                "description": "선정한 분야의 기초 개념 5가지를 정리해서 공유하세요",
                "type": "learning",
                "point": 300,
                "step": 2,
            },
            {
                "title": "실습 프로젝트",
                "description": "배운 내용을 활용한 작은 프로젝트를 진행하고 결과를 공유하세요",
                "type": "project",
                "point": 500,
                "step": 3,
            },
            {
                "title": "지식 공유",
                "description": "학습한 내용을 다른 사람들이 이해하기 쉽게 정리해서 공유하세요",
                "type": "teaching",
                "point": 400,
                "step": 4,
            },
            {
                "title": "멘토링 진행",
                "description": "초보자 1명에게 배운 내용을 멘토링하고 후기를 작성하세요",
                "type": "mentoring",
                "point": 600,
                "step": 5,
            },
            {
                "title": "커뮤니티 참여",
                "description": "관련 커뮤니티에서 활발히 활동하고 인사이트를 공유하세요",
                "type": "community",
                "point": 300,
                "step": 6,
            },
        ],
    },
]
