/* Penghubung UI browser ke backend Python. Token Firebase hanya di server. */
(function (window) {
  'use strict';
  const NS = window.PK = window.PK || {};
  async function call(action, payload = {}) {
    let response;
    try {
      response = await fetch('/api/auth/' + action, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload), credentials: 'same-origin', cache: 'no-store'
      });
    } catch (_) { throw new Error('Server Python tidak terhubung. Jalankan python app.py di terminal VS Code.'); }
    let data;
    try { data = await response.json(); }
    catch (_) { throw new Error('Respons server tidak valid. Pastikan menjalankan app.py, bukan Live Server.'); }
    if (!response.ok) throw new Error(data.message || 'Permintaan gagal.');
    return data;
  }
  NS.authApi = {
    register: data => call('register', data),
    login: (email, password) => call('login', {email, password}),
    restore: () => call('restore'),
    requestReset: email => call('reset', {email}),
    resendVerification: () => call('resend-verification'),
    logout: () => call('logout')
  };
})(window);
