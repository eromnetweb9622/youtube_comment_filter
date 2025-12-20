// ==============================
// 📊 Chart.js 인스턴스 저장용
// ==============================
let chartInstance = null;

// ==============================
// 📌 대시보드 로드 함수
// ==============================
function loadDashboard() {
  // 🔹 fetchComments()에서 저장한 댓글 데이터 불러오기
  const saved = localStorage.getItem("dashboardComments");

  // 🔥 분석된 데이터가 없을 경우 방어
  if (!saved) {
    alert("분석된 댓글이 없습니다. 먼저 URL을 분석하세요.");
    return;
  }

  // 🔹 문자열 → 객체 변환
  const comments = JSON.parse(saved);

  // ==============================
  // 📊 카테고리 통계 초기화
  // ==============================
  let stats = {
    정상: 0,
    욕설: 0,
    혐오: 0,
    광고: 0,
    위험: 0,
    주의: 0
  };

  // ==============================
  // 📌 카테고리별 카운트
  // ==============================
  comments.forEach(c => {
    const category = c.category || "정상"; // ⚠️ category 없을 때 대비

    if (stats[category] !== undefined) {
      stats[category]++;
    }
  });

  // ==============================
  // 📊 상단 카드 숫자 업데이트
  // ==============================
  document.getElementById("total-count").innerText = comments.length;
  document.getElementById("normal-count").innerText = stats["정상"];

  // ⚠️ 위험도 높은 댓글은 합산
  document.getElementById("abuse-count").innerText =
    stats["욕설"] + stats["혐오"] + stats["위험"];

  document.getElementById("spam-count").innerText = stats["광고"];

  // ==============================
  // 📈 차트 렌더링
  // ==============================
  renderChart(stats);
}

// ==============================
// 📈 차트 렌더링 함수
// ==============================
function renderChart(stats) {
  const ctx = document.getElementById("categoryChart");

  // 🔄 기존 차트 제거 (중복 방지)
  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: Object.keys(stats),
      datasets: [{
        data: Object.values(stats),

        // 🎨 카테고리별 색상 (댓글 카드와 통일)
        backgroundColor: [
          "#16a34a", // 정상 (green)
          "#ec4899", // 욕설 (pink)
          "#7c3aed", // 혐오 (purple)
          "#2563eb", // 광고 (blue)
          "#dc2626", // 위험 (red)
          "#facc15"  // 주의 (yellow)
        ],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#e5e7eb", // 글자색 (다크모드)
            padding: 16
          }
        }
      }
    }
  });
}

// ==============================
// 🖱️ 버튼 이벤트 연결
// ==============================
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("dashboard-btn");

  if (btn) {
    btn.addEventListener("click", loadDashboard);
  }
});
