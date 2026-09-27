# Jordy Channel — instrucciones para Claude Code

Este repo es la fábrica de shorts de noticias de un canal de noticias de Jordy, periodista. La rutina completa está en `RUTINA.md`; los prompts en `prompts/`.

Cuando Jordy diga algo como "hagamos el short de hoy", seguí `RUTINA.md` paso a paso:
1. Creá `episodios/AAAA-MM-DD-slug/` (fecha de hoy).
2. Guion con `prompts/01_guion_short.md`. Nunca inventes datos, citas ni cifras; marcá `[VERIFICAR]`.
3. Esperá a que Jordy grabe `voz.*` y exporte `voz.srt` (TurboScribe).
4. `python3 scripts/srt_a_marcas.py <carpeta>/voz.srt > <carpeta>/marcas.txt`
5. Imágenes con `prompts/02_imagenes.md` usando la skill de Higgsfield: una por marca, guardadas
   en `<carpeta>/imagenes/` con nombre = segundos (`0.00.png`, `2.40.png`).
6. Pedí a Jordy que revise las imágenes antes de armar.
7. `python3 scripts/armar_video.py --audio <carpeta>/voz.mp3 --imagenes <carpeta>/imagenes --subs <carpeta>/voz.srt --salida <carpeta>/short.mp4`
8. Textos de publicación con `prompts/03_publicacion.md`.

Idioma: español rioplatense, voseo. Criterio periodístico por sobre la velocidad.
Los archivos de `episodios/` (audio, imágenes, video) no se suben a git.
