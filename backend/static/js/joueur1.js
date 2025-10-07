// joueur1.js — Agent A (compte à rebours, barre, beeps, alarm)
// Assure-toi que ce fichier est accessible sous /static/js/joueur1.js

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const timerEl = document.getElementById('timer');
  const progressBar = document.getElementById('progressBar');
  const loadFullBtn = document.getElementById('loadFull');
  const csvContainer = document.getElementById('csvContainer');
  const csvStatus = document.getElementById('csvStatus');
  const siteInput = document.getElementById('siteInput');
  const codeA = document.getElementById('codeA');
  const codeB = document.getElementById('codeB');
  const finalBtn = document.getElementById('finalBtn');
  const finalResult = document.getElementById('finalResult');

  // Configuration
  const TOTAL_SECONDS = 5 * 60; // 5 minutes
  let timeLeft = TOTAL_SECONDS;
  let timerInterval = null;
  let beepInterval = null;
  let alarmPlaying = false;
  let audioCtx = null;

  // Start countdown immediately when page loads
  startTimer();

  // Start beep schedule (every 30s)
  const BEEP_PERIOD = 30; // seconds
  scheduleBeeps();

  // Event listeners
  loadFullBtn.addEventListener('click', () => fetchCSV({ 'X-Auth-A': '1' }));
  finalBtn.addEventListener('click', onFinalClick);

  // Disable fields helper
  function setDisabledAll(state = true) {
    [loadFullBtn, siteInput, codeA, codeB, finalBtn].forEach(el => { if (el) el.disabled = state; });
    const inputs = csvContainer.querySelectorAll('input');
    inputs.forEach(i => i.disabled = state);
  }

  // Timer logic
  function startTimer() {
    updateTimerDisplay();
    timerInterval = setInterval(() => {
      timeLeft--;
      updateTimerDisplay();
      if (timeLeft <= 0) {
        clearInterval(timerInterval);
        onTimeExpired();
      }
    }, 1000);
  }

  function updateTimerDisplay() {
    const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
    const s = String(timeLeft % 60).padStart(2, '0');
    timerEl.textContent = `${m}:${s}`;
    // update progress bar (fills from 0 -> 100 as time elapses)
    const progress = ((TOTAL_SECONDS - timeLeft) / TOTAL_SECONDS) * 100;
    progressBar.style.width = `${progress}%`;
  }

  function onTimeExpired() {
    finalResult.className = 'error';
    finalResult.textContent = '💥 Temps écoulé ! Explosion virtuelle !';
    setDisabledAll(true);
    playAlarm();
  }

  // ---------------------
  // Audio: beep & alarm using WebAudio (no external files)
  // ---------------------
  function ensureAudioCtx() {
    if (!audioCtx) {
      try {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      } catch (e) {
        console.warn("Audio non supporté:", e);
      }
    }
    return audioCtx;
  }

  function blinkTimerOnce() {
    timerEl.classList.add('blink');
    setTimeout(() => timerEl.classList.remove('blink'), 900);
  }

  function playBeep() {
    const ctx = ensureAudioCtx();
    if (!ctx) return;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.frequency.value = 880; // A5
    o.type = 'sine';
    g.gain.value = 0.0001;
    o.connect(g);
    g.connect(ctx.destination);
    const now = ctx.currentTime;
    g.gain.cancelScheduledValues(now);
    g.gain.setValueAtTime(0.0001, now);
    g.gain.exponentialRampToValueAtTime(0.08, now + 0.01);
    o.start(now);
    g.gain.exponentialRampToValueAtTime(0.0001, now + 0.18);
    o.stop(now + 0.2);
    blinkTimerOnce();
  }

  function playAlarm() {
    if (alarmPlaying) return;
    const ctx = ensureAudioCtx();
    if (!ctx) return;
    alarmPlaying = true;
    // long intense tone sequence
    const duration = 3.5;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sawtooth';
    o.frequency.setValueAtTime(220, ctx.currentTime);
    g.gain.value = 0.0001;
    o.connect(g); g.connect(ctx.destination);
    const now = ctx.currentTime;
    g.gain.exponentialRampToValueAtTime(0.12, now + 0.02);
    o.start(now);
    // frequency sweep
    o.frequency.linearRampToValueAtTime(880, now + duration);
    g.gain.exponentialRampToValueAtTime(0.0001, now + duration + 0.02);
    o.stop(now + duration + 0.05);
    // visual alarm pulse
    timerEl.classList.add('alarmPulse');
    setTimeout(() => { timerEl.classList.remove('alarmPulse'); }, (duration + 0.1) * 1000);
  }

  function scheduleBeeps() {
    // Immediate beep at load is optional; we beep at every 30s interval aligned to remaining time
    // Compute time to next multiple of BEEP_PERIOD
    const mod = timeLeft % BEEP_PERIOD;
    const firstDelay = mod === 0 ? 0 : (mod);
    // We'll start an interval that checks every second; when timeLeft % 30 === 0 -> beep
    beepInterval = setInterval(() => {
      if (timeLeft > 0 && timeLeft % BEEP_PERIOD === 0) {
        playBeep();
      }
    }, 900);
  }

  // ---------------------
  // CSV loading and rendering (simple, clean)
  // ---------------------
  async function fetchCSV(authHeader) {
    csvStatus.textContent = 'Chargement des données...';
    csvContainer.innerHTML = '';
    try {
      const res = await fetch('/country/RU', { headers: authHeader });
      if (!res.ok) throw new Error(`Erreur ${res.status}`);
      const text = await res.text();
      renderSimpleTable(text);
      csvStatus.textContent = 'Données chargées (version complète).';
    } catch (err) {
      csvStatus.textContent = `Erreur : ${err.message}`;
    }
  }

  function renderSimpleTable(csvText) {
    // Parse CSV - simple splitting by comma (synthetic data)
    const lines = csvText.trim().split(/\r?\n/).filter(l => l.trim().length);
    if (lines.length === 0) {
      csvContainer.innerHTML = '<div class="muted">Aucune donnée.</div>';
      return;
    }
    const headers = splitCsvLine(lines[0]);
    // Ensure we show only a few important columns for clarity (id/site_code, operator, capacity, year)
    // fallback to showing all if those not present
    const wanted = ['site_code', 'id', 'operator', 'capacity', 'year', 'lat', 'lon'];
    const headerMap = headers.reduce((acc, h, i) => { acc[h.trim()] = i; return acc; }, {});
    const useHeaders = headers.filter(h => wanted.includes(h) ).length ? headers.filter(h => wanted.includes(h)) : headers;
    // Build table
    const table = document.createElement('table');
    table.className = 'csv-table';
    const thead = document.createElement('thead');
    const trh = document.createElement('tr');
    useHeaders.forEach(h => {
      const th = document.createElement('th'); th.textContent = h; trh.appendChild(th);
    });
    const thScore = document.createElement('th'); thScore.textContent = 'Confiance (%)'; trh.appendChild(thScore);
    thead.appendChild(trh); table.appendChild(thead);

    const tbody = document.createElement('tbody');
    lines.slice(1).forEach(line => {
      const cols = splitCsvLine(line);
      const tr = document.createElement('tr');
      useHeaders.forEach(h => {
        const td = document.createElement('td');
        const idx = headerMap[h];
        td.textContent = typeof idx === 'number' ? (cols[idx] || '') : '';
        tr.appendChild(td);
      });
      const tdScore = document.createElement('td');
      const inp = document.createElement('input');
      inp.type = 'number';
      inp.min = 0; inp.max = 100; inp.placeholder = '—';
      // small styling
      inp.style.width = '80px';
      tdScore.appendChild(inp);
      tr.appendChild(tdScore);
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    csvContainer.innerHTML = '';
    csvContainer.appendChild(table);
  }

  function splitCsvLine(line) {
    // naive split: first try comma, else semicolon
    if (line.includes(';')) return line.split(';').map(s => s.trim());
    return line.split(',').map(s => s.trim());
  }

  // ---------------------
  // Final submit (POST /final)
  // ---------------------
  async function onFinalClick(e) {
    e.preventDefault();
    finalResult.textContent = '';
    const site_code = (siteInput.value || '').trim();
    const a = (codeA.value || '').trim();
    const b = (codeB.value || '').trim();

    if (!site_code || !a || !b) {
      finalResult.className = 'error';
      finalResult.textContent = 'Veuillez renseigner le pipeline et les deux codes.';
      return;
    }

    // Send request
    try {
      const res = await fetch('/final', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_code, code_a: a, code_b: b })
      });
      const data = await res.json();
      if (!res.ok) {
        finalResult.className = 'error';
        finalResult.textContent = data.detail || JSON.stringify(data);
        return;
      }
      finalResult.className = data.result === 'success' ? 'success' : 'error';
      finalResult.textContent = data.message || JSON.stringify(data);
      if (data.result === 'success') {
        // success: stop timers, stop beeps
        clearInterval(timerInterval);
        clearInterval(beepInterval);
        setDisabledAll(true);
        playBeep(); // little success beep
      } else {
        // failure: small alarm pulse
        playBeep();
      }
    } catch (err) {
      finalResult.className = 'error';
      finalResult.textContent = 'Erreur réseau : ' + err.message;
    }
  }

  // Clean up on page hide/unload
  window.addEventListener('beforeunload', () => {
    clearInterval(timerInterval);
    clearInterval(beepInterval);
  });

});
