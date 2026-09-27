# Prompt 7 — Clips del video largo (domingo)

Te paso el SRT/marcas del video largo de esta semana. Elegí **2 o 3 tramos de 30 a 60 segundos**
que funcionen solos como Reel/Short vertical:
- Que arranquen con una frase que enganche sin necesitar lo anterior.
- Que terminen en una idea cerrada (no a mitad de frase).

Para cada tramo dame:
1. `--desde` y `--hasta` en formato MM-SS (ajustados al inicio/fin de frase).
2. Título corto y caption de 2 líneas que invite a ver el video completo.
3. ¿Collab con El Recorte? Solo si el valor es un momento de Jordy.

Después, para cada tramo, corré
`python scripts/armar_video.py --audio <carpeta>/voz.<ext> --imagenes <carpeta>/imagenes --subs <carpeta>/voz.srt --desde <MM-SS> --hasta <MM-SS> --salida <carpeta>/clipN.mp4`
y guardá los clips en la carpeta del video largo como `clip1.mp4`, `clip2.mp4`...

MARCAS:
<pegá la salida de srt_a_marcas.py del video largo>
