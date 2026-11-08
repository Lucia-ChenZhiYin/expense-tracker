const $ = id => document.getElementById(id);
const money = n => new Intl.NumberFormat("zh-TW", {
  style: "currency", currency: "TWD", maximumFractionDigits: 0
}).format(n || 0);

let categories = [];
let records = [];
let chart = null;

const now = new Date();
const currentMonth = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,"0")}`;
$("monthPicker").value = currentMonth;
$("recordDate").value = dateForInput(now);

function dateForInput(date) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
  }[char]));
}
function showToast(message) {
  $("toast").textContent = message;
  $("toast").classList.add("show");
  window.setTimeout(() => $("toast").classList.remove("show"), 2200);
}
async function api(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) }
  });
  const data = response.status === 204 ? {} : await response.json();
  if (!response.ok) throw new Error(data.error || "操作失敗，請稍後再試。");
  return data;
}
function currentType() {
  return document.querySelector('input[name="type"]:checked').value;
}
function renderCategoryOptions(selectedId = "") {
  const options = categories.filter(item => item.type === currentType());
  $("category").innerHTML = options.map(item =>
    `<option value="${item.id}" ${String(item.id) === String(selectedId) ? "selected" : ""}>${escapeHtml(item.name)}</option>`
  ).join("");
}
async function loadCategories(selectedId = "") {
  categories = await api("/api/categories");
  renderCategoryOptions(selectedId);
}
async function refresh() {
  const month = $("monthPicker").value || currentMonth;
  $("monthLabel").textContent = `${month.replace("-", " 年 ")} 月`;
  const [list, stats, comparison] = await Promise.all([
    api(`/api/records?month=${month}`),
    api(`/api/analytics/monthly?month=${month}`),
    api(`/api/analytics/monthly-comparison?month=${month}`)
  ]);

  records = list;
  $("incomeTotal").textContent = money(stats.income);
  $("expenseTotal").textContent = money(stats.expense);
  $("balanceTotal").textContent = money(stats.balance);
  $("chartBalance").textContent = money(stats.balance);
  renderRecords();
  renderChart(stats.by_category);
  renderComparison(comparison);
}
function renderRecords() {
  $("recordCount").textContent = `${records.length} 筆紀錄`;
  $("recordsEmpty").classList.toggle("hidden", records.length > 0);

  const groups = {};
  records.forEach(record => {
    if (!groups[record.date]) groups[record.date] = [];
    groups[record.date].push(record);
  });

  $("recordsList").innerHTML = Object.entries(groups).map(([day, items]) => `
    <div class="record-day">
      <div class="day-title">${day}</div>
      ${items.map(record => `
        <div class="record-row">
          <div class="record-icon">${record.type === "expense" ? "↗" : "↙"}</div>
          <div>
            <div class="record-name">${escapeHtml(record.category)}</div>
            <div class="record-note">${escapeHtml(record.sub_item || "沒有備註")}</div>
          </div>
          <div class="record-amount ${record.type}">${record.type === "expense" ? "−" : "+"}${money(record.amount)}</div>
          <div class="row-actions">
            <button type="button" onclick="editRecord(${record.id})">編輯</button>
            <button type="button" onclick="deleteRecord(${record.id})">刪除</button>
          </div>
        </div>
      `).join("")}
    </div>
  `).join("");
}
function renderChart(data) {
  $("chartEmpty").classList.toggle("hidden", data.length > 0);
  if (chart) chart.destroy();

  chart = new Chart($("expenseChart"), {
    type: "doughnut",
    data: {
      labels: data.map(item => item.name),
      datasets: [{
        data: data.map(item => item.total),
        backgroundColor: ["#6e927c","#d98c76","#d9b66f","#8c9bb0","#9b8eae","#86aaa5","#c0a18d","#a7b77c"],
        borderColor: "#fff",
        borderWidth: 3,
        hoverOffset: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "72%",
      plugins: {
        legend: {
          position: "bottom",
          labels: { usePointStyle: true, boxWidth: 7, padding: 14 }
        }
      }
    }
  });
}
function renderComparison(data) {
  const visible = data.filter(item => item.current || item.previous);
  $("comparisonEmpty").classList.toggle("hidden", visible.length > 0);
  $("comparisonList").innerHTML = visible.map(item => {
    const differenceText = item.difference > 0
      ? `增加 ${money(item.difference)}`
      : item.difference < 0
        ? `減少 ${money(Math.abs(item.difference))}`
        : "與上月相同";
    const differenceClass = item.difference > 0 ? "up" : item.difference < 0 ? "down" : "";
    return `<div class="comparison-item">
      <strong>${escapeHtml(item.category)}</strong>
      <span>本月 ${money(item.current)} · 上月 ${money(item.previous)}</span><br>
      <span class="${differenceClass}">${differenceText}</span>
    </div>`;
  }).join("");
}
function resetForm() {
  $("recordForm").reset();
  $("recordId").value = "";
  $("recordDate").value = dateForInput(new Date());
  $("formTitle").textContent = "新增一筆紀錄";
  $("saveBtn").textContent = "儲存紀錄";
  $("cancelEdit").classList.add("hidden");
  renderCategoryOptions();
}

window.editRecord = function(id) {
  const record = records.find(item => item.id === id);
  if (!record) return;

  document.querySelector(`input[name="type"][value="${record.type}"]`).checked = true;
  renderCategoryOptions(record.category_id);
  $("recordId").value = record.id;
  $("amount").value = record.amount;
  $("recordDate").value = record.date;
  $("subItem").value = record.sub_item || "";
  $("formTitle").textContent = "編輯收支紀錄";
  $("saveBtn").textContent = "更新紀錄";
  $("cancelEdit").classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
};

window.deleteRecord = async function(id) {
  if (!window.confirm("確定要刪除這筆紀錄嗎？")) return;
  try {
    await api(`/api/records/${id}`, { method: "DELETE" });
    showToast("紀錄已刪除");
    await refresh();
  } catch (error) {
    showToast(error.message);
  }
};

document.querySelectorAll('input[name="type"]').forEach(input => {
  input.addEventListener("change", () => renderCategoryOptions());
});

$("monthPicker").addEventListener("change", () => {
  refresh().catch(error => showToast(error.message));
});
$("cancelEdit").addEventListener("click", resetForm);

$("recordForm").addEventListener("submit", async event => {
  event.preventDefault();
  const id = $("recordId").value;
  const payload = {
    amount: $("amount").value,
    type: currentType(),
    category_id: $("category").value,
    date: $("recordDate").value,
    sub_item: $("subItem").value
  };

  try {
    await api(id ? `/api/records/${id}` : "/api/records", {
      method: id ? "PUT" : "POST",
      body: JSON.stringify(payload)
    });
    showToast(id ? "紀錄更新成功" : "新增成功");
    resetForm();
    await refresh();
  } catch (error) {
    showToast(error.message);
  }
});

$("addCategoryBtn").addEventListener("click", async () => {
  const name = $("newCategory").value.trim();
  if (!name) {
    showToast("請先輸入類別名稱");
    return;
  }
  try {
    await api("/api/categories", {
      method: "POST",
      body: JSON.stringify({
        name,
        type: $("newCategoryType").value
      })
    });
    $("newCategory").value = "";
    await loadCategories();
    showToast("類別新增成功");
  } catch (error) {
    showToast(error.message);
  }
});

async function startApp() {
  try {
    await loadCategories();
    await refresh();
  } catch (error) {
    showToast(error.message);
    console.error(error);
  }
}
startApp();
