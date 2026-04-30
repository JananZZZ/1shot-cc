/* 安装向导流程控制 */
class InstallWizard {
  constructor(installFn, options = {}) {
    this.installFn = installFn;
    this.successMsg = options.successMsg || "安装完成！";
    this.onSuccess = options.onSuccess || null;
    this.taskId = null;
    this.eventSource = null;
    this.started = false;
  }

  getEls() {
    return {
      icon: document.getElementById("icon"),
      status: document.getElementById("status-text"),
      bar: document.getElementById("bar"),
      pct: document.getElementById("pct-text"),
      start: document.getElementById("start-btn"),
      retry: document.getElementById("retry-btn"),
      next: document.getElementById("next-step"),
    };
  }

  async start() {
    if (this.started) return;
    this.started = true;
    const e = this.getEls();
    if (e.start) { e.start.disabled = true; e.start.textContent = "⏳ 正在准备..."; }
    if (e.retry) e.retry.style.display = "none";
    if (e.next) e.next.style.display = "none";
    if (e.icon) { e.icon.textContent = "⏳"; e.icon.classList.remove("done"); }

    try {
      const resp = await this.installFn();
      if (!resp || (!resp.success && !resp.task_id)) {
        this._fail(resp?.error || "启动安装失败");
        return;
      }
      this.taskId = resp.task_id;
      this._subscribe();
    } catch (err) {
      this._fail(err.message);
    }
  }

  _subscribe() {
    this.eventSource = API.subscribeProgress(
      this.taskId,
      (d) => this._onUpdate(d),
      (d) => this._onDone(d),
      (e) => this._fail(e),
    );
  }

  _onUpdate(data) {
    const e = this.getEls();
    if (e.bar) e.bar.style.width = data.progress + "%";
    if (e.pct) e.pct.textContent = `${Math.round(data.progress)}% — ${data.message || ""}`;
    if (data.message && e.status) e.status.textContent = data.message;
    if (data.progress >= 90 && e.icon) {
      e.icon.textContent = "✅";
      e.icon.classList.add("done");
    }
  }

  _onDone() {
    const e = this.getEls();
    if (e.bar) e.bar.style.width = "100%";
    if (e.pct) e.pct.textContent = "100% — 完成！";
    if (e.icon) { e.icon.textContent = "✅"; e.icon.classList.add("done"); }
    if (e.status) e.status.textContent = this.successMsg;
    if (e.start) {
      e.start.textContent = "✅ 装好了！";
      e.start.classList.remove("btn-primary");
      e.start.classList.add("btn-accent");
      e.start.disabled = true;
    }
    if (e.next) e.next.style.display = "block";
    showToast(this.successMsg, "success");
    if (this.onSuccess) this.onSuccess();
  }

  _fail(error) {
    this.started = false;
    const e = this.getEls();
    if (e.icon) e.icon.textContent = "❌";
    if (e.status) e.status.textContent = "安装出错了";
    if (e.pct) e.pct.textContent = error || "未知错误";
    if (e.start) {
      e.start.disabled = false;
      e.start.textContent = "🔄 重试";
    }
    if (e.retry) e.retry.style.display = "inline-flex";
    showToast(error || "安装失败", "error");
  }

  destroy() {
    if (this.eventSource) { this.eventSource.close(); this.eventSource = null; }
  }
}
