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
      errorBox: document.getElementById("error-detail-box"),
      errorTitle: document.getElementById("err-title"),
      errorCauses: document.getElementById("err-causes"),
      errorManual: document.getElementById("err-manual"),
      errorAutoBtn: document.getElementById("err-auto-fix-btn"),
    };
  }

  async start() {
    if (this.started) return;
    this.started = true;
    const e = this.getEls();
    if (e.start) { e.start.disabled = true; e.start.textContent = "⏳ 正在准备..."; }
    if (e.retry) e.retry.style.display = "none";
    if (e.next) e.next.style.display = "none";
    if (e.errorBox) e.errorBox.style.display = "none";
    if (e.icon) { e.icon.textContent = "⏳"; e.icon.classList.remove("done"); }

    try {
      const resp = await this.installFn();
      if (!resp || (!resp.success && !resp.task_id)) {
        this._fail(resp?.error || "启动安装失败", resp?.error_detail || null);
        return;
      }
      this.taskId = resp.task_id;
      this._subscribe();
    } catch (err) {
      this._fail(err.message, null);
    }
  }

  _subscribe() {
    this.eventSource = API.subscribeProgress(
      this.taskId,
      (d) => this._onUpdate(d),
      (d) => this._onDone(d),
      (err, detail) => this._fail(err, detail),
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

  _fail(error, errorDetail) {
    this.started = false;
    const e = this.getEls();
    if (e.icon) e.icon.textContent = "⚠️";
    if (e.status) e.status.textContent = errorDetail?.title || "安装出错了";

    if (errorDetail && errorDetail.causes && errorDetail.causes.length > 0) {
      if (e.pct) e.pct.textContent = "";
      if (e.errorBox) {
        e.errorBox.style.display = "block";
        e.errorBox.classList.add("warning");
        if (e.errorTitle) e.errorTitle.textContent = errorDetail.title || "安装失败";
        if (e.errorCauses) {
          var causesHtml = errorDetail.causes.map(c => `<li>${c}</li>`).join("");
          // CC-Switch: 提醒用户先检查开始菜单
          if (error.indexOf("CC-Switch") > -1 || error.indexOf("ccswitch") > -1) {
            causesHtml = `<li style="color:var(--t1);font-weight:600;">💡 先看看开始菜单里是不是已经有 CC Switch 了？可能早就装好了。</li>` + causesHtml;
          }
          e.errorCauses.innerHTML = causesHtml;
        }
        if (e.errorManual && errorDetail.manual_fix) {
          var manualItems = errorDetail.manual_fix.slice();
          if (errorDetail.hint_cli) {
            manualItems.push("💡 也可以试试「命令行版」安装（npm 国内镜像，更稳定）：返回本页，选择命令行版后重试");
          }
          e.errorManual.innerHTML = manualItems.map(s => {
            const escaped = s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            return `<li>${escaped}</li>`;
          }).join("");
        }
        if (e.errorAutoBtn) {
          if (errorDetail.auto_fix && errorDetail.auto_fix.length > 0) {
            e.errorAutoBtn.style.display = "inline-flex";
            e.errorAutoBtn.onclick = () => this._doAutoFix(errorDetail.auto_fix);
          } else {
            e.errorAutoBtn.style.display = "none";
          }
        }
      }
    } else {
      if (e.pct) e.pct.textContent = error || "未知错误";
      if (e.errorBox) e.errorBox.style.display = "none";
    }

    if (e.start) {
      e.start.disabled = false;
    }
    if (e.retry) e.retry.style.display = "inline-flex";
    showToast(errorDetail?.title || error || "安装失败", "warning");
  }

  async _doAutoFix(fixes) {
    const e = this.getEls();
    if (e.errorAutoBtn) e.errorAutoBtn.disabled = true;
    try {
      const resp = await API.autoFix(fixes);
      if (resp.success && resp.results) {
        const r = resp.results;
        const fixed = [];
        const failed = [];
        if (r.policy?.success) fixed.push("PowerShell 策略");
        else if (r.policy) failed.push("PowerShell 策略: " + (r.policy.error || ""));
        if (r.registry?.success) fixed.push("npm 镜像源");
        else if (r.registry) failed.push("npm 镜像源: " + (r.registry.stderr || r.registry.error || ""));
        let msg = "";
        if (fixed.length > 0) msg += "已修复: " + fixed.join(", ");
        if (failed.length > 0) msg += (msg ? " | " : "") + "未能修复: " + failed.join(", ");
        showToast(msg || "修复完成", fixed.length > 0 ? "success" : "warning");
        if (fixed.length > 0) {
          // 自动重试安装
          setTimeout(() => this.start(), 500);
        }
      }
    } catch (err) {
      showToast("自动修复失败: " + err.message, "error");
    } finally {
      if (e.errorAutoBtn) e.errorAutoBtn.disabled = false;
    }
  }

  destroy() {
    if (this.eventSource) { this.eventSource.close(); this.eventSource = null; }
  }
}
