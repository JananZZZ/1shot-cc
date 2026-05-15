"""1shot-CC — Claude Code 一键安装向导入口"""
import os
import socket
import time
import threading

# ─── 欢迎页基础 HTML（无自动跳转，用于手动打开欣赏） ───
WELCOME_HTML_BASE = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>1shot-CC</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Segoe UI","Microsoft YaHei",system-ui,sans-serif;background:#faf8f5;overflow:hidden;height:100vh;display:flex;align-items:center;justify-content:center;user-select:none}
body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 80% 60% at 50% 40%,rgba(196,117,90,0.04),transparent),radial-gradient(ellipse 50% 50% at 20% 70%,rgba(107,143,113,0.04),transparent)}
.bubble{position:fixed;border-radius:50%;pointer-events:none;z-index:0;will-change:transform}
.bubble.b1{width:180px;height:180px;top:10%;left:5%;background:radial-gradient(circle,rgba(196,117,90,0.12),transparent);animation:floatB 7s ease-in-out infinite}
.bubble.b2{width:120px;height:120px;top:50%;right:8%;background:radial-gradient(circle,rgba(107,143,113,0.10),transparent);animation:floatB 6s ease-in-out 1s infinite}
.bubble.b3{width:90px;height:90px;bottom:15%;left:12%;background:radial-gradient(circle,rgba(196,146,74,0.10),transparent);animation:floatB 8s ease-in-out 2s infinite}
.bubble.b4{width:140px;height:140px;top:25%;right:20%;background:radial-gradient(circle,rgba(196,117,90,0.08),transparent);animation:floatB 7.5s ease-in-out 0.5s infinite}
@keyframes floatB{0%,100%{transform:translateY(0)translateX(0)}25%{transform:translateY(-20px)translateX(10px)}50%{transform:translateY(-8px)translateX(-8px)}75%{transform:translateY(-25px)translateX(5px)}}
main{position:relative;z-index:1;text-align:center;padding:40px 24px;animation:mainIn .8s cubic-bezier(.16,1,.3,1) both}
@keyframes mainIn{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:scale(1)}}
.floats{position:fixed;inset:0;pointer-events:none;z-index:2}
.floats span{position:absolute;font-size:1.6rem;animation:emojiFloat 4s ease-in-out infinite}
.floats span:nth-child(1){top:8%;left:10%;animation-delay:0s}
.floats span:nth-child(2){top:12%;right:12%;animation-delay:.5s;font-size:1.3rem}
.floats span:nth-child(3){top:45%;left:4%;animation-delay:1s;font-size:1.1rem}
.floats span:nth-child(4){bottom:20%;right:6%;animation-delay:1.5s;font-size:1.4rem}
.floats span:nth-child(5){bottom:25%;left:8%;animation-delay:2s;font-size:1.2rem}
.floats span:nth-child(6){top:55%;right:10%;animation-delay:2.5s;font-size:1rem}
@keyframes emojiFloat{0%,100%{transform:translateY(0)rotate(0deg)}50%{transform:translateY(-18px)rotate(5deg)}}
.code-line{font-family:"Consolas","Cascadia Code",monospace;color:rgba(107,143,113,0.7);font-size:1.05rem;letter-spacing:1.5px;margin-bottom:8px;animation:codeIn .6s .2s both;transition:transform .12s}
@keyframes codeIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}
.title{font-family:"Noto Serif SC","Georgia",serif;color:#c4755a;font-size:2.8rem;font-weight:700;letter-spacing:.08em;line-height:1.3;animation:titleIn .7s .3s both}
@keyframes titleIn{from{opacity:0;letter-spacing:.25em}to{opacity:1;letter-spacing:.08em}}
.subtitle{color:#5c5344;font-size:1.25rem;margin:14px 0 10px;font-weight:400;animation:fadeUp .6s .5s both}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.tagline{color:#9c9384;font-size:1.15rem;margin:8px 0;animation:fadeUp .6s .65s both}
.bracket{font-family:"Consolas","Cascadia Code",monospace;color:rgba(196,117,90,0.5);font-size:1rem;letter-spacing:2.5px;animation:fadeUp .6s .7s both}
.quote{color:#5c5344;font-size:1.2rem;margin:12px 0 0;font-weight:500;animation:fadeUp .6s .75s both}
.quote em{color:#c4755a;font-style:normal}
footer{position:fixed;bottom:18px;left:0;right:0;text-align:center;z-index:1;color:#bfb8aa;font-size:.85rem;animation:fadeUp .6s 1s both}
.glow{position:fixed;pointer-events:none;z-index:0;width:400px;height:400px;border-radius:50%;background:radial-gradient(circle,rgba(196,117,90,.08),transparent 65%);transform:translate(-50%,-50%)}
</style></head><body>
<div class="glow" id="glow"></div>
<div class="bubble b1"></div><div class="bubble b2"></div><div class="bubble b3"></div><div class="bubble b4"></div>
<div class="floats" id="floats"><span>✨</span><span>🚀</span><span>💻</span><span>🔧</span><span>🤖</span><span>⚡</span></div>
<main id="main-content">
  <p class="code-line" id="code-line">&gt; 1shot-CC.init()</p>
  <h1 class="title">欢 迎 使 用 <br>1shot-CC</h1>
  <p class="subtitle">Claude Code 全流程自动安装配置</p>
  <p class="tagline">人人都可以发挥想象力的 AI 编程时代</p>
  <p class="bracket">&lt; 科技平权 &gt; &nbsp;{ 从您迈出的第一步开始 }</p>
  <p class="quote">开心享用吧 <em>~</em></p>
</main>
<footer>1shot-CC &copy; 2026 &middot; 让每个人都能用上 AI 编程</footer>
<script>
document.addEventListener('mousemove',function(e){
  var cx=e.clientX,cy=e.clientY,w=window.innerWidth,h=window.innerHeight;
  var rx=(cx/w-.5)*20,ry=(cy/h-.5)*18;
  var g=document.getElementById('glow');g.style.left=cx+'px';g.style.top=cy+'px';
  document.querySelectorAll('.bubble').forEach(function(b,i){b.style.transform='translate('+rx*(i+1)*.8+'px,'+ry*(i+1)*.8+'px)'});
  var cl=document.getElementById('code-line');if(cl)cl.style.transform='translateX('+rx*.5+'px)';
  var fl=document.getElementById('floats');if(fl)fl.style.transform='rotate('+rx*.08+'deg)';
  var mc=document.getElementById('main-content');if(mc)mc.style.transform='translate('+rx*.35+'px,'+ry*.3+'px)';
});
</script>
</body></html>"""

# ─── 启动画面 HTML（带轮询+自动跳转，首次启动用） ───
SPLASH_HTML = WELCOME_HTML_BASE.replace(
    "</body></html>",
    """<script>
var FLASK_PORT = __FLASK_PORT__, MIN_DISPLAY = 6000, _startTime = Date.now();
(function poll(n){n=n||0;if(n>180){return}
fetch('/ping').then(function(r){return r.json()}).then(function(d){
if(d.ok){var remain=Math.max(300,MIN_DISPLAY-(Date.now()-_startTime));setTimeout(function(){location.href='http://127.0.0.1:'+FLASK_PORT+'/'},remain)}
else{setTimeout(function(){poll(n+1)},500)}}).catch(function(){setTimeout(function(){poll(n+1)},500)})})();
</script>
</body></html>"""
)


def _find_free_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


_flask_ready_time = 0.0


def main():
    flask_port = _find_free_port()

    try:
        splash_port = _find_free_port()
        splash_srv = _SplashServer(splash_port, flask_port)
        threading.Thread(target=splash_srv.run, daemon=True).start()

        os.startfile(f"http://127.0.0.1:{splash_port}/")
        print(f"1shot-CC 欢迎页: http://127.0.0.1:{splash_port}")

        _run_flask(flask_port)
    except Exception as e:
        _fatal(f"端口错误: {e}")


class _SplashServer:
    def __init__(self, port: int, flask_port: int):
        self._running = True
        self._server = None
        self.flask_port = flask_port
        self.port = port

    def run(self):
        import http.server
        SPLASH = SPLASH_HTML.replace("__FLASK_PORT__", str(self.flask_port))
        handler = self._make_handler(SPLASH)

        class _Srv(http.server.HTTPServer):
            def handle_error(self, request, client_address):
                pass

        self._server = _Srv(("127.0.0.1", self.port), handler)
        try:
            self._server.serve_forever()
        except Exception:
            pass

    def _make_handler(self, splash_content: str):
        import http.server

        class _Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/ping":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"ok":true}')
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(splash_content.encode("utf-8"))

            def log_message(self, format, *args):
                pass

        return _Handler

    def shutdown(self):
        self._running = False
        if self._server:
            try:
                self._server.shutdown()
            except Exception:
                pass


def _probe_port(port: int) -> bool:
    """探测端口是否就绪"""
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=0.3)
        s.close()
        return True
    except Exception:
        return False


def _wait_flask_ready(port: int, timeout: int = 30):
    """等待 Flask 端口就绪"""
    for _ in range(int(timeout / 0.1)):
        if _probe_port(port):
            print(f"Flask 已就绪: http://127.0.0.1:{port}")
            return
        time.sleep(0.1)
    print("Flask 启动超时")


def _save_welcome_html():
    """保存欢迎页 HTML 到临时目录，供导航栏按钮打开"""
    try:
        import tempfile
        welcome_dir = os.path.join(tempfile.gettempdir(), "1shot-cc")
        os.makedirs(welcome_dir, exist_ok=True)
        welcome_path = os.path.join(welcome_dir, "welcome.html")
        html = WELCOME_HTML_BASE.replace("__FLASK_PORT__", "")
        with open(welcome_path, "w", encoding="utf-8") as f:
            f.write(html)
        return welcome_path
    except Exception:
        return None


def _run_flask(port: int):
    from app import create_app
    from app.utils.logger import init as init_logger, info, error

    try:
        log_path = init_logger()
    except Exception:
        log_path = None

    try:
        app = create_app()
    except Exception as e:
        error(f"Flask 创建失败: {e}", exc_info=True)
        _fatal(f"程序启动失败: {e}", log_path)
        return

    global _flask_ready_time
    _flask_ready_time = time.time()

    welcome_file = _save_welcome_html()
    if welcome_file:
        info(f"欢迎页已保存: {welcome_file}")

    _start_watchdog()

    info(f"1shot-CC 已启动: http://127.0.0.1:{port}")
    print(f"1shot-CC 已启动: http://127.0.0.1:{port}")
    print(f"诊断日志: {log_path or '未启用'}")
    print("关闭此窗口将退出程序。")

    try:
        app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)
    except Exception as e:
        error(f"Flask 崩溃: {e}", exc_info=True)
        _fatal(f"程序运行异常: {e}", log_path)


def _start_watchdog():
    """页面引用计数看门狗：只有所有页面关闭后才退出"""
    threading.Thread(target=_watchdog_loop, daemon=True).start()


def _watchdog_loop():
    from app.routes.api_system import get_page_state

    time.sleep(30)
    while True:
        time.sleep(10)
        try:
            last_seen, lock, last_close = get_page_state()
            with lock:
                now = time.time()
                stale = [pid for pid, t in last_seen.items() if now - t > 90]
                for pid in stale:
                    del last_seen[pid]
                should_exit = (len(last_seen) == 0 and
                              last_close > 0 and
                              now - last_close > 15)
            if should_exit:
                os._exit(0)
        except Exception:
            pass


def _fatal(msg: str):
    """致命错误弹窗提示"""
    try:
        import tkinter.messagebox as mb
        mb.showerror("1shot-CC 启动失败", msg)
    except Exception:
        print(msg)
        input("按 Enter 退出...")


if __name__ == "__main__":
    main()
