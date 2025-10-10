document.addEventListener('DOMContentLoaded', () => {
  const countries = document.querySelectorAll('.country');
  const timerEl = document.getElementById('timer');
  
  // -------------------------- Timer synchronisé avec WebSocket --------------------------
  let websocket = null;
  const TOTAL_DURATION = 30 * 60; // 30 minutes
  let reconnectAttempts = 0;
  const MAX_RECONNECT_ATTEMPTS = 5;

  function startTimer() {
    if (websocket) {
      websocket.close();
    }

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

          if (timerEl) timerEl.textContent = `${m}:${s}`;

          if (timeLeft <= 0) {
            stopTimer();
            alert('💥 Temps écoulé ! Explosion virtuelle !');
            window.location.reload();
          }
          return;
        }

        if (data.type === 'game_success') {
          stopTimer();
          alert('🎉 Pipeline sécurisé ! Victoire !');
          return;
        }

        if (data.game_completed) {
          stopTimer();
          alert('🎉 Pipeline sécurisé ! Victoire !');
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
        console.error('❌ Échec de reconnexion WebSocket');
      }
    };
  }

  function stopTimer() {
    if (websocket) {
      websocket.close();
      websocket = null;
    }
  }

  // Démarrer le timer WebSocket
  startTimer();

  countries.forEach(c => {
    c.addEventListener('click', async () => {
      const code = c.dataset.code;
      if (code === 'RU') {
        window.location.href = '/login';
      } else {
        // La pénalité sera appliquée côté serveur et synchronisée via WebSocket
        // Pas besoin de faire quoi que ce soit ici, le serveur s'en charge
      }
    });
  });
});
