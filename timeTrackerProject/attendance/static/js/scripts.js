function showTooltip(event, tooltipId) {
    const tooltip = document.getElementById(tooltipId);
    tooltip.style.left = `${event.clientX}px`; // Posición horizontal según la posición del ratón
    tooltip.style.top = `${event.clientY}px`; // Posición vertical según la posición del ratón
    tooltip.classList.add('visible'); // Clase para hacer visible el tooltip
}