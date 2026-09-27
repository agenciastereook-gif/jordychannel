# jordychannel — sistema estándar

Producción de **Jordy en Vivo · El Hit · El Recorte** con herramientas gratis. Empezá por `RUTINA.md`.

- `INSTALAR.bat` — instala lo necesario (una vez). `NUEVO SHORT.bat` — crea la carpeta del short.
- En Claude Code: `/short` arma el video.
La versión con IA paga está en la rama `sistema-premium`.

- `prompts/00_investigacion.md` — investigación con búsqueda web: fuentes, cruce y datos (ChatGPT).
- `prompts/01_guion_chatgpt.md` — guion + qué mostrar (se usa en ChatGPT).
- `modelos/MANUAL_DE_ESTILO.md` — manual de estilo de los guiones (se sube al Proyecto de ChatGPT). Los guiones reales quedan en `modelos/` como archivo, no se le pasan a ChatGPT.
- `prompts/02_asignar_material.md` — Claude asigna tus fotos/videos a cada segundo.
- `prompts/03`–`07` — publicación, El Hit, El Recorte, video largo, clips.
- `scripts/transcribir.py` — transcribe la voz en la compu y genera el SRT (reemplaza TurboScribe).
- `scripts/nuevo_episodio.py` — crea la carpeta del short.
- `scripts/srt_a_marcas.py` — SRT de TurboScribe → marcas de tiempo.
- `scripts/asignar_material.py` — copia el material a su marca según `asignacion.txt`.
- `scripts/armar_video.py` — voz + fotos/videos → video vertical u horizontal; saca clips de un tramo.
