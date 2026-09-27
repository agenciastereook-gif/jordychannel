# Sistema estándar — Jordy en Vivo · El Hit · El Recorte

Es el método del video original (voz propia + imágenes que cambian cada 2–4 segundos, cada una en
su segundo exacto), con herramientas gratis. Una persona. La versión con IA paga está guardada en
la rama `sistema-premium`, para cuando esto sea rentable.

## Una sola vez
Doble clic en **`INSTALAR.bat`**. Si instala Python, cerrá la ventana y abrilo de nuevo.

## Cada short

| # | Qué | Quién |
|---|---|---|
| 1 | Investigación y guion en tus GPT de ChatGPT (Investigador → Guionista) | ChatGPT (vos revisás) |
| 2 | Doble clic en **`NUEVO SHORT.bat`**, escribís el tema → se crea y se abre la carpeta | PC |
| 3 | Pegás el guion en `guion.md`, tirás tu grabación en la carpeta y las fotos/videos en `material/` (cualquier nombre) | Vos |
| 4 | En Claude Code escribís **`/short`** | Vos |
| 5 | Transcribe la voz, asigna el material a cada segundo y te pide OK | PC (Claude) |
| 6 | Arma `short.mp4` y escribe `textos.md` con caption, título y post de X | PC (Claude) |

La transcripción corre gratis en tu compu (reemplaza a TurboScribe). La primera vez baja el modelo
de voz, unos 500 MB.

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
