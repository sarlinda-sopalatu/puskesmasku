"""PuskesmasKu: server Python lokal, tanpa pip, npm, atau hosting."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie, CookieError
import json
import mimetypes
from pathlib import Path
import secrets
from threading import Lock
from time import monotonic
from urllib.parse import urlsplit
import firebase_auth as firebase

ROOT = Path(__file__).resolve().parent
SESSIONS = {}
LOCK = Lock()
SESSION_TTL = 8 * 3600
COOKIE = 'pk_python_sid'

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Jangan mencatat payload/password/token atau query string.
        pass

    def allowed_host(self):
        port = self.server.server_port
        return self.headers.get('Host') in {f'localhost:{port}', f'127.0.0.1:{port}'}

    def reply(self, data, status=200, cookie=None):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        if cookie is not None:
            self.send_header('Set-Cookie', f'{COOKIE}={cookie}; Path=/; HttpOnly; SameSite=Strict' + ('; Max-Age=0' if not cookie else ''))
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def sid(self):
        try:
            cookies = SimpleCookie(self.headers.get('Cookie', ''))
            return cookies[COOKIE].value if COOKIE in cookies else None
        except CookieError:
            return None

    def forget(self):
        with LOCK:
            SESSIONS.pop(self.sid(), None)

    def get_token(self):
        with LOCK:
            entry = SESSIONS.get(self.sid())
            if entry and entry[1] > monotonic():
                return entry[0]
            SESSIONS.pop(self.sid(), None)
        return None

    def set_token(self, sid, token):
        with LOCK:
            now = monotonic()
            for key in list(SESSIONS):
                if SESSIONS[key][1] <= now:
                    del SESSIONS[key]
            SESSIONS[sid] = (token, now + SESSION_TTL)

    def do_GET(self):
        if not self.allowed_host():
            return self.reply({'message': 'Host tidak diizinkan.'}, 403)
        path = urlsplit(self.path).path
        if path == '/api/health':
            return self.reply({'ok': True, 'backend': 'Python'})
        rel = 'index.html' if path == '/' else path.lstrip('/')
        file = (ROOT / rel).resolve()
        allowed = file == ROOT / 'index.html' or (file.parent == ROOT / 'js' and file.suffix == '.js') or (file.parent == ROOT / 'css' and file.suffix == '.css')
        allowed = allowed or (ROOT / 'docs' in file.parents and file.suffix in {'.md', '.png', '.svg'})
        if not allowed or not file.is_file():
            return self.reply({'message': 'Halaman tidak ditemukan.'}, 404)
        body = file.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8' if file.suffix == '.md' else (mimetypes.guess_type(str(file))[0] or 'application/octet-stream'))
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        # API hanya menerima JSON same-origin; lindungi sesi lokal dari situs lain.
        if not self.allowed_host() or self.headers.get('Origin') != 'http://' + self.headers.get('Host', ''):
            return self.reply({'message': 'Origin tidak diizinkan.'}, 403)
        if self.headers.get_content_type() != 'application/json':
            return self.reply({'message': 'Gunakan JSON.'}, 415)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 65536:
                return self.reply({'message': 'Ukuran permintaan tidak valid.'}, 400)
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError
        except (ValueError, UnicodeError):
            return self.reply({'message': 'JSON tidak valid.'}, 400)
        path = urlsplit(self.path).path
        try:
            if path == '/api/auth/register':
                return self.reply(firebase.register(data))
            if path == '/api/auth/reset':
                return self.reply(firebase.reset(data))
            if path == '/api/auth/login':
                self.forget()
                token, info = firebase.login(data)
                sid = secrets.token_urlsafe(32)
                self.set_token(sid, token)
                return self.reply(info, cookie=sid)
            if path == '/api/auth/logout':
                self.forget()
                return self.reply({'ok': True}, cookie='')
            if path in {'/api/auth/restore', '/api/auth/resend-verification'}:
                token = self.get_token()
                if not token:
                    if path.endswith('/restore'):
                        return self.reply(None, cookie='')
                    raise firebase.AuthError('Silakan masuk kembali.', status=401)
                token = firebase.refresh(token)
                info = firebase.get_profile(token)
                self.set_token(self.sid(), token)
                if path.endswith('/restore'):
                    return self.reply(info)
                if not info['emailVerified']:
                    firebase.auth('sendOobCode', {'requestType': 'VERIFY_EMAIL', 'idToken': token['idToken']})
                return self.reply({'ok': True})
            return self.reply({'message': 'Endpoint tidak ditemukan.'}, 404)
        except firebase.AuthError as exc:
            if path.endswith('/restore') or path.endswith('/login'):
                self.forget()
                return self.reply({'message': str(exc), 'code': exc.code}, exc.status, cookie='')
            return self.reply({'message': str(exc), 'code': exc.code}, exc.status)
        except Exception:
            return self.reply({'message': 'Kesalahan backend Python. Periksa konfigurasi Firebase.'}, 500)


def main():
    parser = argparse.ArgumentParser(description='Server lokal PuskesmasKu')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Port harus 1–65535.')
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    except OSError as exc:
        parser.exit(1, f'Gagal membuka port: {exc}. Coba python app.py --port 8080\n')
    print(f'PuskesmasKu | Backend Python aktif: http://localhost:{args.port}/', flush=True)
    print('Tekan Ctrl+C untuk menghentikan server.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer dihentikan.')
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
