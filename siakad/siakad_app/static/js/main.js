let token = null;

function setStatus(msg, isError=false) {
  const el = document.getElementById('login-status');
  el.textContent = msg;
  el.style.color = isError ? '#b91c1c' : '#065f46';
}

async function api(path, options={}) {
  options.headers = options.headers || {};
  if (token) options.headers['Authorization'] = 'Bearer ' + token;
  options.headers['Content-Type'] = 'application/json';
  const res = await fetch(path, options);
  if (!res.ok) {
    const data = await res.json().catch(()=>({}));
    throw new Error(data.error || ('HTTP ' + res.status));
  }
  return res.json();
}

async function loadDashboard() {
  try {
    const stats = await api('/dashboard/stats');
    document.getElementById('stat-students').textContent = stats.students;
    document.getElementById('stat-teachers').textContent = stats.teachers;
    document.getElementById('stat-subjects').textContent = stats.subjects;

    const rows = await api('/dashboard/avg-by-subject');
    const labels = rows.map(r => r.code);
    const values = rows.map(r => r.average);

    const ctx = document.getElementById('avgChart').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Rata-rata',
          data: values,
          backgroundColor: '#3b82f6'
        }]
      },
      options: {
        scales: { y: { beginAtZero: true, max: 100 } }
      }
    });
  } catch (e) {
    setStatus('Gagal memuat dashboard: ' + e.message, true);
  }
}

function showDashboard() {
  document.getElementById('auth-section').classList.add('hidden');
  document.getElementById('dashboard-section').classList.remove('hidden');
}

window.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    setStatus('Login...');
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    try {
      const data = await api('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) });
      token = data.access_token;
      setStatus('Login sukses');
      showDashboard();
      await loadDashboard();
    } catch (e) {
      setStatus('Login gagal: ' + e.message, true);
    }
  });
});
