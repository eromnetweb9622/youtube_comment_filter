let chartInstance = null;

async function loadDashboard() {
  const url = document.getElementById("youtube-url").value;
  if (!url) {
    alert("유튜브 URL을 입력하세요");
    return;
  }

  const res = await fetch(`/api/comments?url=${encodeURIComponent(url)}`);
  const comments = await res.json();

  let stats = {
    정상: 0,
    욕설: 0,
    혐오: 0,
    광고: 0
  };

  comments.forEach(c => {
    if (stats[c.category] !== undefined) {
      stats[c.category]++;
    }
  });

  // 카드 숫자 업데이트
  document.getElementById("total-count").innerText = comments.length;
  document.getElementById("normal-count").innerText = stats["정상"];
  document.getElementById("abuse-count").innerText = stats["욕설"] + stats["혐오"];
  document.getElementById("spam-count").innerText = stats["광고"];

  renderChart(stats);
}

function renderChart(stats) {
  const ctx = document.getElementById("categoryChart");

  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: Object.keys(stats),
      datasets: [{
        data: Object.values(stats)
      }]
    },
    options: {
      plugins: {
        legend: {
          labels: { color: "#e5e7eb" }
        }
      }
    }
  });
}

// 버튼 이벤트 연결 (⭐ 중요)
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("dashboard-btn");
  if (btn) {
    btn.addEventListener("click", loadDashboard);
  }
});
