# Cambios y correcciones de bugs en PyCatan

## Resumen de los cambios

Se han realizado varias correcciones en el código principal del juego para solucionar bugs críticos detectados en la gestión de recursos, el comercio, la fase inicial y el descarte de cartas con el ladrón. Estos cambios mejoran la fidelidad de la simulación respecto a las reglas originales de Catan y evitan comportamientos erróneos que afectaban a la jugabilidad y a la evaluación de los agentes.

## Detalle de los bugs y su solución

### 1. Recursos duplicados al entregar materiales
**Problema:**
La función `give_resources` sumaba los recursos dos veces a los jugadores, ya que se actualizaba tanto `player['resources']` como `player['player'].hand`, que en la mayoría de los casos referencian el mismo objeto. Esto provocaba que los jugadores recibieran el doble de recursos por cada pueblo o ciudad.

**Solución:**
Ahora solo se suma a `player['resources']` y se sincroniza la mano después, evitando duplicidades.

---

### 2. Comercio: send/receive invertido o incorrecto
**Problema:**
La lógica de intercambio podía dar lugar a situaciones en las que los recursos enviados y recibidos se gestionaban de forma incorrecta, permitiendo a los jugadores ofrecer o recibir recursos que no tenían o no correspondían a la oferta.

**Solución:**
Se ha corregido la función `_trade_with_player` para que el intercambio de materiales sea correcto y coherente con la oferta y la demanda de cada jugador.

---

### 3. Recursos en la ronda inicial
**Problema:**
En la fase inicial, los jugadores recibían recursos al colocar su primer pueblo, cuando según las reglas solo deben recibirlos al colocar el segundo pueblo (segunda ronda de colocación).

**Solución:**
Ahora los recursos solo se otorgan en la segunda ronda de colocación, respetando la mecánica original del juego.

---

### 4. Descarte con el ladrón
**Problema:**
Cuando salía un 7 en los dados, el descarte de cartas no siempre era correcto y podía no ajustarse a la mitad de cartas (redondeando hacia abajo), o descartar materiales que el jugador no tenía.

**Solución:**
Se ha ajustado la función de descarte para que solo se descarten materiales que el jugador realmente posee y hasta llegar a la cantidad correcta.

---

## Ubicación de los cambios

Todos los cambios se han realizado en el archivo `Managers/GameManager.py`.

