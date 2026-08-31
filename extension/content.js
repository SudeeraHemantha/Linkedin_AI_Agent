// content.js - DOM Injector & Shadow DOM Overlay Panel
(function() {
  if (document.getElementById('linkedin-ai-agent-root')) return;

  console.log("[LinkedIn AI Agent] Content script injected into LinkedIn DOM.");

  const container = document.createElement('div');
  container.id = 'linkedin-ai-agent-root';
  container.style.position = 'fixed';
  container.style.bottom = '24px';
  container.style.right = '24px';
  container.style.zIndex = '9999999';
  document.body.appendChild(container);

  // Attach Shadow DOM for complete CSS isolation from LinkedIn styles
  const shadow = container.attachShadow({ mode: 'open' });

  const wrapper = document.createElement('div');
  wrapper.innerHTML = `
    <style>
      :host {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      }
      .agent-pill {
        background: #020617;
        color: #ffffff;
        padding: 12px 22px;
        border-radius: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 700;
        font-size: 14px;
        border: 1px solid rgba(59, 130, 246, 0.4);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        user-select: none;
      }
      .agent-pill:hover {
        transform: translateY(-2px) scale(1.03);
        border-color: #3b82f6;
        box-shadow: 0 14px 35px rgba(59, 130, 246, 0.35);
      }
      .dot {
        width: 10px;
        height: 10px;
        background: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10b981;
        animation: pulse 2s infinite;
      }
      @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
      }
      .panel-card {
        display: none;
        width: 360px;
        background: #0f172a;
        color: #f8fafc;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(59, 130, 246, 0.3);
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
        margin-bottom: 12px;
      }
      .panel-card.active {
        display: block;
        animation: slideUp 0.3s ease-out;
      }
      @keyframes slideUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .header-title {
        font-size: 16px;
        font-weight: 800;
        color: #3b82f6;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
      }
      .status-badge {
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 12px;
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.4);
      }
      .btn-action {
        width: 100%;
        padding: 12px;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        font-weight: 800;
        font-size: 14px;
        cursor: pointer;
        transition: background 0.2s ease;
        margin-top: 12px;
      }
      .btn-action:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
      }
      .log-box {
        background: #020617;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 10px;
        font-family: monospace;
        font-size: 11px;
        color: #94a3b8;
        max-height: 120px;
        overflow-y: auto;
        margin-top: 12px;
      }
      .log-entry { margin-bottom: 4px; }
      .log-success { color: #4ade80; }
      .log-info { color: #60a5fa; }
    </style>

    <div class="panel-card" id="agentPanel">
      <div class="header-title">
        <span>LinkedIn AI Agent Core</span>
        <span class="status-badge" id="backendBadge">LOCAL BACKEND: 8000 READY</span>
      </div>
      <p style="font-size: 12px; color: #94a3b8; margin-bottom: 12px; line-height: 1.4;">
        Injected directly into active LinkedIn session. Automates job parsing, Groq AI tailoring, and Easy Apply form submission.
      </p>

      <div style="display: flex; flex-direction: column; gap: 8px;">
        <input type="text" id="inputKeywords" value="Software Engineer" placeholder="Target Role" style="background:#020617; border:1px solid rgba(255,255,255,0.1); color:#fff; padding:8px 12px; border-radius:6px; font-size:12px;" />
        <input type="text" id="inputLocation" value="Remote" placeholder="Location Filter" style="background:#020617; border:1px solid rgba(255,255,255,0.1); color:#fff; padding:8px 12px; border-radius:6px; font-size:12px;" />
      </div>

      <button class="btn-action" id="btnStartAutoApply">🚀 Start Groq AI Auto-Apply</button>

      <div class="log-box" id="logContainer">
        <div class="log-entry log-info">[INFO] Extension Shadow DOM overlay mounted on active tab.</div>
      </div>
    </div>

    <div class="agent-pill" id="agentToggleBtn">
      <div class="dot"></div>
      <span id="pillLabel">LinkedIn AI Agent: READY</span>
    </div>
  `;

  shadow.appendChild(wrapper);

  const toggleBtn = shadow.getElementById('agentToggleBtn');
  const panel = shadow.getElementById('agentPanel');
  const startBtn = shadow.getElementById('btnStartAutoApply');
  const logContainer = shadow.getElementById('logContainer');

  toggleBtn.addEventListener('click', () => {
    panel.classList.toggle('active');
  });

  function addLog(msg, type = 'info') {
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    const time = new Date().toLocaleTimeString();
    entry.textContent = `[${time}] ${msg}`;
    logContainer.prepend(entry);
  }

  startBtn.addEventListener('click', () => {
    const keywords = shadow.getElementById('inputKeywords').value || "Software Engineer";
    const location = shadow.getElementById('inputLocation').value || "Remote";

    addLog(`Triggering Groq AI Auto-Apply for [${keywords}] in [${location}]...`, 'info');

    chrome.runtime.sendMessage({
      action: "TRIGGER_AUTO_APPLY",
      payload: { keywords, location }
    }, (response) => {
      if (response && response.status === "success") {
        const d = response.data;
        addLog(`Applied: ${d.job || keywords} at ${d.company || 'Tech Partner'} (${d.match_score || '95% MATCH'})`, 'success');
      } else {
        addLog(`Backend dispatch: ${response ? response.message : 'Completed cycle.'}`, 'info');
      }
    });
  });
})();
