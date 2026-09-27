# Prompt 2 — Imágenes por marca de tiempo (Higgsfield / "Hexfield")

Pegá esto en Claude Code **debajo** del listado de marcas que genera
`scripts/srt_a_marcas.py`. Claude usa la skill de generación de imágenes instalada.

---

Vas a generar imágenes para un video de noticias: **una imagen por cada marca de tiempo** del
listado de abajo. No agrupes ni saltees marcas: si hay 25 marcas, son 25 imágenes.

Para cada línea `[segundos] texto`, generá una ilustración que muestre lo que se dice en esa frase.

Estilo (igual en todas, para que el canal sea reconocible):
- Dibujo extremadamente simple, estilo MS Paint hecho a mano por un principiante.
- Trazo negro grueso, pocos colores planos (rojo, amarillo, azul), **fondo blanco**.
- Sin 3D, sin sombras realistas, sin estilo cinematográfico, sin fotorrealismo.
- Personajes tipo muñequito/caricatura simple. Se puede usar un rasgo reconocible
  (pelo, anteojos, camiseta, micrófono) pero **nunca** un retrato realista de una persona real.
- Texto dentro de la imagen: solo si es 1–3 palabras clave (ej. "JUICIO", "$ 3 MILLONES").
- Formato **vertical 9:16** (para short). Si te pido video largo: 16:9.

Reglas de cuidado (es un canal de noticias):
- No dibujes a una persona real cometiendo un delito o en una situación íntima/humillante
  que no esté confirmada. Para acusaciones o rumores, usá símbolos (un sobre, un juzgado,
  un signo de pregunta, un teléfono) en vez de la persona.
- Nada de logos de marcas, medios o partidos políticos.

Cuando termines:
1. Descargá todas las imágenes a `episodios/<fecha>-<slug>/imagenes/`.
2. Renombrá cada archivo con su marca exacta en segundos: `0.00.png`, `3.42.png`, `7.10.png`...
3. Decime cuántas imágenes quedaron y si alguna marca falló.

MARCAS:
<pegá acá la salida de srt_a_marcas.py>
