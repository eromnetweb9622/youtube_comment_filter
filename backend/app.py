# ==============================
# Flask 기본 모듈
# ==============================
from flask import Blueprint, request, jsonify, render_template, session

# ==============================
# CORS 설정
# ==============================
from flask_cors import CORS

# ==============================
# 정규식
# ==============================
import re

# ==============================
# YouTube API 로직
# ==============================
from backend.youtube_api import get_comments


# ==============================
# Blueprint 생성
# ==============================
# ❗ Flask(app) 생성 ❌
# ❗ run.py에서 생성한 app에 등록됨
api = Blueprint("api", __name__)
CORS(api)


# ==============================
# 🎯 페이지 라우팅
# ==============================

@api.route("/")
def public_monitor():
    """
    실시간 댓글 모니터링 메인 화면

    ✔ 일반 유저:
      - 항상 빈 화면으로 시작

    ✔ 관리자:
      - 이전에 분석한 URL/댓글이 있으면
        session에서 복원해서 화면에 전달
    """

    # 🔥 관리자 + 이전 분석 데이터가 있을 경우
    if session.get("is_admin") and session.get("last_comments"):
        return render_template(
            "public_monitor.html",
            url=session.get("last_url"),
            comments=session.get("last_comments"),
            summary=session.get("last_summary")
        )

    # 🔹 일반 유저 or 최초 접근
    return render_template("public_monitor.html")


@api.route("/admin/dashboard")
def admin_dashboard():
    """
    관리자 대시보드 화면

    ⚠️ 주의:
    - 여기서는 session을 건드리지 말 것
    - 그래야 실시간 관제로 돌아가도 상태 유지됨
    """
    return render_template("admin_dashboard.html")


@api.route("/admin/blacklist")
def admin_blacklist():
    """
    블랙리스트 관리 화면
    """
    return render_template("admin_blacklist.html")

@api.route("/admin/login")
def admin_login():
    return render_template("admin_login.html")


# ==============================
# 🔍 유튜브 URL → video_id 추출
# ==============================
def extract_video_id(youtube_url):
    """
    다양한 유튜브 URL에서 video_id 추출
    """
    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?]+)",
        r"shorts/([^?]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)

    return None


# ==============================
# ✅ 유튜브 댓글 API
# ==============================
@api.route("/api/comments", methods=["GET"])
def comments():
    """
    유튜브 댓글을 가져와 JSON으로 반환

    ✔ 관리자일 경우:
      - 분석한 URL / 댓글 / 요약 정보를
        Flask session에 저장
    """

    youtube_url = request.args.get("url")

    if not youtube_url:
        return jsonify({"error": "url is required"}), 400

    video_id = extract_video_id(youtube_url)

    if not video_id:
        return jsonify({"error": "invalid youtube url"}), 400

    try:
        # 🔹 유튜브 댓글 + AI 분석
        comments_data = get_comments(video_id)

        # 🔥 관리자일 경우만 세션에 저장
        if session.get("is_admin"):
            session["last_url"] = youtube_url
            session["last_comments"] = comments_data["comments"]
            session["last_summary"] = comments_data["summary"]

        return jsonify(comments_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
