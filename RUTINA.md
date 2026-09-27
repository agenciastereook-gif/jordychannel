# Sistema estándar — Jordy en Vivo · El Hit · El Recorte

Es el método del video original (voz propia + imágenes que cambian cada 2–4 segundos, cada una en
su segundo exacto), con herramientas gratis. Una persona. La versión con IA paga está guardada en
la rama `sistema-premium`, para cuando esto sea rentable.

## Los pasos del short (siempre iguales)

Carpeta del día: `episodios/AAAA-MM-DD-slug/`

| # | Paso | Herramienta | Quién | Queda guardado |
|---|---|---|---|---|
| 0 | Investigación: fuentes, cruce y datos | ChatGPT con `prompts/00_investigacion.md` | ChatGPT (vos revisás) | `investigacion.md` |
| 1 | Guion + qué mostrar en cada frase | ChatGPT con `prompts/01_guion_chatgpt.md` | ChatGPT (vos verificás) | `guion.md` |
| 2 | Grabar la voz | Celular o micrófono | Vos | `voz.mp3` |
| 3 | Marcas de tiempo | TurboScribe → exportar SRT | Vos | `voz.srt` |
| 4 | Juntar fotos y videos | La "lista de búsqueda" del guion | Vos | `material/` |
| 5 | Asignar cada archivo a su segundo | Claude Code con `prompts/02_asignar_material.md` | Claude (vos das OK) | `imagenes/` |
| 6 | Armar el video | `scripts/armar_video.py` | Claude | `short.mp4` |
| 7 | Textos para publicar | `prompts/03_publicacion.md` | Claude | — |

Comando del paso 6:
```
python3 scripts/armar_video.py --audio episodios/<carpeta>/voz.mp3 --imagenes episodios/<carpeta>/imagenes --subs episodios/<carpeta>/voz.srt --salida episodios/<carpeta>/short.mp4
```

**IA (opcional, para más adelante):** si una frase no tiene material, en el guion va como `IA`.
Mientras no haya herramienta, queda la imagen anterior en pantalla. El día que la haya, la imagen
o animación se guarda en `material/` y se cambia esa línea en `asignacion.txt`. Nada más cambia.

**Fotos:** personas reales siempre con foto o video real. Fuentes seguras: fotos oficiales de
gobiernos y organismos, Wikimedia Commons (mirar licencia), capturas con crédito del medio.
Nunca fotos de agencia (Reuters, AFP, Getty) sin licencia. Crédito en la descripción.

## Dónde sale cada cosa

| Pieza | Piso | Ideal | Sale en |
|---|---|---|---|
| Short de la noticia (lun–vie) | 1 por día | 1 por día | IG collab El Hit + Jordy · YouTube Shorts Jordy · dato a X de El Hit |
| El Hit extra (placa, carrusel, breaking) | 1 por día | 2 por día | IG El Hit (`prompts/04_el_hit.md`) |
| El Recorte | 1 clip por día | 2 por día | IG El Recorte, collab con El Hit si es noticia, X de El Hit (`prompts/05_recorte.md`) |
| Video largo | 1 por semana | 1 por semana | YouTube Jordy (`prompts/06_video_largo.md`, mismos 7 pasos en `--formato horizontal`) |
| Clips del largo (finde) | 1 | 2+ | Stock para Reels/Shorts (`prompts/07_clips.md` + `--desde/--hasta`) |

El piso es obligatorio; el ideal, si hay tiempo. Semana complicada: short 3 días y se usa el stock.
