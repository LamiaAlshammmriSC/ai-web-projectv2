//const API = "http://localhost:5000/api";
const API = "/api";
const LABELS = {
  positive: { text: "إيجابي", emoji: "😊", color: "var(--positive)" },
  neutral:  { text: "محايد",  emoji: "😐", color: "var(--neutral)" },
  negative: { text: "سلبي",   emoji: "😞", color: "var(--negative)" },
};

const $ = (id) => document.getElementById(id);
const textInput = $("textInput");
const analyzeBtn = $("analyzeBtn");
let lastText = "";

// ---------- أدوات مساعدة ----------
async function request(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "حدث خطأ");
  return data;
}

function toast(msg, isError = false) {
  const t = $("toast");
  t.textContent = msg;
  t.className = "show" + (isError ? " error" : "");
  clearTimeout(t._timer);
  t._timer = setTimeout(() => (t.className = ""), 3000);
}

function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------- التحليل ----------
async function analyze() {
  const text = textInput.value.trim();
  if (!text) return toast("اكتب نص أولاً", true);

  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "جاري التحليل...";
  try {
    const result = await request("/analyze", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    lastText = text;
    showResult(result);
    loadHistory();
    loadStats();
  } catch (err) {
    toast(err.message === "Failed to fetch"
      ? "الخادم غير شغال! شغّل app.py أولاً" : err.message, true);
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "تحليل النص";
  }
}

function showResult({ sentiment, confidence, scores }) {
  const info = LABELS[sentiment];
  $("resultCard").classList.remove("hidden");
  $("resultEmoji").textContent = info.emoji;
  $("resultLabel").textContent = info.text;
  $("resultLabel").className = "label-" + sentiment;
  $("resultConfidence").textContent = `نسبة الثقة: ${confidence}%`;

  $("scoreBars").innerHTML = Object.keys(LABELS).map((key) => `
    <div class="bar">
      <div class="bar-label"><span>${LABELS[key].text}</span><span>${scores[key] ?? 0}%</span></div>
      <div class="bar-track">
        <div class="bar-fill" style="width:0;background:${LABELS[key].color}" data-w="${scores[key] ?? 0}"></div>
      </div>
    </div>`).join("");

  // حركة الأشرطة
  requestAnimationFrame(() => {
    document.querySelectorAll(".bar-fill").forEach((b) => (b.style.width = b.dataset.w + "%"));
  });
}

// ---------- تصحيح النتيجة (تعليم النموذج) ----------
async function sendFeedback(label) {
  if (!lastText) return;
  try {
    const r = await request("/feedback", {
      method: "POST",
      body: JSON.stringify({ text: lastText, label }),
    });
    toast(`شكراً! تم إعادة تدريب النموذج على ${r.trained_on} مثال ✅`);
  } catch (err) {
    toast(err.message, true);
  }
}

// ---------- السجل والإحصائيات ----------
async function loadHistory() {
  const list = $("historyList");
  try {
    const rows = await request("/history");
    if (!rows.length) {
      list.innerHTML = `<li class="empty">لا توجد تحليلات بعد</li>`;
      return;
    }
    list.innerHTML = rows.map((r) => `
      <li>
        <span class="badge ${r.sentiment}">${LABELS[r.sentiment].text}</span>
        <div class="h-text">
          ${escapeHTML(r.text)}
          <div class="h-meta">${r.created_at} · ثقة ${r.confidence}%</div>
        </div>
        <button class="del" data-id="${r.id}" title="حذف">🗑️</button>
      </li>`).join("");
  } catch {
    list.innerHTML = `<li class="empty">تعذر الاتصال بالخادم أو قاعدة البيانات</li>`;
  }
}

async function loadStats() {
  try {
    const s = await request("/stats");
    $("statPositive").textContent = s.positive;
    $("statNeutral").textContent = s.neutral;
    $("statNegative").textContent = s.negative;
  } catch { /* يتم تجاهلها */ }
}

async function deleteItem(id) {
  try {
    await request(`/history/${id}`, { method: "DELETE" });
    loadHistory();
    loadStats();
  } catch (err) {
    toast(err.message, true);
  }
}

// ---------- الأحداث ----------
analyzeBtn.addEventListener("click", analyze);
textInput.addEventListener("input", () => {
  $("charCount").textContent = `${textInput.value.length} / 2000`;
});
textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && e.ctrlKey) analyze(); // Ctrl+Enter للتحليل
});
document.querySelectorAll(".fb").forEach((btn) =>
  btn.addEventListener("click", () => sendFeedback(btn.dataset.label))
);
$("historyList").addEventListener("click", (e) => {
  const btn = e.target.closest(".del");
  if (btn) deleteItem(btn.dataset.id);
});

loadHistory();
loadStats();
