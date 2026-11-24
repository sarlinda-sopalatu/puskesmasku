import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from unittest.mock import patch
import app
import firebase_auth as fb

TOKEN = {'idToken': 'test-id', 'refreshToken': 'test-refresh', 'localId': 'uid1', 'email': 'demo@example.com'}
INFO = {'id': 'uid1', 'username': 'demo', 'role': 'pengunjung', 'emailVerified': False, 'status': 'pending'}

class FirebaseTests(unittest.TestCase):
    def test_reset_request(self):
        with patch.object(fb, 'auth', return_value={}) as api:
            self.assertEqual(fb.reset({'email': 'demo@example.com'}), {'ok': True})
            api.assert_called_once_with('sendOobCode', {'requestType': 'PASSWORD_RESET', 'email': 'demo@example.com'})
    def test_reset_unknown_email(self):
        with patch.object(fb, 'auth', side_effect=fb.AuthError('unknown', 'EMAIL_NOT_FOUND')):
            self.assertEqual(fb.reset({'email': 'demo@example.com'}), {'ok': True})
    def test_registration_role_pending(self):
        data = dict(name='Demo', username='demo', phone='', email='demo@example.com', requestedRole='admin', password='abcdefghi', confirm='abcdefghi')
        with patch.object(fb, 'auth', side_effect=[TOKEN, {}]) as auth, patch.object(fb, 'request', return_value={}) as req:
            self.assertTrue(fb.register(data)['verificationSent'])
            fields = req.call_args.args[1]['fields']
            self.assertEqual(fields['role']['stringValue'], 'pengunjung')
            self.assertEqual(fields['requestedRole']['stringValue'], 'admin')
            self.assertEqual(fields['status']['stringValue'], 'pending')
            self.assertNotIn('password', fields)
            self.assertEqual(auth.call_args.args[1]['requestType'], 'VERIFY_EMAIL')
    def test_profile_approval(self):
        fields = {k: {'stringValue': v} for k, v in {'role': 'dokter', 'status': 'approved', 'username': 'demo'}.items()}
        with patch.object(fb, 'auth', return_value={'users': [{'localId': 'uid1', 'emailVerified': False}]}), patch.object(fb, 'request', return_value={'fields': fields}):
            self.assertEqual(fb.get_profile(TOKEN)['role'], 'pengunjung')
        with patch.object(fb, 'auth', return_value={'users': [{'localId': 'uid1', 'emailVerified': True}]}), patch.object(fb, 'request', return_value={'fields': fields}):
            self.assertEqual(fb.get_profile(TOKEN)['role'], 'dokter')
    def test_invalid_email(self):
        with self.assertRaises(fb.AuthError):
            fb.reset({'email': 'bad'})

class ServerTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        self.base = f'http://127.0.0.1:{self.server.server_port}'
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()
        app.SESSIONS.clear()
    def post(self, action, payload=None, cookie=None, origin=None):
        headers = {'Content-Type': 'application/json', 'Origin': origin or self.base}
        if cookie:
            headers['Cookie'] = cookie
        with urlopen(Request(self.base + '/api/auth/' + action, data=json.dumps(payload or {}).encode(), headers=headers), timeout=5) as res:
            return json.load(res), res.headers.get('Set-Cookie', '')
    def test_static_and_health(self):
        with urlopen(self.base + '/') as res:
            self.assertIn(b'PuskesmasKu', res.read())
        with urlopen(self.base + '/api/health') as res:
            self.assertEqual(json.load(res)['backend'], 'Python')
        with self.assertRaises(HTTPError) as e:
            urlopen(self.base + '/firebase_config.py')
        self.assertEqual(e.exception.code, 404)
    def test_session(self):
        with patch.object(fb, 'login', return_value=(TOKEN, INFO)), patch.object(fb, 'refresh', return_value=TOKEN), patch.object(fb, 'get_profile', return_value=INFO):
            info, cookie = self.post('login', {'email':'demo@example.com', 'password':'test'})
            self.assertEqual(info, INFO)
            self.assertIn('HttpOnly', cookie)
            self.assertNotIn('test-refresh', cookie)
            sid = cookie.split(';')[0]
            self.assertEqual(self.post('restore', cookie=sid)[0], INFO)
            self.assertIsNone(self.post('restore')[0])
            self.post('logout', cookie=sid)
            self.assertIsNone(self.post('restore', cookie=sid)[0])
    def test_origin_rejected(self):
        with self.assertRaises(HTTPError) as e:
            self.post('reset', {'email':'demo@example.com'}, origin='https://example.com')
        self.assertEqual(e.exception.code, 403)
    def test_reset_endpoint(self):
        with patch.object(fb, 'reset', return_value={'ok':True}) as reset:
            self.assertEqual(self.post('reset', {'email':'demo@example.com'})[0], {'ok':True})
            reset.assert_called_once_with({'email':'demo@example.com'})

if __name__ == '__main__':
    unittest.main()
