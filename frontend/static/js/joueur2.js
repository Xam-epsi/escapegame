// static/js/joueur2.js
document.addEventListener('DOMContentLoaded', () => {
  // -------------------------- éléments DOM --------------------------
  const timerEl = document.getElementById('timer');
  const predictForm = document.getElementById('predictForm');
  const predictResults = document.getElementById('predictResults');
  const finalBtn = document.getElementById('submitFinalBtn');
  const finalResp = document.getElementById('finalResponse');
  const siteInput = document.getElementById('finalSite');
  const codeInput = document.getElementById('finalCode');

  let timerInterval = null;

  // -------------------------- timer --------------------------
  function startTimer() {
    updateTimer(); // update immédiat
    timerInterval = setInterval(updateTimer, 1000);
  }

  function stopTimer() {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = null;
    predictForm.querySelectorAll('input, button').forEach(el => el.disabled = true);
    finalBtn.disabled = true;
    finalResp.className = 'text-red-400 font-bold';
    finalResp.textContent = '⏹️ Temps écoulé ! Vous ne pouvez plus soumettre.';
  }

  async function updateTimer() {
    try {
      const res = await fetch('/timer');
      if (!res.ok) return;
      const data = await res.json();
      const timeLeft = Number(data.remaining) || 0;
      const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
      const s = String(timeLeft % 60).padStart(2, '0');
      timerEl.textContent = `${m}:${s}`;
      if (timeLeft <= 0) stopTimer();
    } catch (err) {
      console.error('Erreur timer:', err);
    }
  }

  startTimer();

  // -------------------------- prédiction --------------------------
  predictForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    predictResults.textContent = '⏳ Calcul en cours...';
    predictResults.className = 'mt-4 p-3 text-center font-mono bg-gray-800/80 rounded-lg border border-gray-700 text-blue-300';

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

  // -------------------------- validation finale --------------------------
  finalBtn.addEventListener('click', async () => {
    finalResp.textContent = '';
    finalResp.className = '';

    const site = siteInput.value.trim();
    const code = codeInput.value.trim();

    if (!site || !code) {
      finalResp.textContent = 'Veuillez renseigner le pipeline et le code secret.';
      finalResp.className = 'text-yellow-400 font-semibold';
      return;
    }

    try {
      finalBtn.disabled = true;
      const res = await fetch('/final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_code: site, code_a: code })
      });

      const data = await res.json();

      if (data.result === 'success') {
        finalResp.textContent = data.message;
        finalResp.className = 'text-green-400 font-bold';
        // stopper timer après succès
        stopTimer();
      } else {
        finalResp.textContent = data.message;
        finalResp.className = 'text-red-400 font-bold';
      }
    } catch (err) {
      finalResp.textContent = 'Erreur de communication : ' + err.message;
      finalResp.className = 'text-red-400 font-bold';
    } finally {
      finalBtn.disabled = false;
    }
  });
});
