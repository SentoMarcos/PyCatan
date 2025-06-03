
// Obtenemos los elementos del DOM donde se insertará el tablero y los nodos/caminos
const board = document.getElementById("board");
const overlay = document.getElementById("overlay");

// Lista de tipos de terrenos disponibles (4 de cada uno, excepto piedra y arcilla que tienen 3, y un desierto)
const terrainTypes = [
  'madera', 'madera', 'madera', 'madera',
  'trigo', 'trigo', 'trigo', 'trigo',
  'piedra', 'piedra', 'piedra',
  'arcilla', 'arcilla', 'arcilla',
  'oveja', 'oveja', 'oveja', 'oveja',
  'desierto'
];

// Números del 2 al 12 (sin incluir 7, que no se usa)
const numberTokens = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12];

// Mezclamos aleatoriamente el array de terrenos
terrainTypes.sort(() => Math.random() - 0.5);
// Mezclamos también los números
numberTokens.sort(() => Math.random() - 0.5);

// Asociamos a cada tipo de terreno una imagen correspondiente
const terrainImages = {
  madera: 'Images/textures/madera.png',
  trigo: 'Images/textures/trigo.png',
  piedra: 'Images/textures/piedra.png',
  arcilla: 'Images/textures/arcilla.png',
  oveja: 'Images/textures/oveja.png',
  desierto: 'Images/textures/desierto.png'
};

// Definimos la disposición del tablero hexagonal (cuántos hexágonos por fila)
const layout = [3, 4, 5, 4, 3];

// Tamaños de los hexágonos
const hexSize = 127;
const hexHeight = 123;

// Espaciado entre hexágonos en X e Y (ajustado para que encajen bien en forma hexagonal)
const xSpacing = hexSize * 0.87;
const ySpacing = hexHeight * 0.775;

let terrainIndex = 0; // Índice actual del terreno
let numberIndex = 0;  // Índice actual del número
let hexCenters = [];  // Lista donde se almacenan los centros (x, y) de cada hexágono

layout.forEach((hexCount, rowIndex) => {
  const row = document.createElement('div');
  row.classList.add('row');
  const offset = (layout[2] - hexCount) * xSpacing / 2;

  for (let i = 0; i < hexCount; i++) {
    const terrain = terrainTypes[terrainIndex++];
    const hex = document.createElement('div');
    hex.className = 'hex';
    hex.style.backgroundImage = `url(${terrainImages[terrain]})`;

    const x = offset + i * xSpacing + hexSize / 2;
    const y = rowIndex * ySpacing + hexHeight / 2;

    hexCenters.push({ x, y, terrain }); // Guardamos la posición y tipo

    // Círculo del centro
    const centerCircle = document.createElement('div');
    centerCircle.className = 'hex-center';
    hex.appendChild(centerCircle);

    // Si no es desierto, le ponemos número
    if (terrain !== 'desierto') {
      const numberToken = document.createElement('div');
      numberToken.className = 'number-token';
      numberToken.innerText = numberTokens[numberIndex++];
      hex.appendChild(numberToken);
    }

    row.appendChild(hex);
  }

  board.appendChild(row);
});

// Auxiliar para evitar duplicados de nodos/caminos
function roundToGrid(value, gridSize = 25) {
  return Math.round(value / gridSize) * gridSize;
}

// Dibuja nodos y caminos
function addOverlayElements() {
  const radius = hexSize / 2;
  const angleOffset = -30;

  const nodeMap = new Map(); // clave: "x,y" redondeado => valor: nodeId
  const roadMap = new Map();

  let nodeIdCounter = 0;

  hexCenters.forEach(({ x, y }) => {
    const localNodes = [];

    for (let i = 0; i < 6; i++) {
      const angle = (angleOffset + i * 60) * (Math.PI / 180);
      const nx = x + radius * Math.cos(angle);
      const ny = y + radius * Math.sin(angle);
      const key = `${roundToGrid(nx)},${roundToGrid(ny)}`;

      let nodeId;

      if (!nodeMap.has(key)) {
        nodeId = `node_${nodeIdCounter++}`;
        const node = document.createElement('div');
        node.className = 'node';
        node.id = nodeId;
        node.style.left = `${nx}px`;
        node.style.top = `${ny}px`;
        overlay.appendChild(node);
        nodeMap.set(key, nodeId);
      } else {
        nodeId = nodeMap.get(key);
      }

      localNodes.push({ x: nx, y: ny, id: nodeId });
    }

    // Crear caminos entre los nodos locales de este hexágono
    for (let i = 0; i < 6; i++) {
      const nodeA = localNodes[i];
      const nodeB = localNodes[(i + 1) % 6];

      const px = (nodeA.x + nodeB.x) / 2;
      const py = (nodeA.y + nodeB.y) / 2;
      const angleDeg = Math.atan2(nodeB.y - nodeA.y, nodeB.x - nodeA.x) * (180 / Math.PI);
      const pkey = `${roundToGrid(px)},${roundToGrid(py)}`;

      // Evitar duplicados
      if (!roadMap.has(pkey)) {
        const id1 = nodeA.id;
        const id2 = nodeB.id;

        // Ordenamos los IDs para evitar duplicados con orden diferente
        const sortedIds = [id1, id2].sort();
        const roadId = `road_${sortedIds[0]}_${sortedIds[1]}`;

        const road = document.createElement('div');
        road.className = 'road';
        road.id = roadId;
        road.style.left = `${px}px`;
        road.style.top = `${py}px`;
        road.style.transform = `translate(-50%, -50%) rotate(${angleDeg}deg)`;
        overlay.appendChild(road);
        roadMap.set(pkey, true);
      }
    }
  });
}


// Ejecutamos la generación de elementos
addOverlayElements();

// === EVENTOS DINÁMICOS PARA ELEMENTOS INTERACTIVOS ===

// Delegación de eventos para nodos
overlay.addEventListener('click', (e) => {
  if (e.target.classList.contains('node')) {
    console.log("Haz hecho clic en un nodo:", e.target.id);
    e.target.classList.toggle("selected-node");
  } else if (e.target.classList.contains('road')) {
    console.log("Haz hecho clic en un camino");
    e.target.classList.toggle("selected-road");
  }
});
