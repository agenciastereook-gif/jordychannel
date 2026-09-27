---
description: Arma el short de la carpeta de episodio más reciente (transcribe, asigna material, arma el video y los textos)
---
Armá el short. Carpeta: $ARGUMENTS (si está vacío, usá la carpeta más reciente de `episodios/`).
En Windows usá `python` (o `py` si `python` no existe).

1. Verificá que haya: `guion.md` con el guion pegado, un archivo de audio en la raíz de la carpeta
   (cualquier nombre: mp3, m4a, wav, ogg, opus, aac) y archivos en `material/`. Si falta algo,
   decí exactamente qué falta y pará.
2. Renombrá el audio a `voz.<extensión>` (si hay más de uno, preguntá cuál es la voz).
3. Si no existe `voz.srt`: `python scripts/transcribir.py <carpeta>/voz.<ext>`.
   Si falla por falta de faster-whisper, decile a Jordy que corra `INSTALAR.bat`.
4. `python scripts/srt_a_marcas.py <carpeta>/voz.srt > <carpeta>/marcas.txt`
5. Seguí `prompts/02_asignar_material.md` desde el paso 2: mirá el material, escribí
   `asignacion.txt`, mostrá la asignación en una tabla corta y **esperá el OK de Jordy**.
6. Con el OK: `python scripts/asignar_material.py <carpeta>/asignacion.txt` y después
   `python scripts/armar_video.py --audio <carpeta>/voz.<ext> --imagenes <carpeta>/imagenes --subs <carpeta>/voz.srt --salida <carpeta>/short.mp4`
7. Abrí la carpeta para que Jordy vea `short.mp4`, y escribí los textos de `prompts/03_publicacion.md`
   en `<carpeta>/textos.md`.

No generes imágenes, diseños ni nada que no esté en estos pasos. Respuestas cortas.
