/* API 调用封装 */
const API = {
  async get(url) {
    const resp = await fetch(url);
    return resp.json();
  },

  async post(url, data = {}) {
    const resp = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return resp.json();
  },

  // 系统检测
  checkAll() { return this.get("/api/system/check-all"); },
  checkNodeJS()   { return this.get("/api/system/check-nodejs"); },
  checkGit()      { return this.get("/api/system/check-git"); },
  checkClaude()   { return this.get("/api/system/check-claude"); },
  checkCCSwitch() { return this.get("/api/system/check-ccswitch"); },

  // 安装操作（返回 task_id）
  installNodeJS() { return this.post("/api/install/nodejs"); },
  installGit() { return this.post("/api/install/git"); },
  installClaudeCode() { return this.post("/api/install/claude-code"); },
  installCCSwitchGUI() { return this.post("/api/install/ccswitch-gui"); },
  fixPolicy() { return this.post("/api/install/fix-policy"); },
  fixRegistry() { return this.post("/api/install/fix-registry"); },
  autoFix(fixes) { return this.post("/api/install/auto-fix", { fixes }); },
  upgradeComponent(comp) { return this.post("/api/install/upgrade/" + comp); },
  launchPowerShell() { return this.post("/api/install/launch-powershell"); },
  clearCheckCache() { return this.post("/api/system/clear-detect-cache"); },
  launchCCSwitch() { return this.post("/api/install/launch-ccswitch"); },
  launchClaude() { return this.post("/api/install/launch-claude"); },
  installColorCC() { return this.post("/api/install/colorcc"); },
  checkColorCC() { return this.get("/api/install/colorcc-check"); },
  installWinTerm() { return this.post("/api/install/winterm"); },
  checkWinTerm() { return this.get("/api/system/check-winterm"); },
  startupChecks() { return this.get("/api/system/startup-checks"); },

  // 订阅 SSE 进度
  subscribeProgress(taskId, onUpdate, onComplete, onError) {
    const es = new EventSource(`/api/install/progress/${taskId}`);
    es.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onUpdate(data);
      if (data.done) {
        es.close();
        if (data.error) {
          onError(data.error, data.error_detail || null);
        } else {
          onComplete(data);
        }
      }
    };
    es.onerror = () => { es.close(); onError("SSE 连接失败", null); };
    return es;
  },

  // 配置管理
  getProviders() { return this.get("/api/config/providers"); },
  writeConfig(provider, apiKey, models = {}, baseUrl = "") {
    return this.post("/api/config/write", {
      provider,
      api_key: apiKey,
      haiku_model: models.haiku || "",
      sonnet_model: models.sonnet || "",
      opus_model: models.opus || "",
      base_url: baseUrl,
    });
  },
  getCurrentConfig() { return this.get("/api/config/current"); },

  // 教程
  getTutorials() { return this.get("/api/tutorial/list"); },
};

/* Toast 通知 */
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
