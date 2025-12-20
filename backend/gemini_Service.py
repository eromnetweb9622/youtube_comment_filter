# ==============================
# Gemini REST API 우회 호출 (실사용)
# ==============================
import os
import requests
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def classify_comment(text: str):

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1/models/gemini-pro:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    prompt = f"""
당신은 글로벌 플랫폼의 지능형 필터링 시스템입니다.

댓글을 분석해서
[정상, 스팸, 욕설, 비방] 중 하나로 분류하세요.

댓글: "{text}"

반드시 JSON 형식으로만 응답하세요.
{{
  "category": "",
  "language": "",
  "langCode": "",
  "reason": ""
}}
"""

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=payload
    )

    data = response.json()

    try:
        result_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(result_text)
    except:
        return {
            "category": "정상",
            "language": "Unknown",
            "langCode": "und",
            "reason": "Gemini 분석 실패 (우회)"
        }
