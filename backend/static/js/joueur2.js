document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('predictForm');
  const resultsEl = document.getElementById('predictResults');
  const timerEl = document.getElementById('timer');
  const finalSite = document.getElementById('finalSite');
  const finalCode = document.getElementById('finalCode');
  const submitFinalBtn = document.getElementById('submitFinalBtn');
  const finalResponse = document.getElementById('finalResponse');

  const TOTAL_DURATION = 30 * 60;
  let timerInterval = setInterval(updateTimer, 1000);
  updateTimer();

  async function updateTimer() {
    try {
      const res = await fetch('/timer');
      const data = await res.json();
      const timeLeft = data.remaining;
      const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
      const s = String(timeLeft % 60).padStart(2, '0');
      timerEl.textContent = `${m}:${s}`;
      if (timeLeft <= 0) {
        clearInterval(timerInterval);
        resultsEl.textContent = '💥 Le temps est écoulé.';
      }
    } catch (e) {
      console.error('Erreur timer:', e);
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    resultsEl.textContent = 'Analyse en cours...';
    const payload = {
      lat: parseFloat(document.getElementById('lat').value),
      lon: parseFloat(document.getElementById('lon').value),
      capacity: parseFloat(document.getElementById('capacity').value),
      year: parseInt(document.getElementById('year').value, 10)
    };
    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || res.statusText);
      resultsEl.innerHTML = `<strong>Score de confiance :</strong> ${data.score}`;
    } catch (err) {
      resultsEl.textContent = 'Erreur : ' + err.message;
    }
  });

  submitFinalBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    finalResponse.textContent = '';
    const site = finalSite.value.trim();
    const code = finalCode.value.trim();
    if (!site || !code) {
      finalResponse.className = 'error';
      finalResponse.textContent = 'Remplissez site_code et code secret.';
      return;
    }
    try {
      const res = await fetch('/final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_code: site, code_a: code })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || res.statusText);
      finalResponse.className = data.result === 'success' ? 'success' : 'error';
      finalResponse.textContent = data.message;
    } catch (err) {
      finalResponse.className = 'error';
      finalResponse.textContent = 'Erreur : ' + err.message;
    }
  });
});
