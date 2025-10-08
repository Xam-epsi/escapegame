// static/js/joueur1.js
document.addEventListener('DOMContentLoaded', () => {
  // -------------------------- éléments DOM --------------------------
  const puzzleSection = document.getElementById('puzzleSection');
  const puzzleGrid = document.getElementById('puzzleGrid');
  const validatePuzzleBtn = document.getElementById('validatePuzzleBtn');
  const puzzleStatus = document.getElementById('puzzleStatus');

  const dataSection = document.getElementById('dataSection');
  const timerEl = document.getElementById('timer');
  const progressBar = document.getElementById('progressBar');
  const csvContainer = document.getElementById('csvContainer');
  const csvStatus = document.getElementById('csvStatus');
  const validateTableBtn = document.getElementById('validateTableBtn');
  const pipelineInfo = document.getElementById('pipelineInfo');
  const pipelineCodeEl = document.getElementById('pipelineCode');
  const secretCodeEl = document.getElementById('secretCode');
  const finalResult = document.getElementById('finalResult');

  const alertPopup = document.getElementById('alertPopup');
  const alertMessage = document.getElementById('alertMessage');
  const closeAlert = document.getElementById('closeAlert');

  // sécurité si certains éléments n'existent pas dans la page
  if (!puzzleGrid || !validatePuzzleBtn) {
    console.warn('Éléments puzzle manquants dans le DOM.');
  }

  // -------------------------- configuration puzzle --------------------------
  const PIECES = 9;
  // taille d'affichage d'une pièce en px (tu peux ajuster si tu veux)
  const DISPLAY_PIECE_W = 213;
  const DISPLAY_PIECE_H = 171;

  // ordre courant (indices 0..8) — mélange Fisher-Yates pour meilleure randomisation
  let currentOrder = Array.from({ length: PIECES }, (_, i) => i);
  (function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  })(currentOrder);

  let firstClick = null;

  closeAlert && closeAlert.addEventListener('click', () => {
    alertPopup.style.display = 'none';
  });

  function showAlert(message) {
    alertMessage.textContent = message;
    alertPopup.style.display = 'flex';
  }

  // -------------------------- rendu puzzle (découpage propre) --------------------------
  function renderPuzzle() {
    puzzleGrid.innerHTML = '';
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = '/puzzle/image'; // route backend qui renvoie l'image complète

    img.onload = () => {
      // taille source
      const srcW = img.naturalWidth;
      const srcH = img.naturalHeight;
      const srcPieceW = Math.floor(srcW / 3);
      const srcPieceH = Math.floor(srcH / 3);

      // layout : 3 colonnes
      puzzleGrid.style.gridTemplateColumns = `repeat(3, ${DISPLAY_PIECE_W}px)`;

      currentOrder.forEach((pieceIdx, posIdx) => {
        const row = Math.floor(pieceIdx / 3);
        const col = pieceIdx % 3;

        const wrapper = document.createElement('div');
        wrapper.className = 'puzzle-cell';
        wrapper.style.width = `${DISPLAY_PIECE_W}px`;
        wrapper.style.height = `${DISPLAY_PIECE_H}px`;
        wrapper.style.overflow = 'hidden';
        wrapper.style.display = 'flex';
        wrapper.style.alignItems = 'center';
        wrapper.style.justifyContent = 'center';
        wrapper.style.cursor = 'pointer';
        wrapper.style.border = '1px solid #e2e8f0';
        wrapper.dataset.index = posIdx;

        // canvas : on dessine la portion correspondante et on l'affiche à la taille DISPLAY_W/H
        const canvas = document.createElement('canvas');
        // dessiner en résolution d'affichage (pour éviter flou sur écrans retina on pourrait multiplier par devicePixelRatio)
        const DPR = window.devicePixelRatio || 1;
        canvas.width = Math.floor(DISPLAY_PIECE_W * DPR);
        canvas.height = Math.floor(DISPLAY_PIECE_H * DPR);
        canvas.style.width = `${DISPLAY_PIECE_W}px`;
        canvas.style.height = `${DISPLAY_PIECE_H}px`;

        const ctx = canvas.getContext('2d');
        // calculer source rectangle (précis, avec arrondi)
        const sx = col * srcPieceW;
        const sy = row * srcPieceH;
        const sWidth = srcPieceW;
        const sHeight = srcPieceH;
        // dessiner en tenant compte du DPR
        ctx.drawImage(
          img,
          sx, sy, sWidth, sHeight,
          0, 0, canvas.width, canvas.height
        );

        wrapper.appendChild(canvas);
        wrapper.addEventListener('click', () => onPieceClick(posIdx));
        puzzleGrid.appendChild(wrapper);
      });
    };

    img.onerror = () => {
      showAlert('Impossible de charger l’image du puzzle (route /puzzle/image).');
    };
  }

  function onPieceClick(i) {
    if (firstClick === null) {
      firstClick = i;
      // signal visuel : encadrer la case sélectionnée
      const cell = puzzleGrid.querySelector(`div[data-index="${i}"]`);
      if (cell) cell.style.boxShadow = '0 0 0 3px rgba(59,130,246,0.45)';
    } else {
      // enlever bordure visuelle de la première
      const firstCell = puzzleGrid.querySelector(`div[data-index="${firstClick}"]`);
      if (firstCell) firstCell.style.boxShadow = '';

      [currentOrder[firstClick], currentOrder[i]] = [currentOrder[i], currentOrder[firstClick]];
      firstClick = null;
      renderPuzzle();
    }
  }

  // initial render
  renderPuzzle();

  // -------------------------- validation puzzle -> backend --------------------------
  validatePuzzleBtn.addEventListener('click', async () => {
    puzzleStatus.textContent = '';
    puzzleStatus.className = '';

    // envoi de l'ordre actuel (positions) au backend
    try {
      validatePuzzleBtn.disabled = true;
      const res = await fetch('/puzzle/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ positions: currentOrder }),
      });

      const data = await res.json().catch(() => ({ message: 'Réponse serveur invalide' }));

      if (!res.ok) {
        // backend fournit un objet detail avec message / penalty / remaining (conforme au main.py)
        const detail = data.detail || data;
        const msg = (detail && detail.message) ? detail.message : (detail || 'Erreur validation puzzle');
        // afficher popup d'alerte (avec info pénalité si présente)
        let extra = '';
        if (detail && detail.penalty) {
          extra = `\nTemps réduit de ${Math.round(detail.penalty / 60)} minute(s).`;
        }
        showAlert(msg + extra);
        // forcer refresh timer en demandant /timer (si présent)
        try { await fetch('/timer'); } catch (e) { /* ignore */ }
        return;
      }

      // OK
      puzzleStatus.textContent = data.message || 'Puzzle résolu !';
      puzzleStatus.className = 'text-green-600 font-semibold';
      // basculer vers la section données après un court délai
      setTimeout(() => {
        puzzleSection.classList.add('hidden');
        dataSection.classList.remove('hidden');
        startGame(); // lance le reste (timer, chargement CSV...)
      }, 900);
    } catch (err) {
      showAlert('Erreur réseau lors de la validation du puzzle : ' + (err.message || err));
    } finally {
      validatePuzzleBtn.disabled = false;
    }
  });

  // -------------------------- Fonctionnalités du jeu principal --------------------------
  function startGame() {
    // constantes et état
    const TOTAL_DURATION = 30 * 60; // 30 minutes en sec
    let timerInterval = null;

    // démarre le timer partagé (client interroge /timer backend)
    function startTimerLoop() {
      if (timerInterval) clearInterval(timerInterval);
      updateTimer(); // immediate
      timerInterval = setInterval(updateTimer, 1000);
    }
    function stopTimer() {
      if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
        finalResult.className = 'text-green-600 font-bold';
        finalResult.textContent = '⏹️ Le jeu est terminé — pipeline détecté !';
        disableInputs(true);
      }
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
        if (progressBar) {
          const progress = ((TOTAL_DURATION - timeLeft) / TOTAL_DURATION) * 100;
          progressBar.style.width = `${Math.max(0, Math.min(100, progress))}%`;
        }
        if (timeLeft <= 0) {
          clearInterval(timerInterval);
          finalResult.className = 'text-red-600 font-bold';
          finalResult.textContent = '💥 Temps écoulé ! Explosion virtuelle !';
          disableInputs(true);
        }
      } catch (e) {
        console.error('Erreur timer:', e);
      }
    }

    function disableInputs(state) {
      const inputs = csvContainer.querySelectorAll('input');
      inputs.forEach(i => i.disabled = state);
      validateTableBtn.disabled = state;
    }

    // --------------------------------- CSV ---------------------------------
    async function loadCSV() {
      csvStatus.textContent = 'Chargement des données...';
      csvContainer.innerHTML = '';
      try {
        const res = await fetch('/country/RU', { headers: { 'X-Auth-A': '1' } });
        if (!res.ok) throw new Error(res.statusText);
        const text = await res.text();
        renderTable(text);
        csvStatus.textContent = 'Données chargées.';
      } catch (e) {
        csvStatus.textContent = `Erreur : ${e.message || e}`;
        showAlert('Impossible de charger le CSV : ' + (e.message || e));
      }
    }

    function renderTable(csvText) {
      const lines = csvText.trim().split(/\r?\n/).filter(l => l.trim());
      if (lines.length < 2) {
        csvContainer.innerHTML = '<div class="text-gray-600 p-4">Aucune donnée.</div>';
        return;
      }

      const headers = lines[0].split(';').map(h => h.trim());
      const headerMap = {};
      headers.forEach((h, i) => headerMap[h.toLowerCase()] = i);

      // colonnes à ignorer pour l'affichage
      const skipPred = (h) => {
        const lh = h.toLowerCase();
        return lh.includes('notes') || lh.includes('confidence_score') || lh.includes('is_sabot') || lh.includes('anonym') || lh.includes('synthetic');
      };
      const displayHeaders = headers.filter(h => !skipPred(h));

      const table = document.createElement('table');
      table.className = 'csv-table w-full';
      table.style.borderCollapse = 'collapse';
      table.innerHTML = '';

      // thead
      const thead = document.createElement('thead');
      const trh = document.createElement('tr');
      displayHeaders.forEach(h => {
        const th = document.createElement('th');
        th.textContent = h;
        th.style.padding = '6px 8px';
        th.style.borderBottom = '1px solid #e5e7eb';
        th.style.textAlign = 'left';
        trh.appendChild(th);
      });
      const thScore = document.createElement('th');
      thScore.textContent = 'Confiance (%)';
      thScore.style.padding = '6px 8px';
      trh.appendChild(thScore);
      thead.appendChild(trh);
      table.appendChild(thead);

      // tbody
      const tbody = document.createElement('tbody');
      lines.slice(1).forEach(line => {
        const cols = line.split(';');
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid #f3f4f6';

        // récupérer site_code index pour dataset
        const siteCodeIdx = headerMap['site_code'] ?? headerMap['site'] ?? headerMap['sitecode'] ?? null;
        if (siteCodeIdx !== null) {
          tr.dataset.siteCode = (cols[siteCodeIdx] || '').trim();
        }

        displayHeaders.forEach(h => {
          const idx = headerMap[h.toLowerCase()];
          const td = document.createElement('td');
          td.textContent = (typeof idx === 'number') ? (cols[idx] || '') : '';
          td.style.padding = '6px 8px';
          tr.appendChild(td);
        });

        // colonne de saisie confiance
        const tdScore = document.createElement('td');
        tdScore.style.padding = '6px 8px';
        const inp = document.createElement('input');
        inp.type = 'number';
        inp.min = '0';
        inp.max = '100';
        inp.step = '1';
        inp.placeholder = '—';
        inp.required = true;
        inp.className = 'w-20 p-1 rounded border';
        tdScore.appendChild(inp);
        tr.appendChild(tdScore);

        tbody.appendChild(tr);
      });

      table.appendChild(tbody);
      csvContainer.innerHTML = '';
      csvContainer.appendChild(table);
    }

    function allScoresFilled() {
      const inputs = csvContainer.querySelectorAll('tbody input');
      if (!inputs.length) return false;
      return Array.from(inputs).every(i => i.value.trim() !== '');
    }

    // --------------------------------- validation du tableau ---------------------------------
    validateTableBtn.addEventListener('click', async () => {
      finalResult.textContent = '';
      finalResult.className = '';

      if (!allScoresFilled()) {
        finalResult.className = 'text-red-600 font-semibold';
        finalResult.textContent = '⚠️ Remplissez toutes les cases "Confiance (%)" avant de valider.';
        return;
      }

      const rows = Array.from(csvContainer.querySelectorAll('tbody tr'));
      const scores = rows.map(r => {
        const site = r.dataset.siteCode || (r.cells[0] && r.cells[0].textContent.trim()) || '';
        const input = r.querySelector('input');
        return { site_code: site, score: parseFloat(input.value) };
      });

      try {
        validateTableBtn.disabled = true;
        const res = await fetch('/validate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ scores })
        });

        const data = await res.json().catch(() => ({}));

        if (!res.ok) {
          // backend renvoie detail {message, penalty, remaining}
          const detail = data.detail || data;
          const message = (detail && detail.message) ? detail.message : (typeof detail === 'string' ? detail : 'Erreur validation');
          const penalty = detail && detail.penalty ? detail.penalty : 0;
          const remaining = detail && detail.remaining ? detail.remaining : null;
          // afficher message d'alerte sans révéler le pipeline
          let extra = '';
          if (penalty) extra = `\nTemps réduit de ${Math.round(penalty / 60)} minute(s).`;
          showAlert(message + extra);
          // forcer refresh timer
          await updateTimer();
          return;
        }

        // succès : afficher pipeline & code secret
        pipelineCodeEl.textContent = data.detected_site || '—';
        secretCodeEl.textContent = data.code_secret || '—';
        pipelineInfo.classList.remove('hidden');
        finalResult.className = 'text-green-600 font-semibold';
        finalResult.textContent = `✅ Tableau validé — pipeline détecté : ${data.detected_site || '—'}`;
        disableInputs(true);
        
      } catch (e) {
        showAlert('Erreur lors de la validation : ' + (e.message || e));
      } finally {
        validateTableBtn.disabled = false;
      }
    });

    // démarrer tout
    startTimerLoop();
    loadCSV();
  }

  // si on ouvre directement la page dataSection (par exemple pour debug) on peut démarrer le jeu
  // mais normalement on lance startGame après validation du puzzle
  // startGame();
});
