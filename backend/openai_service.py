# ==============================
# OpenAI GPT 댓글 필터링 서비스 (최적화 버전)
# ==============================
import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ==============================
# 1️⃣ 로컬 욕설 필터 (GPT 안 탐)
# ==============================
BAD_WORDS = ["씨발", "존나", "병신", "미친", "좆"]

def local_badword_filter(text: str):
    for w in BAD_WORDS:
        if w in text:
            return {
                "category": "욕설",
                "reason": "욕설 키워드 포함"
            }
    return None


# ==============================
# 2️⃣ 빠른 정상 댓글 필터
# ==============================
def local_fast_filter(text: str):
    if len(text.strip()) <= 4:
        return {
            "category": "정상",
            "reason": "짧은 댓글"
        }

    SAFE_WORDS = ["ㅋㅋ", "ㅎㅎ", "재밌", "좋다", "귀엽", "👍", "❤️"]
    if any(w in text for w in SAFE_WORDS):
        return {
            "category": "정상",
            "reason": "일반 반응 댓글"
        }

    return None


# ==============================
# 3️⃣ GPT 배치 분석 (속도 핵심)
# ==============================
def analyze_comments_batch(texts: list[str]):
    """
    여러 댓글을 한 번의 GPT 호출로 분석
    """

    joined_comments = "\n".join(
        [f"{i+1}. {t}" for i, t in enumerate(texts)]
    )

    payload = {
        "model": "gpt-4o-mini",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": "너는 SNS 댓글 필터링 API다. 반드시 JSON 배열만 반환해라."
            },
            {
                "role": "user",
                "content": f"""
아래 댓글들을 분석해.

댓글:
{joined_comments}

반환 형식(JSON 배열):
[
  {{ "index": 1, "category": "정상|욕설|혐오|광고", "reason": "한 줄" }}
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

    return json.loads(
        response.json()["choices"][0]["message"]["content"]
    )

# ==============================
# 4️⃣ 단일 댓글 분석 (기존 코드와 호환용)
# ==============================
def analyze_comment(text: str):
    """
    기존 코드와 호환되도록 만든 단일 댓글 분석 함수
    내부적으로 로컬 필터 → GPT 배치 분석 사용
    """

    # 1️⃣ 욕설 즉시 차단
    result = local_badword_filter(text)
    if result:
        return result

    # 2️⃣ 빠른 정상 처리
    result = local_fast_filter(text)
    if result:
        return result

    # 3️⃣ GPT 호출 (1개라도 batch 사용)
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
