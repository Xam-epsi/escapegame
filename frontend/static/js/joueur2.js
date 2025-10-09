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

  let websocket = null;
  let lastAlertTime = 0;
  const TOTAL_DURATION = 30 * 60; // 30 minutes
  let reconnectAttempts = 0;
  const MAX_RECONNECT_ATTEMPTS = 5;

  closeAlert && closeAlert.addEventListener('click', () => {
    alertPopup.style.display = 'none';
  });

  function showAlert(message) {
    if (alertPopup && alertMessage) {
      alertMessage.textContent = message;
      alertPopup.style.display = 'flex';
    }
  }

  // -------------------------- timer synchronisé avec WebSocket --------------------------
  // Initialiser le temps de début du timer dès le chargement de la page
  if (!window.timerStartTime) {
    window.timerStartTime = Math.floor(Date.now() / 1000);
  }
  
  // Variable pour stocker le temps de victoire
  let victoryTime = null;

  function startTimer() {
    if (websocket) {
      websocket.close();
    }

    // Initialiser le temps de début du timer
    window.timerStartTime = Math.floor(Date.now() / 1000);

    // Déterminer l'URL WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/timer/ws`;
    
    console.log('🔌 Connexion WebSocket timer:', wsUrl);
    websocket = new WebSocket(wsUrl);

    websocket.onopen = function(event) {
      console.log('✅ WebSocket timer connecté');
      reconnectAttempts = 0;
    };

    websocket.onmessage = function(event) {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'timer_update') {
          const timeLeft = Number(data.remaining) || 0;
          const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
          const s = String(timeLeft % 60).padStart(2, '0');
          timerEl.textContent = `${m}:${s}`;

          const now = Date.now();
          if (now - lastAlertTime > 300_000 && timeLeft > 0) { // 5 minutes au lieu de 30 secondes
            lastAlertTime = now;
            showAlert('⏰ Rappel : le temps continue de s\'écouler !');
          }

          if (timeLeft <= 0) stopTimer();
          return;
        }

        if (data.type === 'game_success') {
          // Capturer le temps de victoire avant d'arrêter le timer
          victoryTime = Math.floor(Date.now() / 1000);
          stopTimer();
          showVictoryPopup();
          return;
        }

        if (data.game_completed) {
          // Capturer le temps de victoire avant d'arrêter le timer
          victoryTime = Math.floor(Date.now() / 1000);
          stopTimer();
          showVictoryPopup();
          return;
        }

      } catch (e) {
        console.error('Erreur parsing WebSocket timer data:', e);
      }
    };

    websocket.onerror = function(event) {
      console.error('❌ Erreur WebSocket timer:', event);
    };

    websocket.onclose = function(event) {
      console.log('🔌 WebSocket timer fermé:', event.code, event.reason);
      
      // Tentative de reconnexion automatique
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        console.log(`🔄 Tentative de reconnexion WebSocket ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}`);
        setTimeout(() => {
          startTimer();
        }, 2000 * reconnectAttempts); // Délai progressif
      } else {
        console.error('❌ Échec de reconnexion WebSocket, passage au mode fallback');
        startTimerFallback();
      }
    };
  }

  function stopTimer() {
    if (websocket) {
      websocket.close();
      websocket = null;
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
        if (now - lastAlertTime > 300_000 && timeLeft > 0) { // 5 minutes au lieu de 30 secondes
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
    if (!popup) return;

    popup.style.display = 'flex';
  }

  window.closeVictoryPopup = function() {
    const popup = document.getElementById('victoryPopup');
    if (popup) popup.style.display = 'none';
  }

  window.restartGame = function() {
    // Fermer la popup de victoire
    closeVictoryPopup();
    
    // Arrêter le timer avant la redirection
    stopTimer();
    
    // Rediriger vers la page de sélection des pays pour recommencer
    window.location.href = '/select_country';
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
        // Capturer le temps de victoire avant d'arrêter le timer
        victoryTime = Math.floor(Date.now() / 1000);
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
