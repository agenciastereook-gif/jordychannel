# jordychannel — sistema estándar

Producción de **Jordy en Vivo · El Hit · El Recorte** con herramientas gratis. Empezá por `RUTINA.md`.

- `INSTALAR.bat` — instala lo necesario (una vez).
- **`ESTUDIO.pyw`** — el panel: investigación y guion (ChatGPT vía Codex), voz y material, asignación y textos (Claude), video. Gemini (Gemini CLI, cuenta de Google): segunda opinión de la investigación, revisión de datos del guion y mira los videos completos para la asignación. Interfaz en `estudio/index.html`, mismo diseño que StreamDash. Se conecta con El Recorte (botón "Mandar a Estudio" y sección "Desde El Recorte").
- Los prompts se editan desde el panel (✎ Editar prompts). Los del panel están en `prompts/estudio/`; el original de cada uno queda en `prompts/.originales/` la primera vez que se edita.
- Sin el panel sigue andando lo de antes: `NUEVO SHORT.bat` + `/short` en Claude Code.
La versión con IA paga está en la rama `sistema-premium`.

- `prompts/00_investigacion.md` — investigación con búsqueda web: fuentes, cruce y datos (ChatGPT).
- `prompts/01_guion_chatgpt.md` — guion en secciones (tipo, guion, títulos, verificaciones); lo usan ChatGPT, Gemini o Claude.
- `modelos/MANUAL_DE_ESTILO.md` — manual de estilo de los guiones (se sube al Proyecto de ChatGPT). Los guiones reales quedan en `modelos/` como archivo, no se le pasan a ChatGPT.
- `prompts/02_asignar_material.md` — Claude asigna tus fotos/videos a cada segundo.
- `prompts/03`–`07` — publicación, El Hit, El Recorte, video largo, clips.
- `scripts/transcribir.py` — transcribe la voz en la compu y genera el SRT (reemplaza TurboScribe).
- `scripts/nuevo_episodio.py` — crea la carpeta del short.
- `scripts/srt_a_marcas.py` — SRT (de transcribir.py o TurboScribe) → marcas de tiempo.
- `scripts/asignar_material.py` — copia el material a su marca según `asignacion.txt`.
- `scripts/armar_video.py` — voz + fotos/videos → video vertical u horizontal; saca clips de un tramo.
