document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('predictForm');
  const predictError = document.getElementById('predictError');
  const predictResults = document.getElementById('predictResults');
  const finalSite = document.getElementById('finalSite');
  const finalA = document.getElementById('finalA');
  const finalB = document.getElementById('finalB');
  const submitFinalBtn = document.getElementById('submitFinalBtn');
  const finalResponse = document.getElementById('finalResponse');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    predictError.textContent = '';
    predictResults.textContent = 'Analyse en cours...';

    const payload = {
      lat: parseFloat(document.getElementById('lat').value),
      lon: parseFloat(document.getElementById('lon').value),
      capacity: parseFloat(document.getElementById('capacity').value),
      operator: document.getElementById('operator').value.trim(),
      year: parseInt(document.getElementById('year').value, 10),
      k: 3 // fixé par défaut
    };

    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || res.statusText);

      const preds = data.predictions || [];
      if (!preds.length) {
        predictResults.textContent = 'Aucune fuite détectée.';
        return;
      }

      const best = preds[0];
      finalSite.value = best.site_code || best.name || '—';
      predictResults.innerHTML = `<strong>Pipeline suspect :</strong> ${best.site_code || best.name}<br><em>Score : ${best.score || best.confidence}</em>`;
    } catch (err) {
      predictError.textContent = 'Erreur : ' + err.message;
    }
  });

  submitFinalBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    const site_code = finalSite.value.trim();
    const code_a = finalA.value.trim();
    const code_b = finalB.value.trim();
    if (!site_code || !code_a || !code_b) {
      finalResponse.className = 'error';
      finalResponse.textContent = 'Remplissez tous les champs.';
      return;
    }
    try {
      const res = await fetch('/final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_code, code_a, code_b })
      });
      const data = await res.json();
      finalResponse.className = data.result === 'success' ? 'success' : 'error';
      finalResponse.textContent = data.message;
    } catch (err) {
      finalResponse.className = 'error';
      finalResponse.textContent = 'Erreur : ' + err.message;
    }
  });
});
