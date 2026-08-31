// popup.js - Extension Controller
document.addEventListener('DOMContentLoaded', () => {
  const statusBadge = document.getElementById('statusBadge');
  const btnTrigger = document.getElementById('btnTrigger');
  const btnDashboard = document.getElementById('btnDashboard');
  const appliedCount = document.getElementById('appliedCount');
  const keywordsInput = document.getElementById('keywords');
  const locationInput = document.getElementById('location');

  // 1. Check backend status
  chrome.runtime.sendMessage({ action: "CHECK_BACKEND_STATUS" }, (response) => {
    if (response && response.status === "success") {
      statusBadge.textContent = "BACKEND ONLINE";
      statusBadge.classList.remove('offline');
    } else {
      statusBadge.textContent = "OFFLINE";
      statusBadge.classList.add('offline');
    }
  });

  // 2. Fetch total applications count
  chrome.runtime.sendMessage({ action: "FETCH_APPLICATIONS" }, (response) => {
    if (response && response.status === "success" && Array.isArray(response.data)) {
      appliedCount.textContent = response.data.length;
    }
  });

  // 3. Trigger auto apply from popup
  btnTrigger.addEventListener('click', () => {
    const keywords = keywordsInput.value || "Software Engineer";
    const location = locationInput.value || "Remote";

    btnTrigger.textContent = "Hunting in progress...";
    btnTrigger.disabled = true;

    chrome.runtime.sendMessage({
      action: "TRIGGER_AUTO_APPLY",
      payload: { keywords, location }
    }, (response) => {
      btnTrigger.textContent = "🚀 Launch Groq AI Auto-Apply";
      btnTrigger.disabled = false;

      if (response && response.status === "success") {
        appliedCount.textContent = parseInt(appliedCount.textContent || "0") + 1;
      }
    });
  });

  // 4. Open Local Web App Dashboard
  btnDashboard.addEventListener('click', () => {
    chrome.tabs.create({ url: "http://localhost:3000" });
  });
});
