document.addEventListener('DOMContentLoaded', () => {
  const timerEl = document.getElementById('timer');
  const progressBar = document.getElementById('progressBar');
  const csvContainer = document.getElementById('csvContainer');
  const csvStatus = document.getElementById('csvStatus');
  const validateBtn = document.getElementById('validateTableBtn');
  const pipelineInfo = document.getElementById('pipelineInfo');
  const pipelineCodeEl = document.getElementById('pipelineCode');
  const secretCodeEl = document.getElementById('secretCode');
  const finalResult = document.getElementById('finalResult');

  const TOTAL_DURATION = 30 * 60; // 30 minutes

  // démarrer timer partagé
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
      if (progressBar) progressBar.style.width = `${((TOTAL_DURATION - timeLeft) / TOTAL_DURATION) * 100}%`;
      if (timeLeft <= 0) {
        clearInterval(timerInterval);
        finalResult.className = 'error';
        finalResult.textContent = '💥 Temps écoulé ! Explosion virtuelle !';
        disableInputs(true);
      }
    } catch (e) {
      console.error('Erreur timer:', e);
    }
  }

  function disableInputs(state) {
    csvContainer.querySelectorAll('input').forEach(i => i.disabled = state);
    validateBtn.disabled = state;
  }

  // CHARGER LE CSV
  async function loadCSV() {
    csvStatus.textContent = 'Chargement des données...';
    try {
      const res = await fetch('/country/RU', { headers: { 'X-Auth-A': '1' } });
      if (!res.ok) throw new Error(res.statusText);
      const text = await res.text();
      renderTable(text);
      csvStatus.textContent = 'Données chargées.';
    } catch (e) {
      csvStatus.textContent = `Erreur : ${e.message}`;
    }
  }

  function renderTable(csvText) {
    const lines = csvText.trim().split(/\r?\n/).filter(l => l.trim());
    if (lines.length < 2) {
      csvContainer.innerHTML = '<div class="muted">Aucune donnée.</div>';
      return;
    }
    const headers = lines[0].split(';').map(h => h.trim());
    const headerMap = {};
    headers.forEach((h, i) => headerMap[h.toLowerCase()] = i);

    const skipPred = h => {
      const lh = h.toLowerCase();
      return lh.includes('notes') || lh.includes('confidence_score') || lh.includes('is_sabot') || lh.includes('anonym');
    };
    const displayHeaders = headers.filter(h => !skipPred(h));

    const table = document.createElement('table');
    table.className = 'csv-table';
    const thead = document.createElement('thead');
    const trh = document.createElement('tr');
    displayHeaders.forEach(h => {
      const th = document.createElement('th'); th.textContent = h; trh.appendChild(th);
    });
    const thScore = document.createElement('th'); thScore.textContent = 'Confiance (%)'; trh.appendChild(thScore);
    thead.appendChild(trh); table.appendChild(thead);

    const tbody = document.createElement('tbody');
    lines.slice(1).forEach(line => {
      const cols = line.split(';');
      const tr = document.createElement('tr');
      const siteCodeIdx = headerMap['site_code'] ?? headerMap['site'] ?? headerMap['sitecode'] ?? null;
      if (siteCodeIdx !== null) tr.dataset.siteCode = (cols[siteCodeIdx] || '').trim();

      displayHeaders.forEach(h => {
        const idx = headerMap[h.toLowerCase()];
        const td = document.createElement('td');
        td.textContent = typeof idx === 'number' ? (cols[idx] || '') : '';
        tr.appendChild(td);
      });
      const tdScore = document.createElement('td');
      const inp = document.createElement('input');
      inp.type = 'number'; inp.min = 0; inp.max = 100; inp.placeholder = '—';
      tdScore.appendChild(inp); tr.appendChild(tdScore);
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    csvContainer.innerHTML = '';
    csvContainer.appendChild(table);
  }

  function allScoresFilled() {
    const inputs = csvContainer.querySelectorAll('tbody input');
    return Array.from(inputs).every(i => i.value.trim() !== '');
  }

  // Validation du tableau — maintenant gère l'erreur + pénalité
  validateBtn.addEventListener('click', async () => {
    finalResult.textContent = '';
    if (!allScoresFilled()) {
      finalResult.className = 'error';
      finalResult.textContent = 'Remplissez toutes les cases "Confiance (%)" avant de valider.';
      return;
    }

    const rows = Array.from(csvContainer.querySelectorAll('tbody tr'));
    const scores = rows.map(r => {
      const site = r.dataset.siteCode || r.cells[0].textContent.trim();
      const input = r.querySelector('input');
      return { site_code: site, score: parseFloat(input.value) };
    });

    try {
      const res = await fetch('/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scores })
      });
      const data = await res.json();

      if (!res.ok) {
        // data.detail contient soit une chaîne soit un objet {message, penalty, remaining}
        const detail = data.detail ?? data;
        if (typeof detail === 'object' && detail !== null) {
          const message = detail.message || JSON.stringify(detail);
          const penalty = detail.penalty ?? 0;
          const remaining = detail.remaining ?? null;
          finalResult.className = 'error';
          finalResult.textContent = message + (penalty ? `\nTemps réduit de ${Math.round(penalty/60)} minute(s).` : '');
          // forcer un rafraîchissement immédiat du timer
          updateTimer();
        } else {
          finalResult.className = 'error';
          finalResult.textContent = String(detail);
        }
        return;
      }

      // succès : afficher pipeline et code
      pipelineCodeEl.textContent = data.detected_site;
      secretCodeEl.textContent = data.code_secret;
      pipelineInfo.style.display = 'block';
      finalResult.className = 'success';
      finalResult.textContent = `Tableau validé — pipeline détecté : ${data.detected_site}`;
      disableInputs(true);
    } catch (e) {
      finalResult.className = 'error';
      finalResult.textContent = 'Erreur validation : ' + e.message;
      console.error(e);
    }
  });

  // initial load
  loadCSV();
});
