async function fetchComments() {
  const url = document.getElementById("youtube-url").value;
  if (!url) {
    alert("유튜브 URL을 입력하세요");
    return;
  }

  const res = await fetch(`/api/comments?url=${encodeURIComponent(url)}`);
  const data = await res.json();

  // 🔥 API 에러 방어
  if (!Array.isArray(data)) {
    alert(data.error || "댓글을 불러오지 못했습니다");
    console.error(data);
    return;
  }

  const list = document.getElementById("comment-list");
  if (!list) return;
  list.innerHTML = "";

  let danger = 0;

  data.forEach(c => {
    if (c.category !== "정상") danger++;

    const card = document.createElement("div");
    card.className = "comment-card";

    card.innerHTML = `
      <div class="font-bold mb-2">${c.author}</div>
      <p class="text-slate-300 mb-3">"${c.text}"</p>
      <span class="text-xs px-3 py-1 rounded-full bg-slate-800">
        ${c.category}
      </span>
    `;

    list.appendChild(card);
  });

  const summaryBox = document.getElementById("ai-summary");
  if (summaryBox) {
    summaryBox.classList.remove("hidden");
    document.getElementById("summary-text").innerText =
      `총 ${data.length}개 댓글 중 ${danger}개가 위험 댓글로 분류되었습니다.`;
  }
}
