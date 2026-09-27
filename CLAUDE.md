# Jordy — instrucciones para Claude Code

Sistema estándar (gratis) de producción de **Jordy en Vivo**, **El Hit** y **El Recorte**.
Jordy trabaja solo. Todo está en `RUTINA.md`. El short se arma con el comando `/short`
(`.claude/commands/short.md`): seguí esos pasos, no agregues otros.

- Los guiones los escribe **ChatGPT** (`prompts/01_guion_chatgpt.md`), no Claude.
- Claude hace: asignar material (`prompts/02_asignar_material.md` + `scripts/asignar_material.py`),
  armar el video (`scripts/armar_video.py`), textos de publicación (`prompts/03`, `04`, `05`)
  y clips del largo (`prompts/07_clips.md`).
- No generes imágenes, diseños ni piezas que Jordy no pidió. Ante la duda, preguntá.
- Nunca inventar datos, citas ni cifras. Personas reales: solo foto o video real.
- Español rioplatense, voseo. Carpeta por pieza: `episodios/AAAA-MM-DD-slug/` (no va a git).
