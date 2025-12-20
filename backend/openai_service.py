# ==============================
# OpenAI GPT 댓글 필터링 서비스 (균형잡힌 필터링)
# ==============================

import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

# ==============================
# ✅ 카테고리 정의
# ==============================
ALLOWED_CATEGORIES = ["정상", "욕설", "혐오", "광고", "위험"]

# ==============================
# 1️⃣ 욕설 필터 (강화)
# ==============================
BAD_WORD_PATTERNS = [
    r"씨\s*발", r"ㅅ\s*ㅂ", r"병\s*신", r"ㅂ\s*ㅅ",
    r"좆", r"미\s*친", r"지\s*랄", r"개\s*새끼", r"염병",
    r"꺼\s*져", r"죽\s*어"
]

def local_badword_filter(text: str):
    """명확한 욕설 패턴 감지"""
    for pattern in BAD_WORD_PATTERNS:
        if re.search(pattern, text):
            return {"category": "욕설", "reason": "욕설 패턴 감지"}
    return None


# ==============================
# 2️⃣ 광고 필터
# ==============================
def local_ad_filter(text: str):
    """명확한 광고 패턴"""
    AD_PATTERNS = [
        r"http[s]?://[^\s]+",  # URL
        r"www\.[^\s]+",
        r"\d{2,4}-\d{3,4}-\d{4}",  # 전화번호
        r"010-?\d{4}-?\d{4}",
        r"카톡\s*문의", r"텔레그램", r"인스타\s*@"
    ]
    
    for pattern in AD_PATTERNS:
        if re.search(pattern, text):
            return {"category": "광고", "reason": "광고/홍보 의심"}
    return None


# ==============================
# 3️⃣ 빠른 정상 필터 (🔥 신중하게 개선)
# ==============================
def local_fast_filter(text: str):
    """
    명백히 안전한 댓글만 통과
    ⚠️ 애매하면 GPT로 넘김
    """
    stripped = text.strip()
    
    # 🔥 아주 짧은 이모티콘만 있는 경우만 정상 처리
    if len(stripped) <= 3 and not any(char.isalnum() for char in stripped):
        return {"category": "정상", "reason": "이모티콘 반응"}
    
    # 🔥 긍정 키워드 (하지만 부정 키워드가 없을 때만)
    POSITIVE_WORDS = [
        "ㅋㅋㅋ", "ㅎㅎㅎ", "ㅠㅠ",  # 최소 3글자 이상
        "좋아", "귀여워", "이쁘", "예쁘", "멋있", 
        "최고", "감사", "응원", "사랑", "축하",
        "👍", "❤️", "💕", "😊", "🥰"
    ]
    
    # 🔥 부정/위험 키워드 (이게 있으면 GPT로)
    NEGATIVE_WORDS = [
        "죽", "꺼져", "싫어", "최악", "쓰레기",
        "혐오", "무식", "한심", "정신", "문제"
    ]
    
    has_negative = any(word in stripped for word in NEGATIVE_WORDS)
    
    # 부정 키워드가 있으면 무조건 GPT로
    if has_negative:
        return None
    
    # 긍정 키워드가 있고 + 부정이 없을 때만 정상
    has_positive = any(word in stripped for word in POSITIVE_WORDS)
    
    if has_positive and len(stripped) >= 5:  # 최소 5글자 이상
        return {"category": "정상", "reason": "긍정적 반응"}
    
    return None


# ==============================
# ✅ GPT JSON 파싱
# ==============================
def safe_json_parse(content: str):
    match = re.search(r"\[.*\]", content, re.S)
    if not match:
        raise ValueError("JSON 배열 없음")
    return json.loads(match.group())


def chunk_list(data, size=10):
    return [data[i:i + size] for i in range(0, len(data), size)]


