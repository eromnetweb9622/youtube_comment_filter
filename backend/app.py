# ==============================
# Flask 기본 모듈
# ==============================
from flask import Blueprint, request, jsonify, render_template

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
# 🎯 페이지 라우팅 (⭐ 이게 없어서 빈 화면이었음)
# ==============================

@api.route("/")
def public_monitor():
    """
    실시간 댓글 모니터링 메인 화면
    → public_monitor.html
    """
    return render_template("public_monitor.html")


@api.route("/admin")
def admin_dashboard():
    """
    관리자 대시보드 화면
    """
    return render_template("admin_dashboard.html")


@api.route("/admin/blacklist")
def admin_blacklist():
    """
    블랙리스트 관리 화면
    """
    return render_template("admin_blacklist.html")


# ==============================
# 유튜브 URL → video_id 추출
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
    """

    youtube_url = request.args.get("url")

    if not youtube_url:
        return jsonify({"error": "url is required"}), 400

    video_id = extract_video_id(youtube_url)

    if not video_id:
        return jsonify({"error": "invalid youtube url"}), 400

    try:
        comments = get_comments(video_id)
        return jsonify(comments)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
