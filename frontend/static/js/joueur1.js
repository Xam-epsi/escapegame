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

  if (!puzzleGrid || !validatePuzzleBtn) {
    console.warn('Éléments puzzle manquants dans le DOM.');
  }

  // -------------------------- configuration puzzle --------------------------
  const PIECES = 9;
  const DISPLAY_PIECE_W = 213;
  const DISPLAY_PIECE_H = 171;

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

  // -------------------------- rendu puzzle --------------------------
  function renderPuzzle() {
    puzzleGrid.innerHTML = '';
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = '/puzzle/image';

    img.onload = () => {
      const srcW = img.naturalWidth;
      const srcH = img.naturalHeight;
      const srcPieceW = Math.floor(srcW / 3);
      const srcPieceH = Math.floor(srcH / 3);

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

        const canvas = document.createElement('canvas');
        const DPR = window.devicePixelRatio || 1;
        canvas.width = Math.floor(DISPLAY_PIECE_W * DPR);
        canvas.height = Math.floor(DISPLAY_PIECE_H * DPR);
        canvas.style.width = `${DISPLAY_PIECE_W}px`;
        canvas.style.height = `${DISPLAY_PIECE_H}px`;

        const ctx = canvas.getContext('2d');
        const sx = col * srcPieceW;
        const sy = row * srcPieceH;
        const sWidth = srcPieceW;
        const sHeight = srcPieceH;
        ctx.drawImage(img, sx, sy, sWidth, sHeight, 0, 0, canvas.width, canvas.height);

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
      const cell = puzzleGrid.querySelector(`div[data-index="${i}"]`);
      if (cell) cell.style.boxShadow = '0 0 0 3px rgba(59,130,246,0.45)';
    } else {
      const firstCell = puzzleGrid.querySelector(`div[data-index="${firstClick}"]`);
      if (firstCell) firstCell.style.boxShadow = '';

      [currentOrder[firstClick], currentOrder[i]] = [currentOrder[i], currentOrder[firstClick]];
      firstClick = null;
      renderPuzzle();
    }
  }

  renderPuzzle();

  // -------------------------- Timer global synchronisé --------------------------
  let eventSource = null;
  const TOTAL_DURATION = 30 * 60; // 30 minutes
  let lastAlertTime = 0;

  function startGlobalTimer() {
    if (eventSource) eventSource.close();
    eventSource = new EventSource('/timer/stream');

    eventSource.onmessage = function(event) {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'timer_update') {
          const timeLeft = Number(data.remaining) || 0;
          const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
          const s = String(timeLeft % 60).padStart(2, '0');

          if (timerEl) timerEl.textContent = `${m}:${s}`;
          if (progressBar) {
            const progress = ((TOTAL_DURATION - timeLeft) / TOTAL_DURATION) * 100;
            progressBar.style.width = `${Math.max(0, Math.min(100, progress))}%`;
          }

          const now = Date.now();
          if (now - lastAlertTime > 30_000 && timeLeft > 0) {
            lastAlertTime = now;
            showAlert('⏰ Rappel : le temps continue de s’écouler !');
          }

          if (timeLeft <= 0) {
            stopGlobalTimer();
            if (finalResult) {
              finalResult.className = 'status-error';
              finalResult.textContent = '💥 Temps écoulé ! Explosion virtuelle !';
            }
            showAlert('💥 Temps écoulé ! Explosion virtuelle !');
          }
          return;
        }

        if (data.type === 'game_success') {
          stopGlobalTimer();
          showVictoryPopup();
          return;
        }

        if (data.game_completed) {
          stopGlobalTimer();
          showVictoryPopup();
          return;
        }

      } catch (e) {
        console.error('Erreur parsing timer data:', e);
      }
    };

    eventSource.onerror = function(event) {
      console.error('Erreur EventSource timer:', event);
      setTimeout(() => {
        if (eventSource && eventSource.readyState === EventSource.CLOSED) {
          startGlobalTimerFallback();
        }
      }, 1000);
    };
  }

  function stopGlobalTimer() {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
  }

  function startGlobalTimerFallback() {
    const fallbackInterval = setInterval(async () => {
      try {
        const res = await fetch('/timer');
        if (!res.ok) return;
        const data = await res.json();
        const timeLeft = Number(data.remaining) || 0;
        const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
        const s = String(timeLeft % 60).padStart(2, '0');

        if (timerEl) timerEl.textContent = `${m}:${s}`;
        if (progressBar) {
          const progress = ((TOTAL_DURATION - timeLeft) / TOTAL_DURATION) * 100;
          progressBar.style.width = `${Math.max(0, Math.min(100, progress))}%`;
        }

        const now = Date.now();
        if (now - lastAlertTime > 30_000 && timeLeft > 0) {
          lastAlertTime = now;
          showAlert('⏰ Rappel : le temps continue de s’écouler !');
        }

        if (timeLeft <= 0) {
          clearInterval(fallbackInterval);
          if (finalResult) {
            finalResult.className = 'status-error';
            finalResult.textContent = '💥 Temps écoulé ! Explosion virtuelle !';
          }
          showAlert('💥 Temps écoulé ! Explosion virtuelle !');
        }
      } catch (e) {
        console.error('Erreur timer fallback:', e);
      }
    }, 1000);
  }

  startGlobalTimer();

  // -------------------------- validation puzzle --------------------------
  validatePuzzleBtn.addEventListener('click', async () => {
    puzzleStatus.textContent = '';
    puzzleStatus.className = '';

    try {
      validatePuzzleBtn.disabled = true;
      const res = await fetch('/puzzle/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ positions: currentOrder }),
      });

      const data = await res.json().catch(() => ({ message: 'Réponse serveur invalide' }));

      if (!res.ok) {
        const detail = data.detail || data;
        let extra = '';
        if (detail && detail.penalty) extra = `\nTemps réduit de ${Math.round(detail.penalty / 60)} minute(s).`;
        showAlert((detail.message || detail.message || 'Erreur validation puzzle') + extra);

        try { 
          await fetch('/timer/sync', { method: 'POST' }); 
          startGlobalTimer();
        } catch (e) { }

        return;
      }

      puzzleStatus.textContent = data.message || 'Puzzle résolu !';
      puzzleStatus.className = 'status-success';

      setTimeout(() => {
        puzzleSection.style.display = 'none';
        dataSection.style.display = 'block';
        startGame();
      }, 900);

    } catch (err) {
      showAlert('Erreur réseau lors de la validation du puzzle : ' + (err.message || err));
    } finally {
      validatePuzzleBtn.disabled = false;
    }
  });

  // -------------------------- Fonctionnalités du jeu principal --------------------------
  function startGame() {
    function stopGame() {
      stopGlobalTimer();
      if (finalResult) {
        finalResult.className = 'status-success';
        finalResult.textContent = '⏹️ Le jeu est terminé — pipeline détecté !';
      }
      disableInputs(true);
    }

    function disableInputs(state) {
      const inputs = csvContainer.querySelectorAll('input');
      inputs.forEach(i => i.disabled = state);
      validateTableBtn.disabled = state;
    }

    async function loadCSV() {
      if (csvStatus) csvStatus.textContent = 'Chargement des données...';
      if (csvContainer) csvContainer.innerHTML = '';
      try {
        const res = await fetch('/country/RU', { headers: { 'X-Auth-A': '1' } });
        if (!res.ok) throw new Error(res.statusText);
        const text = await res.text();
        renderTable(text);
        if (csvStatus) csvStatus.textContent = 'Données chargées.';
      } catch (e) {
        if (csvStatus) csvStatus.textContent = `Erreur : ${e.message || e}`;
        showAlert('Impossible de charger le CSV : ' + (e.message || e));
      }
    }

    function renderTable(csvText) {
      const lines = csvText.trim().split(/\r?\n/).filter(l => l.trim());
      if (lines.length < 2) {
        if (csvContainer) csvContainer.innerHTML = '<div style="color: var(--muted); padding: 20px; text-align: center;">Aucune donnée.</div>';
        return;
      }

      const headers = lines[0].split(';').map(h => h.trim());
      const headerMap = {};
      headers.forEach((h, i) => headerMap[h.toLowerCase()] = i);

      const skipPred = (h) => {
        const lh = h.toLowerCase();
        return lh.includes('notes') || lh.includes('confidence_score') || lh.includes('is_sabot') || lh.includes('anonym') || lh.includes('synthetic');
      };
      const displayHeaders = headers.filter(h => !skipPred(h));

      const table = document.createElement('table');
      table.className = 'csv-table w-full';
      table.style.borderCollapse = 'collapse';
      table.innerHTML = '';

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

      const tbody = document.createElement('tbody');
      lines.slice(1).forEach(line => {
        const cols = line.split(';');
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid #f3f4f6';

        const siteCodeIdx = headerMap['site_code'] ?? headerMap['site'] ?? headerMap['sitecode'] ?? null;
        if (siteCodeIdx !== null) tr.dataset.siteCode = (cols[siteCodeIdx] || '').trim();

        displayHeaders.forEach(h => {
          const idx = headerMap[h.toLowerCase()];
          const td = document.createElement('td');
          td.textContent = (typeof idx === 'number') ? (cols[idx] || '') : '';
          td.style.padding = '6px 8px';
          tr.appendChild(td);
        });

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
      if (csvContainer) {
        csvContainer.innerHTML = '';
        csvContainer.appendChild(table);
      }
    }

    function allScoresFilled() {
      if (!csvContainer) return false;
      const inputs = csvContainer.querySelectorAll('tbody input');
      if (!inputs.length) return false;
      return Array.from(inputs).every(i => i.value.trim() !== '');
    }

    if (validateTableBtn) {
      validateTableBtn.addEventListener('click', async () => {
        if (finalResult) {
          finalResult.textContent = '';
          finalResult.className = '';
        }

        if (!allScoresFilled()) {
          if (finalResult) {
            finalResult.className = 'status-error';
            finalResult.textContent = '⚠️ Remplissez toutes les cases "Confiance (%)" avant de valider.';
          }
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
            const detail = data.detail || data;
            const message = (detail && detail.message) ? detail.message : (typeof detail === 'string' ? detail : 'Erreur validation');
            const penalty = detail && detail.penalty ? detail.penalty : 0;
            let extra = '';
            if (penalty) extra = `\nTemps réduit de ${Math.round(penalty / 60)} minute(s).`;
            showAlert(message + extra);
            try { 
              await fetch('/timer/sync', { method: 'POST' }); 
              startGlobalTimer();
            } catch (e) {}
            return;
          }

          if (pipelineCodeEl) pipelineCodeEl.textContent = data.detected_site || '—';
          if (secretCodeEl) secretCodeEl.textContent = data.code_secret || '—';
          if (pipelineInfo) pipelineInfo.style.display = 'block';
          if (finalResult) {
            finalResult.className = 'status-success';
            finalResult.textContent = `✅ Tableau validé — pipeline détecté : ${data.detected_site || '—'}`;
          }
          disableInputs(true);
        } catch (e) {
          showAlert('Erreur lors de la validation : ' + (e.message || e));
        } finally {
          validateTableBtn.disabled = false;
        }
      });
    }

    loadCSV();
  }

  // -------------------------- popup victoire --------------------------
  function showVictoryPopup() {
    const popup = document.getElementById('victoryPopup');
    const totalTimeEl = document.getElementById('totalTime');
    const securedPipelineEl = document.getElementById('securedPipeline');
    if (!popup) return;

    const startTime = new Date().getTime() - (30 * 60 * 1000);
    const totalSeconds = Math.floor((new Date().getTime() - startTime) / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

    if (totalTimeEl) totalTimeEl.textContent = timeString;
    if (securedPipelineEl) securedPipelineEl.textContent = 'Pipeline sécurisé';

    popup.style.display = 'flex';
  }

  window.closeVictoryPopup = function() {
    const popup = document.getElementById('victoryPopup');
    if (popup) popup.style.display = 'none';
  }
});