# ==============================
# 4️⃣ GPT 배치 분석 (🔥 프롬프트 개선)
# ==============================
def analyze_comments_batch(texts: list[str]):
    """
    GPT 분석 - 명확한 기준 제시
    """
    joined = "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts)])

    payload = {
        "model": "gpt-4o-mini",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": """너는 유튜브 댓글 필터링 AI다.

**분류 기준 (정확하게 따라라)**

✅ **정상** - 이런 댓글들:
- 일반적인 의견, 질문
- "ㅋㅋ", "ㅎㅎ", "ㅠㅠ" 같은 감정 표현
- 이모티콘 사용 (❤️, 😊, 👍)
- "귀여워", "좋아요", "멋있어" 같은 긍정 반응
- "0:16 여기 좋다" 같은 타임스탬프 댓글
- 단순 농담, 밈

⚠️ **욕설** - 명확한 욕설, 비속어

⚠️ **혐오** - 특정 인종/성별/집단에 대한 차별적 발언

⚠️ **광고** - 상품 홍보, 링크, 연락처

🚨 **위험** - 다음 중 하나에 해당:
- 특정 개인에 대한 심각한 인신공격
- 폭력 선동, 위협
- 개인정보 유출 시도
- 자해/자살 조장

**중요**: 
- 단순히 부정적 의견은 "정상"이다
- "별로다", "재미없다" → 정상
- 이모티콘만 있으면 → 정상
- 애매하면 "정상"으로 분류해라

반드시 JSON 배열만 반환해라."""
            },
            {
                "role": "user",
                "content": f"""아래 댓글을 분석해.

{joined}

반환 형식:
[
  {{"index": 1, "category": "정상|욕설|혐오|광고|위험", "reason": "한 줄 설명"}}
]"""
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

    if response.status_code != 200:
        raise Exception("OpenAI API 실패")

    content = response.json()["choices"][0]["message"]["content"]
    return safe_json_parse(content)


# ==============================
# 5️⃣ 단일 댓글 분석
# ==============================
def analyze_comment(text: str):
    """
    처리 순서:
    1. 욕설 필터
    2. 광고 필터
    3. 정상 필터 (신중하게)
    4. GPT 분석
    """
    # 1. 욕설 체크
    result = local_badword_filter(text)
    if result:
        return result
    
    # 2. 광고 체크
    result = local_ad_filter(text)
    if result:
        return result
    
    # 3. 정상 체크 (매우 신중)
    result = local_fast_filter(text)
    if result:
        return result

    # 4. GPT 분석
    try:
        gpt_result = analyze_comments_batch([text])[0]
        category = gpt_result.get("category", "위험")
        
        if category not in ALLOWED_CATEGORIES:
            category = "위험"
        
        return {
            "category": category,
            "reason": gpt_result.get("reason", "AI 판단")
        }
    except Exception:
        return {
            "category": "위험",
            "reason": "AI 분석 실패 (보수적 처리)"
        }


# ==============================
# 6️⃣ 대량 댓글 분석
# ==============================
def analyze_comments_bulk(comments: list[dict]):
    """
    로컬 필터 → GPT 배치 처리
    """
    results = []
    gpt_targets = []

    # 로컬 필터링
    for c in comments:
        text = c["text"]
        
        # 욕설 체크
        local = local_badword_filter(text)
        if local:
            results.append({**c, **local})
            continue
        
        # 광고 체크
        local = local_ad_filter(text)
        if local:
            results.append({**c, **local})
            continue
        
        # 정상 체크 (신중하게)
        local = local_fast_filter(text)
        if local:
            results.append({**c, **local})
            continue
        
        # GPT 대상
        gpt_targets.append(c)

    # GPT 배치 분석
    batches = chunk_list(gpt_targets, size=10)
    
    for batch in batches:
        texts = [c["text"] for c in batch]
        
        try:
            gpt_results = analyze_comments_batch(texts)
            
            if len(gpt_results) != len(batch):
                raise ValueError("GPT 응답 개수 불일치")
            
            for c, g in zip(batch, gpt_results):
                category = g.get("category", "위험")
                
                if category not in ALLOWED_CATEGORIES:
                    category = "위험"
                
                results.append({
                    **c,
                    "category": category,
                    "reason": g.get("reason", "AI 판단")
                })
        
        except Exception:
            # 배치 실패 시 위험 처리
            for c in batch:
                results.append({
                    **c,
                    "category": "위험",
                    "reason": "AI 분석 실패"
                })

    return results