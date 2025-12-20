# ==============================
# Gemini REST API 우회 호출
# ==============================
import os
import requests
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def analyze_comment(text):
    """
    Gemini REST API를 직접 호출하여
    댓글을 분류 (우회 방식)
    """

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1/models/gemini-pro:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    prompt = f"""
    다음 댓글을 분석해서
    욕설, 혐오, 광고, 정상 중 하나로 분류하고
    이유를 간단히 설명해줘.

    댓글: {text}

    JSON 형식으로만 응답해.
    {{
      "category": "",
      "reason": ""
    }}
    """

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )

    data = response.json()

    # Gemini 응답 파싱
    try:
        result_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(result_text)
    except Exception:
        return {
            "category": "error",
            "reason": "Gemini 응답 파싱 실패"
        }


# ==============================
# 단독 실행 테스트
# ==============================
if __name__ == "__main__":
    test_comment = "이 영상 존나 별로네 ㅋㅋ"
    result = analyze_comment(test_comment)
    print(result)
