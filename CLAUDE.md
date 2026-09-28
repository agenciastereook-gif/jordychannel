# Jordy — instrucciones para Claude Code

Sistema estándar (gratis) de producción de **Jordy en Vivo**, **El Hit** y **El Recorte**.
Jordy trabaja solo. Todo está en `RUTINA.md`. El panel `ESTUDIO.pyw` (+ `estudio/index.html`)
hace todo el flujo; los mismos scripts y prompts sirven sin el panel. El short se arma con el comando `/short`
(`.claude/commands/short.md`): seguí esos pasos, no agregues otros.
La edición (cortes, encuadres, textos) la hace Claude: en el panel con "Editar con Claude" (Claude gratis por
Antigravity, `prompts/estudio/editar.md`) o en esta sesión con `/editar`. "Pedir a mi Claude" deja
`.pedido_claude` en la carpeta: si Jordy dice que hay una tarea pendiente, hacé `/pendientes`. Las imágenes IA las genera ChatGPT
(`scripts/generar_imagen.py`), siempre realistas (fotoperiodismo, nunca dibujos); nunca de personas reales.
Encuadre por defecto: pantalla completa. Videos IA: en la PC con Wan2GP (`scripts/animar_imagen.py`, F:\IA\Wan2GP).

- Los guiones los escribe una IA con `prompts/01_guion_chatgpt.md`, no Claude en esta sesión. En el panel
  Jordy elige ChatGPT (Codex CLI, default), Gemini (Antigravity CLI `agy`) o Claude (opcional, plan Pro).
  La respuesta viene en secciones `=== TIPO ===`, `=== GUION ===`... y el panel las separa.
- En el panel, asignación y textos los hace Claude si su CLI tiene sesión (plan Pro); si no, ChatGPT.
  Jordy no tiene plan Pro: el sistema no puede depender de Claude Code CLI ni de nada pago extra.
- Claude (en esta sesión) hace: asignar material (`prompts/02_asignar_material.md` + `scripts/asignar_material.py`),
  armar el video (`scripts/armar_video.py`), textos de publicación (`prompts/03`–`07`).
- No generes imágenes, diseños ni piezas que Jordy no pidió. Ante la duda, preguntá.
- Nunca inventar datos, citas ni cifras. Personas reales: solo foto o video real.
- Material: priorizar fuentes seguras; si no hay, vale cualquiera (Jordy asume el riesgo). Máx. 5 s
  seguidos de un mismo video (microcorte en `armar_video.py`).
- Español rioplatense, voseo. Carpeta por pieza: `episodios/AAAA-MM-DD-slug/` (no va a git).
