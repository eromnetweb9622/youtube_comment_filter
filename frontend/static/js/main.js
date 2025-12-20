async function fetchComments() {
  const url = document.getElementById("youtube-url").value;
  if (!url) {
    alert("유튜브 URL을 입력하세요");
    return;
  }

  const res = await fetch(`/api/comments?url=${encodeURIComponent(url)}`);
  const data = await res.json();

  // ==============================
  // 🔥 API 에러 방어
  // ==============================
  if (!data.comments || !Array.isArray(data.comments)) {
    alert(data.error || "댓글을 불러오지 못했습니다");
    console.error(data);
    return;
  }

  // ==============================
  // ✅ 정상 데이터 분리
  // ==============================
  const comments = data.comments;
  const summary = data.summary;

  const list = document.getElementById("comment-list");
  if (!list) return;
  list.innerHTML = "";

  // ==============================
// ✅ 카테고리별 색상 매핑
// ==============================
const categoryColorMap = {
  "정상": "bg-green-600 text-white",
  "주의": "bg-yellow-500 text-black",
  "위험": "bg-red-600 text-white",
  "욕설": "bg-pink-600 text-white",
  "혐오": "bg-purple-700 text-white",
  "광고": "bg-blue-600 text-white"
};

  // ==============================
  // 댓글 렌더링
  // ==============================
  comments.forEach(c => {
    const category = c.category || "정상";

    const card = document.createElement("div");
    card.className = "comment-card";

    card.innerHTML = `
    <div class="font-bold mb-2">${c.author || "Unknown"}</div>
    <p class="text-slate-300 mb-3">"${c.text || ""}"</p>
    <span class="text-xs px-3 py-1 rounded-full ${
      categoryColorMap[category] || "bg-slate-600 text-white"
    }">
      ${category}
    </span>
  `;

    list.appendChild(card);
  });

  // ==============================
  // AI 요약 영역 업데이트
  // ==============================
  const summaryBox = document.getElementById("ai-summary");
  if (summaryBox) {
    summaryBox.classList.remove("hidden");

    document.getElementById("summary-text").innerText =
      `총 ${summary.total}개 댓글 중 ${summary.danger}개가 위험 댓글로 분류되었습니다.`;
  }
}
