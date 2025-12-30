# ==============================
# Flask 기본 설정
# ==============================
from flask import Flask
from flask_cors import CORS

# ==============================
# backend Blueprint 불러오기
# ==============================
# backend/app.py 안의 api(Blueprint)
from backend.app import api as backend_api


# ==============================
# 메인 Flask 앱 생성
# ==============================
# ✔ 템플릿 / static 경로를 frontend 기준으로 설정
app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)
# ✨ [추가된 부분] 세션 암호화를 위한 비밀키 설정
# 이 설정이 있어야 로그인 상태(session)를 유지할 수 있습니다.
app.secret_key = "super_secret_key_1234"
# ==============================
# CORS 허용
# ==============================
CORS(app)


# ==============================
# 🔗 Blueprint 등록
# ==============================
# ✔ API (/api/comments)
# ✔ 페이지 (/ , /admin , /admin/blacklist)
# 👉 전부 backend/app.py에서 처리
app.register_blueprint(backend_api)


# ==============================
# 서버 실행
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
