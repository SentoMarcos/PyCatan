  const players = ["P1", "P2", "P3", "P4"];

  const icons = {
    madera: 'Images/cartas/madera.png',
    arcilla: 'Images/cartas/arcilla.png',
    oveja: 'Images/cartas/oveja.png',
    trigo: 'Images/cartas/trigo.png',
    piedra: 'Images/cartas/piedra.png',
    puntos_de_victoria: 'Images/cartas/punto.png',
    caballeros: 'Images/cartas/caballero.png',
    construccion_de_carreteras: 'Images/cartas/carreteras.png',
    año_de_cosecha: 'Images/cartas/cosecha.png',
    monopolio: 'Images/cartas/monopolio.png'
  };

  function createCardRow(items, rowClass) {
  return `
    <div class="row ${rowClass}">
      ${items.map(item => `
        <div class="${item} col" data-id="${item}">
          <img src="${icons[item]}" alt="${item}" width="28" height="28" title="${item.replaceAll('_', ' ')}" />
          <span>: </span>
          <span class="${item}_quantity">0</span>
          <i class="fa-solid increment"></i>
        </div>
      `).join('')}
    </div>
  `;
}


  function generatePlayerHand(id) {
    const topRowItems = ["madera", "arcilla", "oveja", "trigo", "piedra"];
    const bottomRowItems = ["puntos_de_victoria", "caballeros", "construccion_de_carreteras", "año_de_cosecha", "monopolio"];

    return `
      <div id="hand_${id}" class="hand text-center">
        <div class="jugador">
            <h3>${id}</h3>
            <img src="Images/cartas/mejor_caballero.png" width="28" height="28" style="opacity: 0.5;" title="Mayor ejercito">
            <img src="Images/cartas/mejor_carretera.png" width="28" height="28" style="opacity: 0.5;" title="Carretera más larga">
        </div>
        ${createCardRow(topRowItems, "top_hand_row")}
        ${createCardRow(bottomRowItems, "bottom_hand_row")}
      </div>
    `;
  }


  const container = document.getElementById("playersContainer");
  container.innerHTML = players.map(player => generatePlayerHand(player)).join('');
