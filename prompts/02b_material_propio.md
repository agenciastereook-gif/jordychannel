# Prompt 2b — Ilustrar con tus fotos y videos reales

Antes: poné tus fotos y videos en `episodios/<carpeta>/material/` (nombres libres, por ejemplo
`lula_firma.jpg`, `congreso.mp4`). Después pegá esto en Claude Code:

---

En `episodios/<carpeta>/material/` están las fotos y videos que tienen que ilustrar el guion.
Las marcas de tiempo están en `episodios/<carpeta>/marcas.txt`.

1. **Mirá cada archivo** (las imágenes abrilas; de cada video sacá un fotograma con ffmpeg
   para ver qué muestra) y hacé una lista corta: archivo → qué se ve.
2. **Asigná un archivo a cada marca** según lo que se dice en esa frase:
   - La **primera marca** (el gancho) lleva la foto o el video más fuerte del protagonista.
   - Cuando se nombra a una persona, va su foto real.
   - Un mismo archivo puede repetirse, pero no más de 2 marcas seguidas: si hace falta seguir
     en la misma imagen, usá `=`.
   - Para ideas abstractas (cifras, "prohibición", "apuestas", "millones") o si no hay material
     que sirva, poné `DIBUJO`.
3. Escribí `episodios/<carpeta>/asignacion.txt` con este formato:
   ```
   [0.00] material/lula_firma.jpg | frase de esa marca
   [2.40] DIBUJO | frase
   [4.90] = | frase
   ```
4. Mostrame la asignación y **esperá mi OK** (yo puedo cambiar líneas).
5. Con mi OK corré `python3 scripts/asignar_material.py episodios/<carpeta>/asignacion.txt`.
6. Si quedaron marcas `DIBUJO`, generalas con `prompts/02_imagenes.md` solo para esas marcas
   y guardalas en `episodios/<carpeta>/imagenes/` con su nombre en segundos.
