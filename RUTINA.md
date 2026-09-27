# Rutina diaria — Shorts de noticias con ilustraciones IA

Adaptación del método del canal "Zen" (dibujos simples que cambian cada 2–3 segundos,
sincronizados con la voz) a **Jordy en Vivo**: noticias con voz y criterio propios.

**Meta:** 1 short por día (2 si hay un día muy cargado de noticias, 0 si no hay nada que valga).
**Tiempo objetivo:** 35–45 min por short una vez que la rutina está aceitada.

---

## Antes de arrancar (una sola vez)

1. **Claude Code** en la compu (pestaña *Code*, no *Chat* ni *Cowork*). Abrí esta carpeta del repo.
2. **Generador de imágenes con CLI:** en el video lo llaman "Hexfield"; casi seguro es
   **Higgsfield** (higgsfield.ai). Creá la cuenta → *MCP & CLI* → *CLI* y corré en la terminal,
   en orden, los tres comandos que te da la página (instalar CLI, autorizar, instalar la skill).
   Usá los comandos de su página, no copies los de terceros.
3. **ffmpeg** para que el video se arme solo (reemplaza arrastrar imágenes en el editor):
   - Mac: `brew install ffmpeg` · Windows: `winget install ffmpeg`
   - o, si no querés instalar nada: `pip install imageio-ffmpeg`
4. **TurboScribe** (3 transcripciones gratis por día; alcanza).
5. Micrófono. **Tu voz es el activo**: no uses voz clonada. Además de lo que dice el video
   (canales con ElevenLabs desmonetizados), YouTube no monetiza contenido masivo/repetitivo
   y tu diferencial frente a los canales sin rostro es que un periodista real firma la nota.

---

## La rutina (cada día)

| # | Paso | Tiempo | Quién |
|---|------|--------|-------|
| 1 | Elegir la noticia | 5 min | Vos |
| 2 | Guion | 5–10 min | Claude + vos |
| 3 | Grabar la voz | 5 min | Vos |
| 4 | Transcribir con marcas | 2 min | TurboScribe |
| 5 | Generar imágenes | ~10 min (esperando) | Claude + Higgsfield |
| 6 | Revisar imágenes | 3–5 min | Vos |
| 7 | Armar el video | 1 min | Script |
| 8 | Publicar y reciclar | 5 min | Claude + vos |

### 1. Elegir la noticia (5 min)
Filtro rápido — tiene que cumplir las tres:
- **¿Pasó hoy o ayer?** (el short de noticias vive 24–48 h)
- **¿Lo puedo contar en 60 segundos sin perder lo importante?**
- **¿Tengo una fuente que puedo nombrar?**

Si es algo para investigar o explicar a fondo → no es short: va al **video largo quincenal**.
Si el valor es un clip de otro → es **El Recorte**, no este formato.

### 2. Guion (5–10 min)
Creá la carpeta del día: `episodios/AAAA-MM-DD-slug/`.
En Claude Code pegá `prompts/01_guion_short.md` + la nota/link/apuntes.
**Vos** revisás: sacás todo `[VERIFICAR]` que no pudiste confirmar, ajustás a tu forma de hablar.
Guardá el guion final como `guion.md` en la carpeta del día.

### 3. Grabar la voz (5 min)
Una o dos tomas. 45–75 s. Guardala como `voz.mp3` (o .wav/.m4a) en la carpeta del día.
Tip: leé con ritmo de noticiero, frases cortas → más cambios de imagen → más retención.

### 4. Transcribir con marcas (2 min)
TurboScribe → *Transcribe files* → subí `voz.mp3` → exportá **SRT** → guardalo como `voz.srt`.
Después, en Claude Code (o terminal):
```
python3 scripts/srt_a_marcas.py episodios/<carpeta>/voz.srt > episodios/<carpeta>/marcas.txt
```
Eso te deja una lista `[0.00] frase...` con una marca cada ~2 segundos.

### 5. Generar imágenes (~10 min)
En Claude Code pegá `prompts/02_imagenes.md` + el contenido de `marcas.txt`.
Aceptá los permisos de terminal. Claude genera, descarga y renombra (`0.00.png`, `2.40.png`...)
en `episodios/<carpeta>/imagenes/`. Mientras tanto, pasá al paso 8 (textos de publicación).

### 6. Revisar imágenes (3–5 min) — **no saltear**
Mirá la carpeta. Rehacé (pedíselo a Claude por número de marca) cualquier imagen que:
- muestre a una persona real de forma que sugiera algo no confirmado,
- tenga texto mal escrito o un dato equivocado,
- no tenga nada que ver con la frase.

### 7. Armar el video (1 min)
```
python3 scripts/armar_video.py \
  --audio episodios/<carpeta>/voz.mp3 \
  --imagenes episodios/<carpeta>/imagenes \
  --subs episodios/<carpeta>/voz.srt \
  --salida episodios/<carpeta>/short.mp4
```
Sale un MP4 vertical 1080×1920 con cada imagen en su segundo exacto y subtítulos quemados.
(Si querés retocar algo o agregar música, importá el MP4 en CapCut; ya viene sincronizado.)
Para el video largo: agregá `--formato horizontal`.

### 8. Publicar y reciclar (5 min)
Pegá `prompts/03_publicacion.md` + el guion → títulos, descripción, texto de Reel y post de X.
Un mismo short rinde en: **YouTube Shorts** (Jordy) + **Reel IG** (Jordy o collab con El Hit si
es noticia de interés general) + **X** de El Hit con el dato. Adaptar no es duplicar.

---

## Ritmo semanal (encaja con el piloto Estrategia 2026)

| Día | Qué |
|-----|-----|
| Lun–Vie | 1 short de noticia del día |
| Sáb | Opcional: short "lo que pasó en la semana" (3 noticias, 60 s) reusando imágenes |
| Dom (semanas pares) | **Video largo** de YouTube con este mismo método en 16:9: el guion es la investigación; las imágenes cambian cada 3–5 s. Acá es donde está la plata de YouTube. |

Anotá en la base **Producción — Estrategia 2026** de Notion cada short publicado, así entra
en las revisiones quincenales (4/10, 18/10, 1/11).

---

## Expectativas realistas

- Los **$61.000/mes** del video son una estimación de vidIQ sobre **videos largos** en inglés
  con 7M de vistas. Los Shorts pagan mucho menos por vista (centavos cada mil). Los shorts
  sirven para **crecer y traer suscriptores**; la monetización fuerte llega con el video largo,
  sponsors y reutilización en IG.
- Lo que sí es copiable: el **ritmo visual** (imagen nueva cada 2–3 s), el **estilo reconocible**
  y la **velocidad de producción**.
- Tu ventaja sobre un canal sin rostro: credibilidad. No la gastes en un título falso.

## Cuándo no publicar
Si en el paso 1 ninguna noticia pasa el filtro, no hay short ese día. Mejor 5 buenos por semana
que 7 flojos: el piloto dice "constancia antes que reinvención", no "volumen antes que criterio".
