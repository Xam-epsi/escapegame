// static/js/joueur2.js
document.addEventListener('DOMContentLoaded', () => {
  // -------------------------- éléments DOM --------------------------
  const timerEl = document.getElementById('timer');
  const predictForm = document.getElementById('predictForm');
  const predictResults = document.getElementById('predictResults');
  const predictResultsContent = predictResults.querySelector('.results-content');
  const finalBtn = document.getElementById('submitFinalBtn');
  const finalResp = document.getElementById('finalResponse');
  const siteInput = document.getElementById('finalSite');
  const codeInput = document.getElementById('finalCode');
  const alertPopup = document.getElementById('alertPopup');
  const alertMessage = document.getElementById('alertMessage');
  const closeAlert = document.getElementById('closeAlert');

  let eventSource = null;
  let lastAlertTime = 0;
  const TOTAL_DURATION = 30 * 60; // 30 minutes

  closeAlert && closeAlert.addEventListener('click', () => {
    alertPopup.style.display = 'none';
  });

  function showAlert(message) {
    if (alertPopup && alertMessage) {
      alertMessage.textContent = message;
      alertPopup.style.display = 'flex';
    }
  }

  // -------------------------- timer synchronisé --------------------------
  function startTimer() {
    if (eventSource) eventSource.close();
    eventSource = new EventSource('/timer/stream');

    eventSource.onmessage = function(event) {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'timer_update') {
          const timeLeft = Number(data.remaining) || 0;
          const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
          const s = String(timeLeft % 60).padStart(2, '0');
          timerEl.textContent = `${m}:${s}`;

          const now = Date.now();
          if (now - lastAlertTime > 30_000 && timeLeft > 0) {
            lastAlertTime = now;
            showAlert('⏰ Rappel : le temps continue de s’écouler !');
          }

          if (timeLeft <= 0) stopTimer();
          return;
        }

        if (data.type === 'game_success') {
          stopTimer();
          showVictoryPopup();
          return;
        }

        if (data.game_completed) {
          stopTimer();
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
          startTimerFallback();
        }
      }, 1000);
    };
  }

  function stopTimer() {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
    predictForm.querySelectorAll('input, button').forEach(el => el.disabled = true);
    finalBtn.disabled = true;
    finalResp.className = 'status-error';
    finalResp.textContent = '⏹️ Temps écoulé ! Vous ne pouvez plus soumettre.';
  }

  function startTimerFallback() {
    const fallbackInterval = setInterval(async () => {
      try {
        const res = await fetch('/timer');
        if (!res.ok) return;
        const data = await res.json();
        const timeLeft = Number(data.remaining) || 0;
        const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
        const s = String(timeLeft % 60).padStart(2, '0');
        timerEl.textContent = `${m}:${s}`;

        const now = Date.now();
        if (now - lastAlertTime > 30_000 && timeLeft > 0) {
          lastAlertTime = now;
          showAlert('⏰ Rappel : le temps continue de s’écouler !');
        }

        if (timeLeft <= 0) {
          clearInterval(fallbackInterval);
          stopTimer();
        }
      } catch (err) {
        console.error('Erreur timer fallback:', err);
      }
    }, 1000);
  }

  startTimer();

  async function forceTimerSync() {
    try {
      await fetch('/timer/sync', { method: 'POST' });
      startTimer();
    } catch (e) {
      console.error('Erreur synchronisation timer:', e);
    }
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
    if (securedPipelineEl) securedPipelineEl.textContent = siteInput.value || 'Pipeline sécurisé';
    popup.style.display = 'flex';
  }

  window.closeVictoryPopup = function() {
    const popup = document.getElementById('victoryPopup');
    if (popup) popup.style.display = 'none';
  }

  // -------------------------- prédiction --------------------------
  predictForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    predictResultsContent.textContent = '⏳ Calcul en cours...';
    predictResultsContent.className = 'results-content';

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
      predictResultsContent.textContent = `Score de confiance IA : ${pct}%`;
      predictResultsContent.className = 'results-content status-success';
    } catch (err) {
      predictResultsContent.textContent = 'Erreur : ' + err.message;
      predictResultsContent.className = 'results-content status-error';
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
        finalResp.className = 'status-success';
        showVictoryPopup();
        stopTimer();
      } else {
        finalResp.textContent = data.message;
        finalResp.className = 'status-error';
      }
    } catch (err) {
      finalResp.textContent = 'Erreur de communication : ' + err.message;
      finalResp.className = 'status-error';
    } finally {
      finalBtn.disabled = false;
    }
  });
});
