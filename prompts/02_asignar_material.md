# Prompt 2 — Asignar el material a cada marca de tiempo (Claude Code)

Lo usa `/short` (paso 5). Necesita en la carpeta del día: `guion.md`, `voz.<ext>`, `voz.srt` y las
fotos/videos en `material/`.

---

Carpeta del día: `episodios/<carpeta>/`.

1. Corré `python scripts/srt_a_marcas.py episodios/<carpeta>/voz.srt > episodios/<carpeta>/marcas.txt`.
2. Mirá cada archivo de `material/` (las imágenes abrilas; de cada video sacá un fotograma con
   ffmpeg) y hacé una lista corta: archivo → qué se ve.
3. Asigná un archivo a cada marca de `marcas.txt`, según lo que se dice en cada frase y, si existe,
   el plan de `visual.md`:
   - Si falta material para una marca, poné `IA` (queda en pantalla la imagen anterior).
   - Para no cortar, usá `=` (sigue la imagen anterior).
   - Un mismo archivo no más de 2 marcas seguidas.
   - Por cada `[SONIDO ORIGINAL]` del guion (o `SONIDO ORIGINAL` en `visual.md`), agregá una línea
     `INSERTAR` con el video que tiene ese sonido. Su marca es donde empieza, en `marcas.txt`, la
     frase que en el guion viene justo después del sonido original (Jordy no la graba: la voz se
     corta ahí, pasa el clip y sigue). Si hace falta solo una parte del clip, agregá
     `desde M:SS hasta M:SS`, ubicando el tramo por lo que dice la transcripción del guion.
4. Escribí `episodios/<carpeta>/asignacion.txt`:
   ```
   [0.00] material/lula_firma.jpg | frase
   [2.40] IA | frase
   [4.90] = | frase
   [7.10] material/anuncio.jpg | frase
   [7.10] INSERTAR material/conferencia.mp4 desde 0:12 hasta 0:19 | sonido original
   ```
5. Mostrame la asignación y **esperá mi OK**.
6. Con mi OK: `python scripts/asignar_material.py episodios/<carpeta>/asignacion.txt`.
