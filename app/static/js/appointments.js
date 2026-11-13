(() => {
  const service = document.querySelector('#service-id');
  const start = document.querySelector('#start-at');
  const quoteBox = document.querySelector('#quote-box');
  if (!service || !start || !quoteBox) return;
  let controller;
  const render = (message, kind = 'secondary') => {
    quoteBox.className = `quote-box rounded p-3 mb-3 text-${kind}`;
    quoteBox.textContent = message;
  };
  async function updateQuote() {
    if (!service.value || !start.value) {
      render('Selecciona servicio y horario para calcular el precio.');
      return;
    }
    if (controller) controller.abort();
    controller = new AbortController();
    render('Calculando tarifa…');
    try {
      const params = new URLSearchParams({service_id: service.value, start_at: `${start.value}:00`});
      const response = await fetch(`/appointments/quote?${params}`, {signal: controller.signal});
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'No se pudo calcular la tarifa.');
      render(`Precio final: $${Number(data.price).toLocaleString('es-CO')} COP · ${data.strategy} · ${data.duration_minutes} min`, 'success');
    } catch (error) {
      if (error.name !== 'AbortError') render(error.message, 'danger');
    }
  }
  service.addEventListener('change', updateQuote);
  start.addEventListener('change', updateQuote);
})();
