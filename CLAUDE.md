# Jordy — instrucciones para Claude Code

Este repo organiza la producción de las tres marcas de Jordy (periodista, trabaja solo):
**Jordy en Vivo** (autor), **El Hit** (medio) y **El Recorte** (clips). La rutina está en
`RUTINA.md` y los prompts en `prompts/`. Es una guía flexible: piso obligatorio, ideal opcional.

- "Hagamos el short de hoy" → Bloque 2 de `RUTINA.md` (prompts 01, 02/02b, 03).
- "Usá las fotos de la carpeta" → `prompts/02b_material_propio.md` + `scripts/asignar_material.py`.
- "Pieza de El Hit" → `prompts/04_el_hit.md`. "Clip de El Recorte" → `prompts/05_recorte.md`.
- "Video largo" → `prompts/06_video_largo.md`, luego dibujos 16:9 y `armar_video.py --formato horizontal`.
- "Clips del largo" → `prompts/07_clips.md` y `armar_video.py --desde/--hasta`.

Reglas: nunca inventar datos, citas ni cifras (marcar `[VERIFICAR]`); nombrar fuentes; nada de
dibujar a personas reales (para personas, foto real). Español rioplatense, voseo.
Carpeta por pieza: `episodios/AAAA-MM-DD-slug/` (no se sube a git).
