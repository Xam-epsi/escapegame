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
  let localTimerInterval = null;
  let fallbackMode = false;

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

  async function startTimer() {
    if (websocket) {
      websocket.close();
    }

    // Initialiser le temps de début du timer
    window.timerStartTime = Math.floor(Date.now() / 1000);

    // Démarrer le timer côté serveur
    try {
      console.log('🚀 Démarrage du timer côté serveur');
      const startRes = await fetch('/timer/start', { method: 'POST' });
      if (startRes.ok) {
        const startData = await startRes.json();
        console.log('✅ Timer démarré côté serveur:', startData);
      }
    } catch (err) {
      console.error('❌ Erreur démarrage timer serveur:', err);
    }

    // Déterminer l'URL WebSocket - Azure nécessite wss:// pour HTTPS
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

        if (data.type === 'game_defeat') {
          // Arrêter le timer en cas de défaite
          console.log('💥 Défaite reçue via WebSocket:', data);
          stopTimer();
          showDefeatPopup();
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
      console.error('   Détails de l\'erreur:', {
        type: event.type,
        target: event.target,
        readyState: event.target?.readyState,
        url: event.target?.url
      });
      
      // Sur Azure, si wss:// échoue, essayer ws:// en fallback
      if (window.location.protocol === 'https:' && reconnectAttempts === 0) {
        console.log('🔄 Tentative fallback ws:// pour Azure');
        setTimeout(() => {
          const fallbackUrl = `ws://${window.location.host}/timer/ws`;
          console.log('🔌 Connexion WebSocket fallback:', fallbackUrl);
          websocket = new WebSocket(fallbackUrl);
          setupWebSocketHandlers();
        }, 1000);
        return;
      }
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
    
    // Fonction pour configurer les handlers WebSocket
    function setupWebSocketHandlers() {
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

          if (data.type === 'game_defeat') {
            // Arrêter le timer en cas de défaite
            console.log('💥 Défaite reçue via WebSocket (setup):', data);
            stopTimer();
            showDefeatPopup();
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
    
    setupWebSocketHandlers();
  }

  function stopTimer() {
    if (websocket) {
      websocket.close();
      websocket = null;
    }
    if (localTimerInterval) {
      clearInterval(localTimerInterval);
      localTimerInterval = null;
    }
    fallbackMode = false;
    predictForm.querySelectorAll('input, button').forEach(el => el.disabled = true);
    finalBtn.disabled = true;
    finalResp.className = 'status-error';
    finalResp.textContent = '⏹️ Temps écoulé ! Vous ne pouvez plus soumettre.';
  }

  async function startTimerFallback() {
    console.log('🔄 Démarrage du mode fallback HTTP');
    fallbackMode = true;
    
    // Démarrer le timer côté serveur
    try {
      console.log('🚀 Démarrage du timer côté serveur (fallback)');
      const startRes = await fetch('/timer/start', { method: 'POST' });
      if (startRes.ok) {
        const startData = await startRes.json();
        console.log('✅ Timer démarré côté serveur (fallback):', startData);
      }
    } catch (err) {
      console.error('❌ Erreur démarrage timer serveur (fallback):', err);
    }
    
    const fallbackInterval = setInterval(async () => {
      try {
        // Essayer d'abord avec le protocole actuel
        let res;
        try {
          res = await fetch('/timer');
        } catch (sslError) {
          // Si erreur SSL sur Azure, essayer avec HTTP au lieu de HTTPS
          if (window.location.protocol === 'https:') {
            console.log('🔄 Tentative fallback HTTP pour Azure');
            const httpUrl = window.location.href.replace('https://', 'http://');
            const timerUrl = httpUrl + '/timer';
            res = await fetch(timerUrl);
          } else {
            throw sslError;
          }
        }
        
        if (!res.ok) return;
        const data = await res.json();
        const timeLeft = Number(data.remaining) || 0;
        const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
        const s = String(timeLeft % 60).padStart(2, '0');
        timerEl.textContent = `${m}:${s}`;

        const now = Date.now();
        if (now - lastAlertTime > 300_000 && timeLeft > 0) { // 5 minutes au lieu de 30 secondes
          lastAlertTime = now;
          showAlert('⏰ Rappel : le temps continue de s\'écouler !');
        }

        if (timeLeft <= 0) {
          clearInterval(fallbackInterval);
          stopTimer();
        }
      } catch (err) {
        console.error('Erreur timer fallback:', err);
        // Si le fallback échoue aussi, passer au mode local
        if (err.message.includes('ERR_CERT_AUTHORITY_INVALID') || err.message.includes('Failed to fetch')) {
          console.log('🔄 Passage au mode timer local');
          clearInterval(fallbackInterval);
          startLocalTimer();
        }
      }
    }, 1000);
  }

  async function startLocalTimer() {
    console.log('🔄 Démarrage du timer local (mode offline)');
    fallbackMode = true;
    
    // Démarrer le timer côté serveur avant de passer en mode local
    try {
      console.log('🚀 Démarrage du timer côté serveur (local)');
      const startRes = await fetch('/timer/start', { method: 'POST' });
      if (startRes.ok) {
        const startData = await startRes.json();
        console.log('✅ Timer démarré côté serveur (local):', startData);
      }
    } catch (err) {
      console.error('❌ Erreur démarrage timer serveur (local):', err);
    }
    
    // Utiliser le temps de début stocké ou le temps actuel
    if (!window.timerStartTime) {
      window.timerStartTime = Math.floor(Date.now() / 1000);
    }
    
    localTimerInterval = setInterval(() => {
      const now = Math.floor(Date.now() / 1000);
      const elapsed = now - window.timerStartTime;
      const timeLeft = Math.max(TOTAL_DURATION - elapsed, 0);
      
      const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
      const s = String(timeLeft % 60).padStart(2, '0');
      timerEl.textContent = `${m}:${s}`;

      const nowMs = Date.now();
      if (nowMs - lastAlertTime > 300_000 && timeLeft > 0) { // 5 minutes au lieu de 30 secondes
        lastAlertTime = nowMs;
        showAlert('⏰ Rappel : le temps continue de s\'écouler !');
      }

      if (timeLeft <= 0) {
        clearInterval(localTimerInterval);
        stopTimer();
      }
    }, 1000);
  }

  startTimer();

  // Test temporaire pour la popup de défaite
  window.testDefeatPopup = function() {
    console.log('🧪 Test popup de défaite');
    showDefeatPopup();
  };
  
  // Fonction de debug pour vérifier l'état du jeu
  window.debugGameState = async function() {
    console.log('🔍 Vérification de l\'état du jeu...');
    try {
      const res = await fetch('/debug/state');
      if (res.ok) {
        const data = await res.json();
        console.log('📊 État du jeu:', data);
        alert(`État du jeu:\nCURRENT_SECRETS: ${JSON.stringify(data.CURRENT_SECRETS)}\nMAPPING: ${JSON.stringify(data.MAPPING)}`);
      } else {
        console.error('❌ Erreur debug state:', res.status);
      }
    } catch (e) {
      console.error('❌ Exception debug state:', e);
    }
  };

  async function forceTimerSync() {
    try {
      // D'abord démarrer le timer si nécessaire
      await fetch('/timer/start', { method: 'POST' });
      // Puis synchroniser
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

  // -------------------------- popup défaite --------------------------
  function showDefeatPopup() {
    console.log('🎭 Affichage popup de défaite');
    const popup = document.getElementById('defeatPopup');
    if (!popup) {
      console.error('❌ Popup de défaite non trouvée dans le DOM');
      return;
    }

    popup.style.display = 'flex';
    console.log('✅ Popup de défaite affichée');
  }

  window.closeDefeatPopup = function() {
    const popup = document.getElementById('defeatPopup');
    if (popup) popup.style.display = 'none';
  }

  window.restartGame = function() {
    // Fermer les popups
    closeVictoryPopup();
    closeDefeatPopup();
    
    // Arrêter le timer avant la redirection
    stopTimer();
    
    // Réinitialiser le jeu côté serveur
    fetch('/game/reset', { method: 'POST' })
      .then(() => {
        console.log('🔄 Jeu réinitialisé côté serveur');
        // Rediriger vers la page de sélection des pays pour recommencer
        window.location.href = '/select_country';
      })
      .catch(err => {
        console.error('❌ Erreur réinitialisation jeu:', err);
        // Rediriger quand même
        window.location.href = '/select_country';
      });
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
      
      console.log('🔍 Statut de la réponse:', res.status);
      
      const data = await res.json();
      console.log('🔍 Réponse finale:', data);
      
      if (!res.ok) {
        console.error('❌ Erreur HTTP:', res.status, data);
        finalResp.textContent = `Erreur ${res.status}: ${data.detail || data.message || 'Erreur inconnue'}`;
        finalResp.className = 'status-error';
        return;
      }

      if (data.result === 'success') {
        // Capturer le temps de victoire avant d'arrêter le timer
        victoryTime = Math.floor(Date.now() / 1000);
        finalResp.textContent = data.message;
        finalResp.className = 'status-success';
        showVictoryPopup();
        stopTimer();
      } else if (data.result === 'defeat') {
        // Gérer la défaite
        console.log('💥 Défaite détectée, affichage popup');
        finalResp.textContent = data.message;
        finalResp.className = 'status-error';
        showDefeatPopup();
        stopTimer();
      } else {
        console.log('❌ Échec simple:', data.result);
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
