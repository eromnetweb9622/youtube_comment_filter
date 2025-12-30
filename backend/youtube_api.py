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
    results = []
    page_token = None

    # 🔥 카운터 3개로 분리
    normal_count = 0
    abuse_count = 0      # 욕설
    spam_count = 0       # 광고/스팸

    while len(results) < max_results:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=50,
            textFormat="plainText",
            pageToken=page_token
        )
        response = request.execute()

        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            text = snippet["textDisplay"]

            analysis = analyze_comment(text)

            # ==============================
            # 🔥 category 정규화 (3가지로 강제 매핑)
            # ==============================
            raw_category = analysis.get("category", "정상").strip()

            # 허용되는 값만 통과, 나머지는 무조건 정상
            if raw_category in ["욕설", "광고/스팸", "스팸", "광고"]:
                if "욕설" in raw_category:
                    category = "욕설"
                else:
                    category = "광고/스팸"
            else:
                category = "정상"

            # 카운터 증가
            if category == "정상":
                normal_count += 1
            elif category == "욕설":
                abuse_count += 1
            elif category == "광고/스팸":
                spam_count += 1

            results.append({
                "author": snippet["authorDisplayName"],
                "text": text,
                "likeCount": snippet["likeCount"],
                "publishedAt": snippet["publishedAt"],
                "category": category,
                "reason": analysis.get("reason", "분석 정보 없음")
            })

            if len(results) >= max_results:
                break

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    # ==============================
    # 🔥 대시보드가 원하는 형태로 summary 반환
    # ==============================
    return {
        "summary": {
            "total": len(results),
            "normal": normal_count,
            "abuse": abuse_count,      # 욕설
            "spam": spam_count         # 광고/스팸
        },
        "comments": results
    }