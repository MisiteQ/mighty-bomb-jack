#!/usr/bin/env python3
"""Tiny static server for the offline Bomb Jack build.

Also accepts POST /__save?name=<file> to persist emulator save states
to the saves/ directory on disk, so archives survive page reloads.
"""
import functools
import http.server
import os
import socketserver
import sys
import webbrowser
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.abspath(__file__))
DIST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, 'dist')
DIST = DIST if os.path.isabs(DIST) else os.path.join(BASE, DIST)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
SAVES_DIR = os.path.join(DIST, 'saves')
os.makedirs(SAVES_DIR, exist_ok=True)

# pythonw（无窗口后台运行）模式下没有控制台，sys.stdout/stderr 不可用，
# 会导致请求处理卡死/崩溃 —— 统一重定向到日志文件（UTF-8，每次启动覆盖）
if sys.stdout is None or sys.stderr is None:
    sys.stdout = sys.stderr = open(
        os.path.join(BASE, 'server.log'), 'w', buffering=1, encoding='utf-8', errors='replace')


def safe_print(*a):
    """任何控制台编码下都不能因打印而崩溃"""
    try:
        print(*a)
    except Exception:
        try:
            sys.stderr.write(' '.join(str(x) for x in a) + '\n')
        except Exception:
            pass


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DIST, **kw)

    def do_GET(self):
        # 列出 saves/ 目录内容 (供存档槽位界面使用)
        if self.path.startswith('/__list'):
            import json
            import time
            items = []
            if os.path.isdir(SAVES_DIR):
                for n in sorted(os.listdir(SAVES_DIR)):
                    p = os.path.join(SAVES_DIR, n)
                    if os.path.isfile(p):
                        st = os.stat(p)
                        items.append({'name': n, 'size': st.st_size,
                                      'mtime': time.strftime('%Y-%m-%d %H:%M', time.localtime(st.st_mtime)),
                                      'ts': st.st_mtime})
            body = json.dumps(items).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        # 删除 saves/ 下的文件 (存档槽位删除功能)
        if self.path.startswith('/__delete'):
            q = parse_qs(urlparse(self.path).query)
            name = os.path.basename(q.get('name', [''])[0])
            p = os.path.join(SAVES_DIR, name) if name else ''
            if p and os.path.isfile(p):
                os.remove(p)
                sys.stderr.write('[delete] %s\n' % p)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            return
        super().do_GET()

    def do_POST(self):
        if not self.path.startswith('/__save'):
            self.send_error(404)
            return
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length)
            q = parse_qs(urlparse(self.path).query)
            name = os.path.basename(q.get('name', ['game.state'])[0])
            if not name:
                self.send_error(400, 'bad name')
                return
            if name.endswith('.png'):
                out_dir = os.path.join(SAVES_DIR, 'screenshots')
                os.makedirs(out_dir, exist_ok=True)
            else:
                out_dir = SAVES_DIR
            path = os.path.join(out_dir, name)
            with open(path, 'wb') as f:
                f.write(data)
            sys.stderr.write('[save] %s (%d bytes)\n' % (path, len(data)))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, fmt, *args):
        sys.stderr.write('%s\n' % (fmt % args))

    def end_headers(self):
        # wasm needs the right mime; also avoid any caching surprises
        if self.path.endswith('.wasm'):
            self.send_header('Content-Type', 'application/wasm')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


socketserver.TCPServer.allow_reuse_address = True
url = 'http://127.0.0.1:%d/index.html' % PORT
try:
    httpd = socketserver.TCPServer(('127.0.0.1', PORT), Handler)
except OSError:
    # 端口被占用 = 服务器已在运行，直接打开浏览器即可
    safe_print('Server already running at', url)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    sys.exit(0)

# 记录 PID，供 stop_server.bat 停止服务用
try:
    with open(os.path.join(BASE, 'server.pid'), 'w') as f:
        f.write(str(os.getpid()))
except Exception:
    pass
safe_print('Serving', DIST, 'at', url)
try:
    webbrowser.open(url)
except Exception:
    pass
try:
    httpd.serve_forever()
finally:
    try:
        os.remove(os.path.join(BASE, 'server.pid'))
    except Exception:
        pass
