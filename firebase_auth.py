"""Backend Python untuk Firebase Auth dan profil Firestore via HTTPS REST."""
import json
import re
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote
from urllib.error import HTTPError, URLError
import firebase_config as config

ROLES = {'admin', 'pendaftaran', 'dokter', 'perawat', 'farmasi', 'kasir', 'pengunjung'}
MESSAGES = {
    'EMAIL_EXISTS': 'Email sudah terdaftar. Silakan masuk atau reset password.',
    'INVALID_LOGIN_CREDENTIALS': 'Email atau password salah.',
    'INVALID_PASSWORD': 'Email atau password salah.', 'EMAIL_NOT_FOUND': 'Email atau password salah.',
    'USER_DISABLED': 'Akun dinonaktifkan.', 'INVALID_EMAIL': 'Alamat email tidak valid.',
    'OPERATION_NOT_ALLOWED': 'Aktifkan Email/Password di Firebase Authentication.',
    'TOO_MANY_ATTEMPTS_TRY_LATER': 'Terlalu banyak percobaan. Coba kembali nanti.',
    'API_KEY_INVALID': 'API key Firebase tidak valid. Periksa firebase_config.py.',
    'PERMISSION_DENIED': 'Akses Firestore ditolak. Periksa rules Firebase.',
    'NOT_FOUND': 'Profil belum ditemukan di Firestore. Hubungi pengelola.',
    'WEAK_PASSWORD': 'Password belum memenuhi kebijakan Firebase.',
    'INVALID_REFRESH_TOKEN': 'Sesi berakhir. Silakan masuk kembali.',
    'TOKEN_EXPIRED': 'Sesi berakhir. Silakan masuk kembali.',
}

class AuthError(Exception):
    def __init__(self, message, code='INVALID_REQUEST', status=400):
        super().__init__(message)
        self.code, self.status = code, status


def request(url, payload=None, method='POST', token=None, form=False):
    """Hanya dipanggil dengan URL layanan Google yang dibentuk di backend."""
    headers = {'Accept': 'application/json', 'X-Firebase-Locale': 'id'}
    data = None
    if payload is not None:
        headers['Content-Type'] = 'application/x-www-form-urlencoded' if form else 'application/json'
        data = (urlencode(payload) if form else json.dumps(payload)).encode('utf-8')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    try:
        with urlopen(Request(url, data=data, headers=headers, method=method), timeout=20) as response:
            return json.load(response)
    except HTTPError as exc:
        try:
            error = json.load(exc).get('error', {})
            code = str(error.get('message', error.get('status', 'UNKNOWN'))).split(' : ')[0]
            message = MESSAGES.get(code) or MESSAGES.get(error.get('status'))
        except (ValueError, AttributeError):
            code, message = 'UNKNOWN', None
        raise AuthError(message or 'Firebase menolak permintaan. Periksa konfigurasi dan coba kembali.', code, 429 if exc.code == 429 else 400) from None
    except (URLError, TimeoutError, OSError):
        raise AuthError('Tidak dapat terhubung ke Firebase. Periksa koneksi internet.', 'NETWORK', 503) from None


def api_key():
    if not config.API_KEY or 'GANTI' in config.API_KEY:
        raise AuthError('Isi API_KEY pada firebase_config.py.')
    return quote(config.API_KEY, safe='')


def auth(action, payload):
    return request('https://identitytoolkit.googleapis.com/v1/accounts:' + action + '?key=' + api_key(), payload)


def profile_path(uid):
    return 'https://firestore.googleapis.com/v1/projects/' + quote(config.PROJECT_ID, safe='') + '/databases/(default)/documents/profiles/' + quote(uid, safe='')


def email_value(value):
    if not isinstance(value, str) or len(value) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value.strip()):
        raise AuthError('Masukkan alamat email yang valid.')
    return value.strip()


def get_profile(token):
    account = (auth('lookup', {'idToken': token['idToken']}).get('users') or [{}])[0]
    if account.get('localId') != token['localId']:
        raise AuthError('Sesi tidak valid.', status=401)
    doc = request(profile_path(token['localId']), method='GET', token=token['idToken'])
    fields = doc.get('fields', {})
    def val(key):
        return fields.get(key, {}).get('stringValue', '')
    if val('status') == 'disabled':
        raise AuthError('Akun dinonaktifkan oleh pengelola.', status=403)
    verified = bool(account.get('emailVerified'))
    role = val('role') if verified and val('status') == 'approved' and val('role') in ROLES else 'pengunjung'
    return dict(id=token['localId'], username=val('username'), name=val('name'), email=account.get('email', ''),
                phone=val('phone'), requestedRole=val('requestedRole'), role=role, emailVerified=verified, status=val('status'))


def register(data):
    def string(key):
        value = data.get(key, '')
        return value if isinstance(value, str) else ''
    name, username, phone = string('name').strip(), string('username').strip().lower(), string('phone').strip()
    email, role, password = email_value(string('email')), string('requestedRole'), string('password')
    if not (1 <= len(name) <= 100 and re.fullmatch(r'[a-z0-9._-]{3,30}', username) and len(phone) <= 25 and role in ROLES and 8 <= len(password) <= 4096 and password == string('confirm')):
        raise AuthError('Periksa nama, username, nomor HP, peran dan konfirmasi password (minimal 8 karakter).')
    token = auth('signUp', {'email': email, 'password': password, 'returnSecureToken': True})
    values = dict(name=name, username=username, email=token['email'], phone=phone, requestedRole=role, role='pengunjung', status='pending')
    fields = {key: {'stringValue': value} for key, value in values.items()}
    try:
        request(profile_path(token['localId']) + '?currentDocument.exists=false', {'fields': fields}, method='PATCH', token=token['idToken'])
    except AuthError as exc:
        try:
            auth('delete', {'idToken': token['idToken']})
        except AuthError:
            raise AuthError('Profil gagal dibuat. Akun Auth mungkin sudah ada; hubungi pengelola Firebase.') from None
        raise exc
    try:
        auth('sendOobCode', {'requestType': 'VERIFY_EMAIL', 'idToken': token['idToken']})
        sent = True
    except AuthError:
        sent = False
    return {'verificationSent': sent}


def login(data):
    email = email_value(data.get('email'))
    password = data.get('password')
    if not isinstance(password, str) or not 1 <= len(password) <= 4096:
        raise AuthError('Masukkan password.')
    token = auth('signInWithPassword', {'email': email, 'password': password, 'returnSecureToken': True})
    return token, get_profile(token)


def refresh(token):
    result = request('https://securetoken.googleapis.com/v1/token?key=' + api_key(),
                     {'grant_type': 'refresh_token', 'refresh_token': token['refreshToken']}, form=True)
    return {'idToken': result['id_token'], 'refreshToken': result['refresh_token'], 'localId': result['user_id']}


def reset(data):
    email = email_value(data.get('email'))
    try:
        auth('sendOobCode', {'requestType': 'PASSWORD_RESET', 'email': email})
    except AuthError as exc:
        if exc.code != 'EMAIL_NOT_FOUND':
            raise
    return {'ok': True}
