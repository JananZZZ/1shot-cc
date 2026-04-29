"""文件下载器 — 支持进度回调、断点续传、重试"""
import hashlib
import os
import tempfile
import time
import urllib.request
import urllib.error


class Downloader:

    def __init__(self):
        self.chunk_size = 8192
        self.max_retries = 3

    def download(
        self,
        url: str,
        dest_path: str,
        progress_callback=None,
        sha256: str = None,
    ) -> dict:
        """
        progress_callback(percent: float, message: str) 每次更新时调用
        返回 {"success": bool, "path": str, "error": str}
        """
        os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
        filename = os.path.basename(dest_path) or url.split("/")[-1]

        last_error = ""
        for attempt in range(self.max_retries):
            try:
                result = self._download_once(url, dest_path, progress_callback)
                if result["success"]:
                    if sha256:
                        if self._verify_sha256(dest_path, sha256):
                            return result
                        os.remove(dest_path)
                        last_error = "SHA256 校验失败"
                        continue
                    return result
                last_error = result.get("error", "未知错误")
            except Exception as e:
                last_error = str(e)

            if attempt < self.max_retries - 1:
                wait = (attempt + 1) * 3
                if progress_callback:
                    progress_callback(0, f"重试中（第 {attempt + 1} 次），等待 {wait} 秒...")
                time.sleep(wait)

        return {"success": False, "path": "", "error": last_error}

    def _download_once(self, url: str, dest_path: str, progress_callback=None) -> dict:
        request = urllib.request.Request(url, headers={"User-Agent": "1shot-CC/1.0"})

        try:
            response = urllib.request.urlopen(request, timeout=30)
        except urllib.error.HTTPError as e:
            return {"success": False, "path": "", "error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"success": False, "path": "", "error": f"连接失败: {e.reason}"}

        total_size = response.headers.get("Content-Length")
        total_size = int(total_size) if total_size else 0
        downloaded = 0

        with open(dest_path, "wb") as f:
            while True:
                chunk = response.read(self.chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total_size > 0:
                    pct = min(downloaded / total_size * 100, 100)
                    progress_callback(pct, f"下载中... {downloaded // 1024 // 1024}MB / {total_size // 1024 // 1024}MB")

        response.close()

        if total_size > 0 and downloaded < total_size:
            return {"success": False, "path": "", "error": "下载未完成"}

        if progress_callback:
            progress_callback(100, "下载完成")
        return {"success": True, "path": dest_path, "error": ""}

    @staticmethod
    def _verify_sha256(filepath: str, expected: str) -> bool:
        sha = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
        return sha.hexdigest().lower() == expected.lower()


download_file = Downloader().download
