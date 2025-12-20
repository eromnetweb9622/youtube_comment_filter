# ==============================
# 환경변수 로드
# ==============================
import os
from dotenv import load_dotenv
load_dotenv()

# ==============================
# YouTube API 라이브러리
# ==============================
from googleapiclient.discovery import build

# ==============================
# OpenAI 댓글 분석 함수
# ==============================
# ❗ 1순위 개선 포인트:
# - analyze_comment 내부 GPT 프롬프트를
#   "확실할 때만 위험" 기준으로 완화해야 함
from backend.openai_service import analyze_comment

# ==============================
# YouTube API Key
# ==============================
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# ❗ API 키 없을 때 바로 에러 확인용
if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY가 .env에 없습니다.")

# ==============================
# YouTube Data API 객체 생성
# ==============================
youtube = build(
    "youtube",
    "v3",
    developerKey=YOUTUBE_API_KEY
)

def get_comments(video_id, max_results=100):
    """
    유튜브 댓글을 가져와서
    각 댓글을 OpenAI(GPT)로 분석한 뒤 반환

    ✔ max_results: 최대로 가져올 댓글 수 (50, 100, 200 등)

    ⚠️ 주의:
    - YouTube API는 한 번에 최대 50개만 반환
    - nextPageToken으로 반복 호출 필요
    """

    results = []
    page_token = None   # 🔥 페이지네이션용 토큰

    danger_count = 0    # 🔥 위험 댓글 개수 (요약용)

    # ==============================
    # 🔁 nextPageToken이 있는 동안 반복 호출
    # ==============================
    while len(results) < max_results:

        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=50,            # ❗ YouTube API 최대값은 항상 50
            textFormat="plainText",
            pageToken=page_token      # 🔥 다음 페이지 요청
        )

        response = request.execute()

        # ==============================
        # 댓글 하나씩 처리
        # ==============================
        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            text = snippet["textDisplay"]

            # =====================================================
            # 🔥 OpenAI(GPT)로 댓글 분석
            #
            # 1순위 핵심:
            # - 이 결과가 과도하게 "위험"으로 나오는 문제는
            #   ❌ 여기 문제가 아니라
            #   ✅ analyze_comment 내부 GPT 프롬프트 문제임
            # =====================================================
            analysis = analyze_comment(text)

            # ==============================
            # 🔥 category 정규화 (매우 중요)
            # ==============================
            raw_category = analysis.get("category", "정상")

            # GPT가 이상한 값 주면 무조건 정상 처리
            if raw_category not in ["정상", "위험"]:
                raw_category = "정상"

            if raw_category == "위험":
                danger_count += 1

            results.append({
                "author": snippet["authorDisplayName"],
                "text": text,
                "likeCount": snippet["likeCount"],
                "publishedAt": snippet["publishedAt"],

                # ❗ 프론트 집계용 category (정상 / 위험만 사용)
                "category": raw_category,

                # ❗ reason은 관리자 확인용
                "reason": analysis.get("reason", "분석 실패 또는 기본 처리")
            })

            # ❗ max_results 초과 방지
            if len(results) >= max_results:
                break

        # ==============================
        # 다음 페이지 토큰 처리
        # ==============================
        page_token = response.get("nextPageToken")

        # ❗ 다음 페이지 없으면 종료
        if not page_token:
            break

    # ==============================
    # 🔥 요약 정보 포함해서 반환
    # ==============================
    return {
        "summary": {
            "total": len(results),
            "danger": danger_count
        },
        "comments": results
    }
