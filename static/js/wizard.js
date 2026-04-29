/* 向导流程控制 */
class InstallWizard {
  constructor(installFn, options = {}) {
    this.installFn = installFn;
    this.title = options.title || "正在安装...";
    this.successMsg = options.successMsg || "安装完成！";
    this.taskId = null;
    this.eventSource = null;
  }

  getElements() {
    return {
      statusIcon: document.getElementById("install-status-icon"),
      statusText: document.getElementById("install-status-text"),
      progressBar: document.getElementById("install-progress-bar"),
      progressText: document.getElementById("install-progress-text"),
      logWindow: document.getElementById("install-log"),
      startBtn: document.getElementById("install-start-btn"),
      retryBtn: document.getElementById("install-retry-btn"),
    };
  }

  async start() {
    const els = this.getElements();
    els.startBtn.disabled = true;
    els.startBtn.textContent = "⏳ 准备中...";
    if (els.retryBtn) els.retryBtn.style.display = "none";

    els.statusIcon.textContent = "⏳";
    els.statusText.textContent = "正在启动安装...";

    try {
      const resp = await this.installFn();
      if (!resp.success || !resp.task_id) {
        this.showError(resp.error || "启动失败");
        return;
      }
      this.taskId = resp.task_id;
      this.subscribe();
    } catch (e) {
      this.showError(e.message);
    }
  }

  subscribe() {
    this.eventSource = API.subscribeProgress(
      this.taskId,
      (data) => this.onUpdate(data),
      (data) => this.onComplete(data),
      (error) => this.showError(error),
    );
  }

  onUpdate(data) {
    const els = this.getElements();
    if (els.progressBar) els.progressBar.style.width = data.progress + "%";
    if (els.progressText) els.progressText.textContent = `${Math.round(data.progress)}%`;

    if (data.message) {
      if (els.statusText) els.statusText.textContent = data.message;
    }

    if (data.step === "installing" && data.progress >= 90) {
      if (els.statusIcon) els.statusIcon.textContent = "✅";
    }
  }

  onComplete(data) {
    const els = this.getElements();
    if (els.progressBar) els.progressBar.style.width = "100%";
    if (els.progressText) els.progressText.textContent = "100%";
    if (els.statusIcon) els.statusIcon.textContent = "✅";
    if (els.statusText) els.statusText.textContent = this.successMsg;
    if (els.startBtn) {
      els.startBtn.textContent = "✅ 安装完成";
      els.startBtn.classList.remove("btn-primary");
      els.startBtn.classList.add("btn-success");
    }

    // 显示下一步
    const nextEl = document.getElementById("install-next-step");
    if (nextEl) nextEl.style.display = "block";

    showToast(this.successMsg, "success");
  }

  showError(error) {
    const els = this.getElements();
    els.statusIcon.textContent = "❌";
    els.statusText.textContent = "安装失败";
    if (els.progressText) els.progressText.textContent = error;
    if (els.startBtn) {
      els.startBtn.disabled = false;
      els.startBtn.textContent = "🔄 重试";
    }
    if (els.retryBtn) els.retryBtn.style.display = "inline-flex";
    showToast(error, "error");
  }

  destroy() {
    if (this.eventSource) this.eventSource.close();
  }
}
