document.addEventListener('DOMContentLoaded', () => {
  const countries = document.querySelectorAll('.country');
  const timerEl = document.getElementById('timer');
  let totalTime = 30 * 60; // 30 minutes
  let start = Date.now();

  function updateTimer() {
    const elapsed = Math.floor((Date.now() - start)/1000);
    const remaining = Math.max(totalTime - elapsed, 0);
    const m = String(Math.floor(remaining/60)).padStart(2,'0');
    const s = String(remaining%60).padStart(2,'0');
    timerEl.textContent = `${m}:${s}`;
    if (remaining <= 0) {
      alert('💥 Temps écoulé ! Explosion virtuelle !');
      window.location.reload();
    }
  }
  setInterval(updateTimer, 1000);
  updateTimer();

  countries.forEach(c => {
    c.addEventListener('click', async () => {
      const code = c.dataset.code;
      if (code === 'RU') {
        window.location.href = '/login';
      } else {
        // si erreur, pénalité 5 min
        totalTime -= 5*60;
        alert('❌ Mauvais choix ! 5 minutes perdues.');
      }
    });
  });
});
