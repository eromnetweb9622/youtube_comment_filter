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
from openai_service import analyze_comment

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

def get_comments(video_id, max_results=50):
    """
    유튜브 댓글을 가져와서
    각 댓글을 OpenAI(GPT)로 분석한 뒤 반환
    """

    results = []

    # 댓글 요청
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText"
    )

    response = request.execute()

    # 댓글 하나씩 처리
    for item in response["items"]:
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        text = snippet["textDisplay"]

        # 🔥 OpenAI(GPT)로 댓글 분석
        analysis = analyze_comment(text)

        # ❗ GPT 오류 대비 기본값 처리
        results.append({
            "author": snippet["authorDisplayName"],
            "text": text,
            "likeCount": snippet["likeCount"],
            "publishedAt": snippet["publishedAt"],
            "category": analysis.get("category", "정상"),
            "reason": analysis.get("reason", "분석 실패 또는 기본 처리")
        })

    return results
