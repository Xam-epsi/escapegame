// login.js — version escape game
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  const input = document.getElementById('code');
  const err = document.getElementById('loginError');

  form.addEventListener('submit', (ev) => {
    ev.preventDefault();
    err.textContent = '';
    const code = input.value.trim().toLowerCase();

    if (!code) {
      err.textContent = 'Entrez un code.';
      return;
    }

    if (code === 'keep') {
      window.location.href = '/joueur1';
      return;
    }
    if (code === 'calm') {
      window.location.href = '/joueur2';
      return;
    }

    err.textContent = 'Accès refusé. Le code semble incorrect.';
  });
});
