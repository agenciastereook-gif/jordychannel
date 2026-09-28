---
description: Claude edita el short con la identidad de Jordy en Vivo y entrega el video final (short.mp4)
---
Editá el short y entregá el video final terminado. Carpeta: $ARGUMENTS (si está vacío, la carpeta más reciente de `episodios/`).
Sos el editor de video de Jordy en Vivo. El resultado de esta tarea es el archivo de video editado, listo para
publicar: no una propuesta para terminar en el Editor de Estudio. Las reglas de edición de `prompts/estudio/editar.md`
siguen valiendo (ignorá su formato de respuesta).

1. Referencia (ya asignada: respetala). Leé de la carpeta: `guion.md`, `guion_meta.json`, la voz (`voz.<ext>`),
   `voz.srt` (subtítulos), `marcas.txt` (segundo y frase), `asignacion.txt` y `edicion.json` (si las dos existen, manda
   la más nueva), `material/creditos.json` y `.mini/*.txt` (descripciones de videos). Mirá cada foto de `material/` y el
   fotograma de cada video (`.mini/<video>.jpg`). Qué imagen va en cada frase ya está decidido: usalo tal cual. Solo
   cambiás un corte si el archivo falta o no sirve, y lo decís en el resumen. Si falta la voz, la transcripción o el
   material, decí qué falta y pará.
2. Imágenes IA (solo donde no hay material bueno, máx. 6, nunca personas reales, fotografía realista estilo fotoperiodismo, nunca dibujos):
   `python scripts/generar_imagen.py <carpeta> "descripción"` (tarda ~1 min, imprime la ruta; queda en `material/`).
   Si a esa imagen le suma movimiento, hacé el video en este orden (Jordy autorizó bajar estos videos a `material/`):
   a. Con los créditos gratis del día, en el Chrome de Jordy (herramientas Claude in Chrome, su sesión de Google ya abierta):
      Google Flow (labs.google/fx/tools/flow), imagen a video, vertical 9:16, con el pedido
      "Animá esta imagen como video vertical de 5 segundos. <movimiento>". Bajá el video a `<carpeta>/material/`.
      Si Flow no tiene créditos, lo mismo en Kling (klingai.com). No aceptes pagos, pruebas pagas ni cambies nada de la cuenta.
   b. Si no quedan créditos o falla: en esta PC, `python scripts/animar_imagen.py <carpeta>/material/<imagen> "movimiento"`
      (unos minutos, imprime la ruta del .mp4). Deforma los textos: no la uses para imágenes con letras.
   c. Si todo falla, queda la foto y lo avisás en el resumen.
3. Identidad visual: todo lo gráfico sale de `identidad/jordy-en-vivo/`. Leé `LEEME.md` completo e `identidad.json`
   (geometría exacta en `formats.vertical.pieces`, colores en `palette`, fuentes en `fuentes/`, logos en `logos/`,
   movimiento en `motion` y en la sección 6 del LEEME). `generar_kit.py` dibuja las piezas con Pillow: reutilizá su
   código para dibujarlas con el texto real. Mirá `muestras/vertical-*.png` para ver cómo tienen que quedar.
   - Marca de agua: todo el video.
   - Subtítulos: los de `voz.srt`, con el bloque de subtítulos de la identidad (en lugar de los subtítulos comunes).
   - Zócalo: en la primera aparición de cada persona que el guion nombra, con nombre y cargo tal como están en el guion.
   - Crédito de imagen: `Imagen: <fuente>` de `material/creditos.json`, mientras está en pantalla ese material.
   - Placa de dato o de cita: solo si el guion tiene una cifra central o una cita textual; texto exacto del guion,
     con su fuente; tiempos de lectura de la identidad.
   - Entre imágenes, corte directo (fundido de 0,12 s solo entre fotos de una misma escena). Las piezas entran y salen
     con los tiempos y las curvas de la sección 6. Orden de capas y piezas excluyentes: sección 7 del LEEME.
   - Si un texto no entra en su caja al tamaño mínimo, no lo acortes ni lo inventes: dividí la pieza o no la pongas,
     y avisalo en el resumen.
   Encuadre: pantalla completa (recorte 9:16); blur atrás solo si al recortar se pierde lo importante. Ningún video
   más de 5 s seguidos.
4. Armado: editá vos el video con ffmpeg y Python (Pillow). Base: la voz con cada imagen o video en su segundo, sin el
   audio de los videos salvo los fragmentos marcados como sonido original. Encima, las piezas de la identidad como PNG
   con transparencia (guardalos en `<carpeta>/graficos/`), animadas con ffmpeg (`overlay` con posición y opacidad
   en función del tiempo). Actualizá `edicion.json` con los cortes que usaste, para que Estudio muestre lo mismo.
   Salida: `<carpeta>/short.mp4`, 1080×1920, 30 fps, H.264 y AAC.
5. Control antes de entregar: la duración coincide con la voz (más los clips de sonido original). Sacá fotogramas,
   uno por cada pieza gráfica y uno cada 5 s, y miralos: textos dentro de su caja y sin cortar, nada tapa caras ni
   otra pieza, subtítulos a tiempo con la voz, marca de agua visible, ningún cuadro negro o congelado. Si algo falla,
   corregilo y volvé a armar.
6. Entrega: borrá `.pedido_claude` y `.pedido_en_curso` de la carpeta si existen. Abrí `short.mp4`
   (`start "" "<ruta>"` en Windows). Si esta sesión puede enviarle archivos a Jordy, mandale `short.mp4`.
   Terminá con la ruta del video y tres líneas: qué piezas gráficas usaste, qué cambiaste de la asignación y qué no
   se pudo hacer.

No termines el turno con procesos en segundo plano trabajando: esperalos en primer plano.
