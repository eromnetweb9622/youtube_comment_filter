# ==============================
# OpenAI GPT 댓글 필터링 서비스 (실서비스 안정화 버전)
# ==============================

import os
import json
import re
import requests
from dotenv import load_dotenv

# ==============================
# 환경 변수 로드 (.env)
# ==============================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ==============================
# 1️⃣ 로컬 욕설 필터 (GPT 호출 안 함)
# - 가장 먼저 실행
# - 명확한 욕설은 즉시 차단
# ==============================

# 정규식 기반 욕설 패턴 (띄어쓰기/변형 대응)
BAD_WORD_PATTERNS = [
    r"씨\s*발",
    r"ㅅ\s*ㅂ",
    r"병\s*신",
    r"ㅂ\s*ㅅ",
    r"좆",
    r"미\s*친",
]

def local_badword_filter(text: str):
    """
    욕설 패턴이 감지되면 즉시 욕설로 분류
    """
    for pattern in BAD_WORD_PATTERNS:
        if re.search(pattern, text):
            return {
                "category": "욕설",
                "reason": "욕설 패턴 감지"
            }
    return None


# ==============================
# 2️⃣ 빠른 정상 댓글 필터
# - GPT 비용 절감용
# - 욕설 가능성 있는 짧은 댓글은 제외
# ==============================

def local_fast_filter(text: str):
    """
    명백히 정상으로 판단 가능한 댓글만 빠르게 통과
    """
    stripped = text.strip()

    # 짧은 댓글이라도 욕설 가능성 있으므로
    # 무조건 정상 처리하지 않음
    if len(stripped) <= 4:
        return None

    SAFE_WORDS = ["ㅋㅋ", "ㅎㅎ", "재밌", "좋다", "귀엽", "👍", "❤️"]

    if any(word in stripped for word in SAFE_WORDS):
        return {
            "category": "정상",
            "reason": "일반 반응 댓글"
        }

    return None


# ==============================
# 3️⃣ GPT 배치 댓글 분석 (핵심 로직)
# - 여러 댓글을 한 번에 분석
# - 속도 + 비용 최적화
# ==============================

def analyze_comments_batch(texts: list[str]):
    """
    여러 댓글을 한 번의 GPT 호출로 분석
    반드시 JSON 배열 형태로만 반환받음
    """

    # 댓글을 번호 붙여 하나의 문자열로 결합
    joined_comments = "\n".join(
        [f"{i+1}. {text}" for i, text in enumerate(texts)]
    )

    payload = {
        "model": "gpt-4o-mini",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "너는 SNS 댓글 필터링 API다. "
                    "반드시 JSON 배열만 반환해야 한다."
                )
            },
            {
                "role": "user",
                "content": f"""
아래 댓글들을 분석해.

댓글:
{joined_comments}

반환 형식(JSON 배열):
[
  {{ "index": 1, "category": "정상|욕설|혐오|광고", "reason": "한 줄 설명" }}
]
"""
            }
        ]
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=15
    )

    # HTTP 오류 체크
    if response.status_code != 200:
        raise Exception("OpenAI API 요청 실패")

    content = response.json()["choices"][0]["message"]["content"]

    # GPT가 JSON 형식 깨뜨리는 경우 대비
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return [{
            "index": 1,
            "category": "error",
            "reason": "GPT JSON 파싱 실패"
        }]


# ==============================
# 4️⃣ 단일 댓글 분석 함수 (기존 코드 호환)
# - 내부적으로 batch 분석 사용
# ==============================

def analyze_comment(text: str):
    """
    단일 댓글 분석
    처리 순서:
    1. 로컬 욕설 필터
    2. 빠른 정상 필터
    3. GPT 분석
    """

    # 1️⃣ 욕설 즉시 차단
    result = local_badword_filter(text)
    if result:
        return result

    # 2️⃣ 명확한 정상 댓글 빠른 처리
    result = local_fast_filter(text)
    if result:
        return result

    # 3️⃣ GPT 호출 (단일 댓글도 batch 방식 사용)
    try:
        gpt_result = analyze_comments_batch([text])
        return {
            "category": gpt_result[0]["category"],
            "reason": gpt_result[0]["reason"]
        }
    except Exception:
        return {
            "category": "error",
            "reason": "OpenAI API 오류"
        }
