# ==============================
# Flask 및 DB 모듈 추가
# ==============================
from flask import Blueprint, request, jsonify, render_template, session, url_for, redirect, current_app
from flask_cors import CORS
import re
import pymysql  # 👈 DB 연결을 위해 추가
from backend.youtube_api import get_comments

api = Blueprint("api", __name__)
CORS(api)

# ==============================
# 🔐 보안: 모든 페이지 접근 제어
# ==============================
@api.before_app_request
def login_required():
    # 로그인 없이 접근 가능한 페이지 정의 (로그인 페이지, static 파일 등)
    allowed_routes = ["api.admin_login", "static"]
    
    if request.endpoint not in allowed_routes and not session.get("is_admin"):
        return redirect(url_for("api.admin_login"))

# ==============================
# 🗄️ 데이터베이스 연결 설정
# ==============================
def get_db_connection():
    return pymysql.connect(
        host='192.168.0.20',
        user='root',       # 이미지에 사용자가 없으나 보통 root를 사용합니다. 설정에 맞게 변경하세요.
        password='1234',   # 실제 DB 비밀번호를 입력하세요.
        db='youtube',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


# ==============================
# 🎯 페이지 라우팅
# ==============================

@api.route("/")
def public_monitor():
    # 관리자 여부와 관계없이 base.html을 확장한 public_monitor.html을 보여줍니다.
    # 템플릿 내부의 {% if session.get('is_admin') %} 로직이 사이드바를 제어합니다.
    if session.get("is_admin") and session.get("last_comments"):
        return render_template(
            "public_monitor.html",
            url=session.get("last_url"),
            comments=session.get("last_comments"),
            summary=session.get("last_summary")
        )
    return render_template("public_monitor.html")

# 로그아웃 후 세션이 비워지면 사이드바가 자동으로 '로그인' 버튼으로 바뀝니다.


@api.route("/admin/dashboard")
def admin_dashboard():
    """
    관리자 대시보드 화면
    세션에서 'last_url'과 'last_summary'를 가져와 템플릿에 전달합니다.
    """
    return render_template(
        "admin_dashboard.html",
        url=session.get("last_url"),
        summary=session.get("last_summary")
    )


@api.route("/admin/blacklist")
def admin_blacklist():
    """
    블랙리스트 관리 화면
    """
    return render_template("admin_blacklist.html")

# ==============================
# 🎯 로그인 로직 (성공 시 실시간 관제로)
# ==============================
@api.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        # 로그인 된 상태라면 바로 메인으로
        if session.get("is_admin"):
            return redirect(url_for("api.public_monitor"))
        return render_template("admin_login.html")

    input_id = request.form.get("admin_id")
    input_pw = request.form.get("secret_code")

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM admins WHERE username=%s"
            cursor.execute(sql, (input_id,))
            admin = cursor.fetchone()

            if admin and admin['password_hash'] == input_pw:
                session.clear() # 이전 세션 초기화
                session["is_admin"] = True
                # 🚀 로그인 성공 시 '실시간 관제' 페이지로 이동
                return redirect(url_for("api.public_monitor"))
            else:
                return render_template("admin_login.html", error="정보가 일치하지 않습니다.")
    except Exception as e:
        return render_template("admin_login.html", error=f"DB 연결 오류: {str(e)}")
    finally:
        if 'connection' in locals(): connection.close()
# 로그아웃 후 세션이 비워지면 사이드바가 자동으로 '로그인' 버튼으로 바뀝니다.
@api.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("api.public_monitor"))
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
# ==============================
# ✅ 유튜브 댓글 API 수정
# ==============================
@api.route("/api/comments", methods=["GET"])
def comments():
    # 🔒 [추가] 관리자 로그인 여부 확인
    if not session.get("is_admin"):
        return jsonify({"error": "unauthorized", "message": "관리자 로그인을 먼저 진행해 주세요."}), 401

    youtube_url = request.args.get("url")
    if not youtube_url:
        return jsonify({"error": "url is required"}), 400

    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "invalid youtube url"}), 400

    try:
        comments_data = get_comments(video_id)

        # 관리자 세션에 마지막 분석 데이터 요약본 저장
        session["last_url"] = youtube_url
        session["last_summary"] = comments_data.get("summary")

        return jsonify(comments_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
