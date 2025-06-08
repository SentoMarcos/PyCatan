// Obtenemos los elementos del DOM 
const board = document.getElementById("board");
const overlay = document.getElementById("overlay");

// Lista de tipos de terrenos disponibles
const terrainTypes = [
  'madera', 'madera', 'madera', 'madera',
  'trigo', 'trigo', 'trigo', 'trigo',
  'piedra', 'piedra', 'piedra',
  'arcilla', 'arcilla', 'arcilla',
  'oveja', 'oveja', 'oveja', 'oveja',
  'desierto'
];

// Números del 2 al 12 (sin incluir 7)
const numberTokens = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12];

// Mezclar terrenos y números
terrainTypes.sort(() => Math.random() - 0.5);
numberTokens.sort(() => Math.random() - 0.5);

// Imágenes de terrenos
const terrainImages = {
  madera: 'Images/tablero/madera.png',
  trigo: 'Images/tablero/trigo.png',
  piedra: 'Images/tablero/piedra.png',
  arcilla: 'Images/tablero/arcilla.png',
  oveja: 'Images/tablero/oveja.png',
  desierto: 'Images/tablero/desierto.png'
};

// Imágenes de puertos
const portImages = {
  madera: 'Images/tablero/puerto_madera.png',
  trigo: 'Images/tablero/puerto_trigo.png',
  oveja: 'Images/tablero/puerto_oveja.png',
  piedra: 'Images/tablero/puerto_piedra.png',
  arcilla: 'Images/tablero/puerto_arcilla.png',
  '3:1': 'Images/tablero/puerto_3.png',
  agua: 'Images/tablero/agua.png'
};

// Tipos de puertos
const portTypes = ['madera', 'trigo', 'oveja', 'piedra', 'arcilla', '3:1', '3:1', '3:1', '3:1'];
portTypes.sort(() => Math.random() - 0.5);

// Disposición hexagonal extendida
const layout = [4, 5, 6, 7, 6, 5, 4];
const hexSize = 101.6;
const hexHeight = 101.6;
const xSpacing = hexSize * 0.89;
const ySpacing = hexHeight * 0.72;

let terrainIndex = 0;
let numberIndex = 0;
let portIndex = 0;
let hexCenters = [];
let edgeHexes = [];

layout.forEach((hexCount, rowIndex) => {
  const row = document.createElement('div');
  row.classList.add('row');
  const offset = (layout[3] - hexCount) * xSpacing / 2;

  for (let i = 0; i < hexCount; i++) {
    const hex = document.createElement('div');
    hex.className = 'hex';

    const x = offset + i * xSpacing + hexSize / 2;
    const y = rowIndex * ySpacing + hexHeight / 2;

    const isEdge =
      rowIndex === 0 || rowIndex === layout.length - 1 || i === 0 || i === hexCount - 1;

    if (isEdge) {
      if (portIndex < portTypes.length) {
        const portType = portTypes[portIndex++];
        hex.style.backgroundImage = `url(${portImages[portType]})`;
      } else {
        hex.style.backgroundImage = `url(${portImages.agua})`;
      }
    } else {
      const terrain = terrainTypes[terrainIndex++];
      hex.style.backgroundImage = `url(${terrainImages[terrain]})`;

      if (terrain !== 'desierto') {
        const numberToken = document.createElement('div');
        numberToken.className = 'number-token';
        numberToken.innerText = numberTokens[numberIndex++];
        hex.appendChild(numberToken);
      }

      // Solo se crean nodos/caminos para terrenos (no para agua ni puertos)
      hexCenters.push({ x, y });
    }

    const centerCircle = document.createElement('div');
    centerCircle.className = 'hex-center';
    hex.appendChild(centerCircle);

    row.appendChild(hex);
  }


  board.appendChild(row);
});

// === NODOS Y CAMINOS ===

function roundToGrid(value, gridSize = 35) {
  return Math.round(value / gridSize) * gridSize;
}

function addOverlayElements() {
  const radius = hexSize / 2;
  const angleOffset = -30;
  const nodeMap = new Map();
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

    for (let i = 0; i < 6; i++) {
      const nodeA = localNodes[i];
      const nodeB = localNodes[(i + 1) % 6];

      const px = (nodeA.x + nodeB.x) / 2;
      const py = (nodeA.y + nodeB.y) / 2;
      const angleDeg = Math.atan2(nodeB.y - nodeA.y, nodeB.x - nodeA.x) * (180 / Math.PI);
      const pkey = `${roundToGrid(px)},${roundToGrid(py)}`;

      if (!roadMap.has(pkey)) {
        const id1 = parseInt(nodeA.id.split('_')[1]);
        const id2 = parseInt(nodeB.id.split('_')[1]);
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

addOverlayElements();

// === EVENTOS INTERACTIVOS ===

overlay.addEventListener('click', (e) => {
  if (e.target.classList.contains('node')) {
    console.log("Haz hecho clic en un nodo:", e.target.id);
    e.target.classList.toggle("selected-node");
  } else if (e.target.classList.contains('road')) {
    console.log("Haz hecho clic en un camino");
    e.target.classList.toggle("selected-road");
  }
});
