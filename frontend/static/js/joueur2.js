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

  let eventSource = null;

  // -------------------------- timer synchronisé --------------------------
  function startTimer() {
    if (eventSource) {
      eventSource.close();
    }
    
    // Utiliser Server-Sent Events pour la synchronisation en temps réel
    eventSource = new EventSource('/timer/stream');
    
    eventSource.onmessage = function(event) {
      try {
        const data = JSON.parse(event.data);
        
        // Vérifier si c'est une notification de synchronisation
        if (data.type === 'timer_update') {
          console.log('Synchronisation du timer reçue (Joueur2):', data);
          // Mettre à jour immédiatement le timer
          const timeLeft = Number(data.remaining) || 0;
          const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
          const s = String(timeLeft % 60).padStart(2, '0');
          timerEl.textContent = `${m}:${s}`;
          
          if (timeLeft <= 0) {
            stopTimer();
          }
          return;
        }
        
        // Vérifier si c'est une notification de victoire
        if (data.type === 'game_success') {
          console.log('Victoire reçue (Joueur2):', data);
          stopTimer();
          showVictoryPopup();
          return;
        }
        
        // Vérifier si le jeu est terminé
        if (data.game_completed) {
          console.log('🎉 Jeu terminé (Joueur2):', data);
          stopTimer();
          showVictoryPopup();
          return;
        }
        
        // Mise à jour normale du timer
        const timeLeft = Number(data.remaining) || 0;
        const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
        const s = String(timeLeft % 60).padStart(2, '0');
        timerEl.textContent = `${m}:${s}`;
        
        if (timeLeft <= 0) {
          stopTimer();
        }
      } catch (e) {
        console.error('Erreur parsing timer data:', e);
      }
    };
    
    eventSource.onerror = function(event) {
      console.error('Erreur EventSource timer:', event);
      // En cas d'erreur, fallback vers la méthode classique
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

  // Fallback en cas de problème avec SSE
  function startTimerFallback() {
    console.log('Utilisation du fallback timer pour joueur2');
    const fallbackInterval = setInterval(async () => {
      try {
        const res = await fetch('/timer');
        if (!res.ok) return;
        const data = await res.json();
        const timeLeft = Number(data.remaining) || 0;
        const m = String(Math.floor(timeLeft / 60)).padStart(2, '0');
        const s = String(timeLeft % 60).padStart(2, '0');
        timerEl.textContent = `${m}:${s}`;
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

  // Fonction pour forcer la synchronisation du timer
  async function forceTimerSync() {
    try {
      await fetch('/timer/sync', { method: 'POST' });
      // Redémarrer le timer synchronisé
      startTimer();
    } catch (e) {
      console.error('Erreur synchronisation timer:', e);
    }
  }

  // Fonction pour afficher la popup de victoire
  function showVictoryPopup() {
    console.log('🎉 Affichage popup victoire (Joueur2)');
    const popup = document.getElementById('victoryPopup');
    const totalTimeEl = document.getElementById('totalTime');
    const securedPipelineEl = document.getElementById('securedPipeline');
    
    if (!popup) {
      console.error('❌ Popup de victoire non trouvée dans le DOM');
      return;
    }
    
    // Calculer le temps total écoulé
    const startTime = new Date().getTime() - (30 * 60 * 1000); // Approximation
    const totalSeconds = Math.floor((new Date().getTime() - startTime) / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    if (totalTimeEl) totalTimeEl.textContent = timeString;
    if (securedPipelineEl) securedPipelineEl.textContent = siteInput.value || 'Pipeline sécurisé';
    
    popup.style.display = 'flex';
    console.log('✅ Popup de victoire affichée');
  }

  // Fonction pour fermer la popup
  window.closeVictoryPopup = function() {
    const popup = document.getElementById('victoryPopup');
    if (popup) {
      popup.style.display = 'none';
    }
  }

  // -------------------------- prédiction --------------------------
  predictForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    console.log('Formulaire soumis !');
    predictResultsContent.textContent = '⏳ Calcul en cours...';
    predictResultsContent.className = 'results-content';

    const lat = parseFloat(document.getElementById('lat').value);
    const lon = parseFloat(document.getElementById('lon').value);
    const capacity = parseFloat(document.getElementById('capacity').value);
    const year = parseInt(document.getElementById('year').value);

    console.log('Données envoyées:', { lat, lon, capacity, year });

    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat, lon, capacity, year })
      });
      console.log('Réponse reçue:', res.status);
      if (!res.ok) {
        const errorText = await res.text();
        console.error('Erreur serveur:', errorText);
        throw new Error(errorText);
      }
      const data = await res.json();
      console.log('Données reçues:', data);
      const pct = Math.round(data.score * 100);
      predictResultsContent.textContent = `Score de confiance IA : ${pct}%`;
      predictResultsContent.className = 'results-content status-success';
    } catch (err) {
      console.error('Erreur complète:', err);
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
        // Afficher popup de victoire et stopper timer seulement après succès
        showVictoryPopup();
        stopTimer();
      } else {
        finalResp.textContent = data.message;
        finalResp.className = 'status-error';
        // Ne pas arrêter le timer en cas d'erreur
      }
    } catch (err) {
      finalResp.textContent = 'Erreur de communication : ' + err.message;
      finalResp.className = 'status-error';
    } finally {
      finalBtn.disabled = false;
    }
  });
});
