document.addEventListener('DOMContentLoaded', () => {
  const timerEl = document.getElementById('timer');
  const predictForm = document.getElementById('predictForm');
  const predictResults = document.getElementById('predictResults');
  const finalBtn = document.getElementById('submitFinalBtn');
  const finalResp = document.getElementById('finalResponse');
  const siteInput = document.getElementById('finalSite');
  const codeInput = document.getElementById('finalCode');

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
        alert('💥 Temps écoulé ! Explosion virtuelle !');
      }
    } catch (err) {
      console.error('Erreur timer:', err);
    }
  }

  predictForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    predictResults.textContent = '⏳ Calcul en cours...';
    const lat = parseFloat(document.getElementById('lat').value);
    const lon = parseFloat(document.getElementById('lon').value);
    const capacity = parseFloat(document.getElementById('capacity').value);
    const year = parseInt(document.getElementById('year').value);

    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat, lon, capacity, year })
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      const pct = Math.round(data.score * 100);
      predictResults.textContent = `Score de confiance IA : ${pct}%`;
      predictResults.className = 'mt-4 p-3 text-center font-mono bg-gray-800/80 rounded-lg border border-gray-700 text-green-400';
    } catch (err) {
      predictResults.textContent = 'Erreur : ' + err.message;
      predictResults.className = 'mt-4 p-3 text-center font-mono bg-gray-800/80 rounded-lg border border-gray-700 text-red-400';
    }
  });

  finalBtn.addEventListener('click', async () => {
    finalResp.textContent = '';
    const site = siteInput.value.trim();
    const code = codeInput.value.trim();

    if (!site || !code) {
      finalResp.textContent = 'Veuillez renseigner le pipeline et le code secret.';
      finalResp.className = 'text-yellow-400 font-semibold';
      return;
    }

    try {
      const res = await fetch('/final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_code: site, code_a: code })
      });
      const data = await res.json();
      if (data.result === 'success') {
        finalResp.textContent = data.message;
        finalResp.className = 'text-green-400 font-bold';
      } else {
        finalResp.textContent = data.message;
        finalResp.className = 'text-red-400 font-bold';
      }
    } catch (err) {
      finalResp.textContent = 'Erreur de communication : ' + err.message;
      finalResp.className = 'text-red-400 font-bold';
    }
  });
});
