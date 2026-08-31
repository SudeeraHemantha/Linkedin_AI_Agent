// background.js - Enterprise Manifest V3 Service Worker
const API_BASE = "http://127.0.0.1:8000/api";

console.log("[LinkedIn AI Agent] Background Service Worker initialized.");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "TRIGGER_AUTO_APPLY") {
    fetch(`${API_BASE}/agent/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request.payload || { keywords: "Software Engineer", location: "Remote" })
    })
      .then(res => res.json())
      .then(data => sendResponse({ status: "success", data }))
      .catch(err => sendResponse({ status: "error", message: err.message }));
    
    return true; // Asynchronous sendResponse
  }

  if (request.action === "CHECK_BACKEND_STATUS") {
    fetch(`${API_BASE}/linkedin/status`)
      .then(res => res.json())
      .then(data => sendResponse({ status: "success", data }))
      .catch(err => sendResponse({ status: "error", message: err.message }));

    return true;
  }

  if (request.action === "FETCH_APPLICATIONS") {
    fetch(`${API_BASE}/applications?user_id=1`)
      .then(res => res.json())
      .then(data => sendResponse({ status: "success", data }))
      .catch(err => sendResponse({ status: "error", message: err.message }));

    return true;
  }
});
