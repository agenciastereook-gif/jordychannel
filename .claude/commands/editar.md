---
description: Claude edita el short (cortes, encuadres, textos, imágenes IA) y lo deja listo en el Editor de Estudio
---
Editá el short. Carpeta: $ARGUMENTS (si está vacío, la carpeta más reciente de `episodios/`).
Sos el editor de video de Jordy en Vivo. Las reglas de edición son las de `prompts/estudio/editar.md`
(Jordy las edita desde Estudio): leelo y seguilo, ignorando su formato de respuesta; acá escribís el archivo final.

1. Leé de la carpeta: `guion.md`, `guion_meta.json`, `marcas.txt` (segundo y frase), `voz.srt`,
   `asignacion.txt` (si hay), `material/creditos.json`, `edicion.json` (si hay) y `.mini/*.txt` (descripciones de videos).
   Mirá cada foto de `material/` y el fotograma de cada video (`.mini/<video>.jpg`).
   Si falta la voz transcripta o el material, decí qué falta y pará.
2. Imágenes IA (solo donde no hay material bueno, máx. 6, nunca personas reales, fotografía realista estilo fotoperiodismo, nunca dibujos):
   `python scripts/generar_imagen.py <carpeta> "descripción"` (tarda ~1 min, imprime la ruta; queda en `material/`).
   Si a esa imagen le suma movimiento, hacé el video en este orden (Jordy autorizó bajar estos videos a `material/`):
   a. Con los créditos gratis del día, en el Chrome de Jordy (herramientas Claude in Chrome, su sesión de Google ya abierta):
      Google Flow (labs.google/fx/tools/flow), imagen a video, vertical 9:16, con el pedido
      "Animá esta imagen como video vertical de 5 segundos. <movimiento>". Bajá el video a `<carpeta>/material/`.
      Si Flow no tiene créditos, lo mismo en Kling (klingai.com). No aceptes pagos, pruebas pagas ni cambies nada de la cuenta.
   b. Si no quedan créditos o falla: en esta PC, `python scripts/animar_imagen.py <carpeta>/material/<imagen> "movimiento"`
      (unos minutos, imprime la ruta del .mp4). Deforma los textos: no la uses para imágenes con letras.
   c. Si todo falla, queda la foto con movimiento de cámara y lo avisás en el resumen.
3. Escribí `edicion.json` (lo lee el Editor de Estudio). Conservá de la `edicion.json` anterior `capas.videos`,
   `capas.audios`, `capas.subtitulos` y los textos sin `"ia": true`; reemplazá los segmentos y los textos `ia`.
   ```json
   {"segmentos": [{"t": 0, "archivo": "foto.jpg", "modo": "recorte", "crop": null, "mov": "zoom_in"}],
    "capas": {"textos": [{"id": "ia1", "ia": true, "texto": "LULA DA SILVA · PRESIDENTE", "ini": 1.0, "fin": 4.0, "estilo": {...}}],
              "videos": [], "audios": [], "subtitulos": {"activo": false, "estilo": {}}}}
   ```
   - Segmentos: `t` = segundo de una frase de `marcas.txt` (el primero en 0), un cambio cada 2 a 5 s.
   - Encuadre: siempre `recorte` (pantalla completa); `blur` solo si al recortar se pierde lo importante.
   - Toda foto lleva `mov` (zoom_in, zoom_out, pan_der, pan_izq, pan_arriba, pan_abajo), alternados. Cada archivo una sola vez.
   - Textos arriba (abajo van los subtítulos), sin superponerse ni repetirse.
   - `recorte`: crop = fracciones x, y, w, h del original, con w/h en píxeles = 9/16 (medí con ffmpeg si hace falta).
   - Estilo de textos: el de un texto que ya exista; si no, el `principal` del perfil actual de
     `P:\TRANSMISIONES\JORDY EN VIVO\GRAPH\v2\ajustes.json` con `tamano` × 1.6, `posicion: "arriba-izq"`, `margen_x: 60`, `margen_y: 230`.
   - Nunca inventes datos: todo sale del guion.
4. Borrá `.pedido_claude` y `.pedido_en_curso` de la carpeta si existen.
5. Resumí en 3 líneas qué hiciste y decile a Jordy que lo revise en la pestaña Editor y le dé "OK · Armar video".
