"""1shot-CC — Claude Code 一键安装向导入口"""
import socket
import sys
import threading
import webbrowser
from app import create_app


def find_free_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def main():
    app = create_app()
    port = find_free_port()

    threading.Thread(
        target=lambda: webbrowser.open(f"http://127.0.0.1:{port}"),
        daemon=True,
    ).start()

    print(f"1shot-CC 已启动: http://127.0.0.1:{port}")
    print("关闭此窗口将退出程序。")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
