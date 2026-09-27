# Rutina — Jordy en Vivo · El Hit · El Recorte

Pensada para **una sola persona**. Regla de oro: **el piso es obligatorio, el ideal es opcional.**
Un día en que cumplís solo el piso es un día bien hecho. Esto es una guía, no una atadura:
si algo no sirve, se cambia.

---

## Qué hace cada marca (en una frase)

- **Jordy en Vivo** — autor: cuenta y explica la noticia con tu voz. Video corto diario + video largo semanal.
- **El Hit** — medio: elige la actualidad que merece atención. Placas, carruseles, breaking.
- **El Recorte** — distribución: el momento audiovisual, contextualizado. Clips.

## Piso e ideal

| | Piso | Ideal |
|---|---|---|
| **Short/Reel de la noticia del día** (lun–vie) | 1 | 1 |
| ↳ sale en | IG collab **El Hit + Jordy** · **YouTube Shorts** Jordy · dato a **X de El Hit** | igual |
| **El Hit — piezas extra** (placa, carrusel, breaking) | 1 por día | 2 por día |
| **El Recorte** | 1 clip por día | 2 por día |
| **Video largo** Jordy YouTube | 1 por semana | 1 por semana |
| **Clips del video largo** (finde, para stock) | 1 | 2 o más |

**Semana de emergencia** (enfermo, viaje, quemado): short solo 3 días, 1 Recorte y 1 Hit por día,
y se usa el stock. No se fabrica contenido para cumplir.

---

## El día (lun–vie) — unas 2 horas en 3 bloques

### Bloque 1 · Relevamiento (15 min, a la mañana)
Mirá la agenda y anotá en una lista:
- **La noticia del short** (Jordy + El Hit): la que más merece ser contada con voz.
- **1–2 noticias para El Hit** que no necesitan voz: una placa o un carrusel alcanzan.
- **1–2 momentos para El Recorte**: TV, radio, streaming, fútbol, entrevistas.

Filtro para la del short: ¿pasó hoy o ayer? ¿se cuenta en 60 segundos? ¿tengo fuente que nombrar?

### Bloque 2 · El short del día (40 min)
Es el método del video (voz propia + dibujos sincronizados). Carpeta: `episodios/AAAA-MM-DD-slug/`.

1. **Guion** — `prompts/01_guion_short.md` + la nota. Vos sacás los `[VERIFICAR]` y lo ajustás a tu forma de hablar.
2. **Voz** — grabás `voz.mp3` (45–75 s).
3. **Marcas** — TurboScribe → exportar SRT → `voz.srt`. Después:
   `python3 scripts/srt_a_marcas.py episodios/<carpeta>/voz.srt > episodios/<carpeta>/marcas.txt`
4. **Imágenes** — elegí según la noticia (ver "Fotos reales, dibujos o mezcla" abajo):
   - **Tus fotos y videos**: ponelos en `episodios/<carpeta>/material/` y usá `prompts/02b_material_propio.md`.
     Claude mira el material, asigna cada archivo a su frase y te muestra la lista para que la apruebes.
   - **Dibujos**: `prompts/02_imagenes.md` + `marcas.txt` (Higgsfield).
   - **Mezcla** (lo más común): 02b primero; las frases sin material quedan como `DIBUJO` y se generan solo esas.
   *Mientras se generan, avanzá con el bloque 3.*
5. **Revisión** — mirá la carpeta `imagenes/`; pedí rehacer lo que esté mal (por número de segundo).
6. **Armado** —
   `python3 scripts/armar_video.py --audio episodios/<carpeta>/voz.mp3 --imagenes episodios/<carpeta>/imagenes --subs episodios/<carpeta>/voz.srt --salida episodios/<carpeta>/short.mp4`
7. **Textos** — `prompts/03_publicacion.md` → caption de la collab, título de YouTube, post de X.

### Bloque 3 · El Hit + El Recorte (30–60 min)
- **El Hit**: `prompts/04_el_hit.md` → texto de la placa o del carrusel, con foto real. Si es
  **breaking**, sale en cuanto pasa, no espera al bloque.
