# Prompt 2 — Asignar el material a cada marca de tiempo (Claude Code)

Antes: `guion.md`, `voz.mp3`, `voz.srt` y tus fotos/videos en `material/` dentro de la carpeta del día.
Pegá esto en Claude Code:

---

Carpeta del día: `episodios/<carpeta>/`.

1. Corré `python3 scripts/srt_a_marcas.py episodios/<carpeta>/voz.srt > episodios/<carpeta>/marcas.txt`.
2. Mirá cada archivo de `material/` (las imágenes abrilas; de cada video sacá un fotograma con
   ffmpeg) y hacé una lista corta: archivo → qué se ve.
3. Asigná un archivo a cada marca de `marcas.txt`, según lo que se dice en cada frase y, si existe,
   el plan de `visual.md`:
   - Si falta material para una marca, poné `IA` (queda en pantalla la imagen anterior).
   - Para no cortar, usá `=` (sigue la imagen anterior).
   - Un mismo archivo no más de 2 marcas seguidas.
4. Escribí `episodios/<carpeta>/asignacion.txt`:
   ```
   [0.00] material/lula_firma.jpg | frase
   [2.40] IA | frase
   [4.90] = | frase
   ```
5. Mostrame la asignación y **esperá mi OK**.
6. Con mi OK: `python3 scripts/asignar_material.py episodios/<carpeta>/asignacion.txt`.