- **El Recorte**: descargás el clip, lo cortás y usás `prompts/05_recorte.md` para el contexto.
  Si el clip también es noticia → collab con El Hit + mismo archivo al X de El Hit.

---

## La semana del video largo

El largo también usa el método de los dibujos, en 16:9. Así cuesta horas, no días.

| Día | Qué | Tiempo |
|---|---|---|
| Lun–Mié | Juntar material del tema de la semana (en ratos sueltos) | — |
| Jue | Guion con `prompts/06_video_largo.md` | 1–2 h |
| Vie | Grabar voz + TurboScribe + dibujos (en tandas) | 1–2 h |
| Sáb | Armar (`--formato horizontal`), miniatura, publicar | 1 h |
| Dom | Sacar 1–2 clips verticales para el stock (`prompts/07_clips.md`) | 30 min |

**Los clips salen sin editar nada:** usás los mismos dibujos y el mismo audio, cortando un tramo.
```
python3 scripts/armar_video.py --audio episodios/<largo>/voz.mp3 \
  --imagenes episodios/<largo>/imagenes --subs episodios/<largo>/voz.srt \
  --desde 02-10 --hasta 03-05 --salida episodios/<largo>/clip1.mp4
```
Salen en vertical, así que van directo a Reel/Short de Jordy (y collab con El Recorte si el valor es
un momento tuyo). El stock se usa los días flojos.

---

## Cómo rinde cada pieza (adaptar no es duplicar)

```
Short del día ──► IG collab El Hit + Jordy
               ├► YouTube Shorts (Jordy)
               └► X de El Hit (el dato)

Clip de El Recorte ──► IG El Recorte (collab con El Hit si es noticia)
                    └► X de El Hit (mismo archivo)

Video largo ──► YouTube Jordy
             └► 1–2 clips verticales ──► stock para Reels/Shorts de Jordy
```

## Fotos reales, dibujos o mezcla

El script acepta **dibujos, fotos y videos mezclados** en la misma carpeta. Si una foto o video no
tiene la proporción del video (ej. foto horizontal en un short vertical), la centra con el mismo
fondo desenfocado de los reels de noticias. Los videos van sin su audio (manda tu voz).

Regla práctica:
- **Personas reales → foto real.** No le pidas al dibujo que "se parezca" a alguien: la IA no lo
  logra bien, muchas herramientas lo bloquean y, si sale parecido a otra persona, es un error
  periodístico. La foto identifica; el dibujo explica.
- **Ideas, cifras, conceptos → dibujo.** "Prohibió las apuestas", "movían 3 mil millones",
  "los chicos con el celular": ahí el dibujo rinde más que cualquier foto de archivo.
- **Momentos → video.** La declaración, el acto, el gol: 2 a 4 segundos del video real.

**De dónde sacar fotos sin problemas:**
- Fotos oficiales de gobiernos y organismos (Casa Rosada, Planalto, Congreso), que suelen
  permitir uso con crédito. Ej.: la Agência Brasil publica con licencia libre citando autor.
- Wikimedia Commons (revisá la licencia de cada foto).
- Capturas de TV/streaming para comentar la noticia, con crédito del medio. Es lo habitual en el
  rubro, pero es zona gris: nunca uses una foto de agencia (Reuters, AFP, Getty) sin licencia.
- Poné el crédito en la descripción: "Fotos: Agência Brasil / Planalto".

**Estilo por marca:** el short y el largo de Jordy pueden llevar mezcla (foto + dibujo); El Hit y
El Recorte, siempre material real.

## Cada dos semanas (15 min)
Mirá qué funcionó (retención, seguidores ganados, qué noticias rindieron) y anotá una cosa para
sostener y una para cambiar. Nada más.

---

## Expectativas realistas
- Los $61.000/mes del video son una estimación sobre videos **largos** en inglés. Los Shorts
  pagan poco: sirven para crecer. La plata de YouTube está en el video largo; la del ecosistema,
  en sponsors e integraciones.
- Tu diferencial frente a los canales sin rostro es que un periodista firma la nota. No lo gastes
  en un título falso.
- YouTube no monetiza contenido masivo sin aporte propio: tu voz y tu criterio son lo que lo evita.
