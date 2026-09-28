# Jordy en Vivo · Identidad visual para video

Versión 1.0 · 28 de septiembre de 2026

Kit basado en las seis referencias aportadas: tipografía condensada de gran tamaño, negro y papel, campos de color, barras rectas y la firma **JORDY / EN VIVO / punto rojo**. Las medidas están adaptadas a video 9:16 y 16:9; no son un recorte de las referencias.

**Entrada para aplicar por código:** `identidad.json`. Contiene colores, archivos de fuentes, posiciones, cajas de texto, tamaños, opacidades, orden de capas y animaciones. **Este kit está preparado para integrar; todavía no está conectado al armado de videos de Estudio.**

## 1. Paleta

Los valores HEX siguientes son la paleta normalizada de esta identidad, no una medición exacta de las imágenes originales. Opacidad y textura se aplican por separado del color.

| Nombre / clave | HEX | Uso |
|---|---|---|
| Negro / `negro` | **#101010** | Fondos de zócalos, subtítulos y créditos; texto sobre papel o amarillo. |
| Papel / `papel` | **#F4F0E6** | Texto sobre negro o azul; fondo de cita; logo claro y subtítulos. |
| Amarillo / `amarillo` | **#FFE000** | Barra del zócalo y acentos editoriales. En un fondo amarillo, el texto es negro. |
| Azul / `azul` | **#0047FF** | Fondo de la placa de dato, siempre con texto papel. |
| Rojo / `rojo` | **#FF2A23** | Punto del logo y barra de cita. Se usa como marca gráfica, sin texto pequeño encima. |

Los cinco colores son suficientes para este sistema. Negro/papel resuelven la lectura; amarillo/azul organizan las piezas; rojo identifica la marca. Esquinas rectas, sin degradados ni sombras en las placas.

La textura de impresión de las referencias queda como opción: grano monocromo **estático**, de 1–2 px a resolución base, con opacidad máxima **3%**, solamente sobre fondos de placa. La versión predeterminada entregada es limpia. No perforar letras, números, logo ni subtítulos con textura.

## 2. Tipografías gratuitas

| Uso | Familia exacta | Estilo / peso | Archivo incluido |
|---|---|---|---|
| Títulos, nombres del zócalo, cifras, citas y palabra JORDY | **Anton** | **Regular · 400** | `fuentes/Anton.ttf` |
| Cargo, explicación y fuentes/créditos | **IBM Plex Sans** | **Regular · 400** | `fuentes/IBMPlexSans-Regular.ttf` |
| Subtítulos, etiquetas, autor de la cita y EN VIVO | **IBM Plex Sans** | **SemiBold · 600** | `fuentes/IBMPlexSans-SemiBold.ttf` |

Son dos familias. Anton ya tiene una forma muy pesada en su peso Regular: no aplicar negrita artificial. Interletrado **0 px** en todas las piezas. Títulos y nombres del zócalo en mayúsculas; cargos y subtítulos con mayúsculas/minúsculas normales. Las citas conservan la escritura original.

Fuentes oficiales: [Anton en Google Fonts](https://fonts.google.com/specimen/Anton) · [IBM Plex Sans en Google Fonts](https://fonts.google.com/specimen/IBM+Plex+Sans). Las dos familias usan SIL Open Font License 1.1; se incluyen las licencias y los archivos locales. No hace falta una suscripción ni descargar las fuentes en cada render.

## 3. Logos entregados

| Archivo en `logos/` | Tamaño | Uso |
|---|---|---|
| `logo-claro-2400.png` | 2400 × 480 px | Firma completa en papel y rojo, sobre fondo oscuro/azul. |
| `logo-oscuro-2400.png` | 2400 × 480 px | Firma completa en negro y rojo, sobre fondo papel/amarillo. |
| `marca-agua-claro-480.png` | 480 × 160 px | Matriz de la marca reducida JORDY + punto rojo, para fondos oscuros. |
| `marca-agua-oscuro-480.png` | 480 × 160 px | Matriz equivalente para fondos claros. |
| `marca-agua-clara-168.png` | 168 × 56 px | Tamaño de aplicación en los dos formatos base. |
| `marca-agua-oscura-168.png` | 168 × 56 px | Tamaño de aplicación sobre fondos claros uniformes. |

**Todos son PNG RGBA con transparencia real.** El fondo negro de protección de la marca de agua es una capa independiente, no está incorporado al archivo. La firma completa conserva “EN VIVO”; la versión chica usa JORDY + punto para mantener legibilidad.

Mantener la proporción: firma completa **5:1**, marca reducida **3:1**. Ancho mínimo recomendado de la firma completa: **360 px** a resolución base; de la marca reducida: **144 px**. Alrededor de la firma completa, dejar espacio libre igual al **25% de su alto**. La marca de agua tiene su propia caja de protección definida abajo. El punto rojo queda fijo, sin parpadeo.

## 4. Coordenadas y escala

| Parámetro | Vertical | Horizontal |
|---|---|---|
| Lienzo | **1080 × 1920** | **1920 × 1080** |
| Relación | 9:16 | 16:9 |
| Zona de contenido legible `x, y, ancho, alto` | **72, 144, 852, 1440** | **96, 54, 1728, 972** |
| Márgenes de contenido: izquierda / arriba / derecha / abajo | **72 / 144 / 156 / 336 px** | **96 / 54 / 96 / 54 px** |

Estas zonas son una decisión de diseño para dejar aire a las interfaces de reproducción, especialmente a la derecha y abajo del vertical. No representan una garantía universal sobre la interfaz de cada red social. Los fondos pueden ocupar toda la pantalla; los 8 px de protección de la marca de agua pueden sobresalir de la zona de texto.

En todas las tablas, `x,y` parten de la **esquina superior izquierda**. `w,h` significan ancho y alto. Los valores son píxeles del lienzo base. Las cajas de texto se miden desde la esquina superior izquierda de la **tinta visible**; el tamaño de fuente es el tamaño em en píxeles, no la altura exacta de las letras. Si el motor trabaja por línea base, compensar con el bounding box de la fuente incluida.

Para otra resolución de la misma proporción: multiplicar **todas** las medidas, tamaños de fuente, bordes y desplazamientos por `ancho_salida / ancho_base`. Redondear al entero más cercano, con .5 hacia arriba. Por ejemplo, vertical 720 × 1280: factor 2/3; horizontal 3840 × 2160: factor 2. Los tiempos no se escalan. Usar el diseño del formato correspondiente, sin estirarlo ni convertirlo mediante recorte.

## 5. Las seis piezas

### Zócalo: nombre y cargo

| Elemento | 9:16 · x,y,w,h | 16:9 · x,y,w,h | Estilo |
|---|---|---|---|
| Caja de fondo | 72,1160,852,160 | 96,688,960,136 | Negro al **94%**, sin borde. |
| Barra izquierda | 72,1160,8,160 | 96,688,8,136 | Amarillo al 100%. |
| Nombre | 104,1182,788,60 | 128,710,896,52 | Anton 400, papel. **52 / 44 px**, mínimo **42 / 36 px**, una línea. |
| Cargo | 104,1256,788,40 | 128,768,896,40 | IBM Plex Sans 400, papel. **30 / 28 px**, una línea. |

Texto alineado a la izquierda. Margen interior horizontal **32 px**; el nombre empieza **22 px** por debajo del borde. Mantener el zócalo **4 s** una vez que terminó de entrar; puede prolongarse hasta 6 s para identificación más larga. Mostrarlo en la primera aparición de la persona y repetirlo solo si vuelve después de otra secuencia.

### Placa de dato

Fondo **azul a pantalla completa**; texto **papel**. El dato es el protagonista. Cifra, unidad/período, explicación y fuente son campos distintos. La marca de agua se superpone en su posición habitual.

| Elemento | 9:16 · x,y,w,h | 16:9 · x,y,w,h | Tipografía / tamaño |
|---|---|---|---|
| Etiqueta “LA CIFRA” | 72,432,852,44 | 96,250,800,44 | IBM Plex Sans 600 · **30 px**. |
| Barra papel | 72,500,96,10 | 96,318,96,10 | Rectángulo opaco. |
| Cifra | 72,550,852,336 | 96,382,816,250 | Anton 400 · **312 / 212 px**, mínimos **176 / 144 px**; una línea. |
| Unidad / período | 72,922,852,68 | 96,660,816,60 | IBM Plex Sans 600 · **44 / 36 px**; una línea. |
| Explicación | 72,1024,852,126 | 1040,388,784,174 | IBM Plex Sans 400 · **42 / 44 px**; interlínea **54 / 56 px**; máximo **2 / 3 líneas**. |
| Fuente y fecha | 72,1200,852,84 | 1040,610,784,80 | IBM Plex Sans 400 · **26 px**, interlínea **34 px**; máximo dos líneas. |
| Separador entre columnas | No lleva | 960,382,4,300 | Papel al **65%**. |

Margen izquierdo **72 / 96 px**. El horizontal separa cifra y contexto en dos columnas; el vertical los apila. Escribir la unidad completa en su campo si se abrevia el número. No redondear, convertir ni abreviar una cifra automáticamente sin autorización editorial. Fuente y fecha obligatorias.

Tiempo de lectura completamente visible: **4 s como mínimo**, o `máx(4, cantidad_de_palabras_visibles / 3)` segundos si hay más explicación. No animar una cuenta ascendente: el dato aparece directamente con su valor real.

### Placa de cita

Fondo **papel a pantalla completa**, texto **negro**, barra **roja**. Frase entre comillas angulares; la atribución tiene su propio bloque. Conservar las palabras y la puntuación originales.

| Elemento | 9:16 · x,y,w,h | 16:9 · x,y,w,h | Tipografía / tamaño |
|---|---|---|---|
| Etiqueta “CITA” | 72,376,852,44 | 96,218,1728,44 | IBM Plex Sans 600 · **30 px**. |
| Barra roja | 72,450,96,10 | 96,290,96,10 | Opaca. |
| Frase textual | 72,530,852,500 | 300,310,1524,310 | Anton 400 · **112 / 104 px**, mínimos **88 / 84 px**; interlínea **128 / 120 px**; máximo **4 / 2 líneas**. |
| Autor | 72,1080,852,58 | 300,658,1524,58 | IBM Plex Sans 600 · **38 / 40 px**; una línea. |
| Cargo | 72,1152,852,84 | 300,726,1524,42 | IBM Plex Sans 400 · **30 / 28 px**; máximo **2 / 1 líneas**; interlínea vertical **40 px**. |
| Fuente y fecha | 72,1256,852,76 | 300,788,1524,40 | IBM Plex Sans 400 · **26 / 24 px**; máximo **2 / 1 líneas**; interlínea vertical **34 px**. |

Todo a la izquierda. En horizontal la cita y la atribución empiezan a **300 px**, separadas de la etiqueta por un retiro de **204 px**. En vertical comparten el margen de **72 px**. No colocar un zócalo sobre esta placa.

Tiempo de lectura completamente visible: `máx(6, cantidad_de_palabras_de_cita_y_atribución / 3)` segundos. Si la cita no entra al tamaño mínimo, dividirla en placas consecutivas sin omitir palabras o pedir un extracto editorialmente autorizado. No resumir una frase presentada como textual.

### Crédito de imagen

| Elemento | 9:16 · x,y,w,h | 16:9 · x,y,w,h | Estilo |
|---|---|---|---|
| Fondo | 72,1352,660,44 | 96,610,720,44 | Negro al **92%**, rectangular. |
| Texto | 88,1358,628,32 | 112,616,688,32 | IBM Plex Sans **Regular 400, 24 px**, papel; una línea. |

Contenido: `Imagen: Autor / medio`. Relleno interior **16 px** a cada lado y **6 px** arriba. Queda entre zócalo y subtítulos en vertical, y por encima del zócalo en horizontal. Mostrarlo durante todo el material al que corresponde. Si cambia el autor, cambiar el crédito con el corte. Con el mismo autor no reiniciar la animación. Conservar la atribución necesaria; si no entra, resolver el texto antes de exportar. En placas de dato/cita se usa el campo “Fuente”, sin duplicar este crédito.

### Subtítulos

| Elemento | 9:16 · x,y,w,h | 16:9 · x,y,w,h | Estilo |
|---|---|---|---|
| Fondo | 72,1424,852,144 | 360,866,1200,128 | Negro al **92%**, sin borde ni sombra. |
| Caja de texto | 96,1440,804,112 | 384,882,1152,96 | IBM Plex Sans **SemiBold 600**, papel. |
| Tamaño / interlínea | **46 / 56 px** | **40 / 48 px** | Máximo **dos líneas**, centradas dentro de la caja. |

Relleno interior horizontal **24 px** y vertical **16 px**. El bloque tiene tamaño fijo para que no salte al variar el largo de la frase. Una sola línea ocupa la primera línea del bloque. Si no hay voz subtitulada, desaparece el bloque completo.

Cortar por grupos de sentido, sin partir palabras. Sin letra a letra, rebote ni resaltado que se mueva. El texto cambia directamente al inicio de cada tramo de voz. No achicar la fuente: repartir un texto largo en más tramos sincronizados con la voz. Los subtítulos pueden coexistir con cualquiera de las otras piezas: su franja queda reservada también en las placas.

### Marca de agua

| Elemento | 9:16 · x,y,w,h | 16:9 · x,y,w,h | Estilo |
|---|---|---|---|
| Protección | 64,148,184,72 | 88,46,184,72 | Negro al **80%**, rectangular. |
| PNG | 72,156,168,56 | 96,54,168,56 | `marca-agua-clara-168.png`, al **100%**. |

Posición: **arriba a la izquierda**. Protección exterior de **8 px**. La combinación clara + protección negra es la opción predeterminada en todas las escenas. La variante oscura queda disponible para aplicaciones sobre fondos claros uniformes sin caja; no alternar versiones según cada fotograma. Mantener la marca durante todo el video, sin reiniciarla en cada corte.

## 6. Movimiento y transiciones

Los tiempos de permanencia anteriores excluyen entrada y salida. Todos los elementos de una misma pieza se animan como un solo grupo. Los fondos a pantalla completa de dato/cita aparecen mediante corte; se anima su contenido. La marca de agua y los subtítulos son capas independientes.

| Pieza | Entrada | Salida |
|---|---|---|
| Zócalo | **0,30 s**: de x−64 px a x final; opacidad 0→100%. | **0,20 s**: x final a x−32 px; opacidad 100→0%. |
| Dato | **0,24 s**: de y+24 px a y final; opacidad 0→100%. | **0,16 s**: fundido a 0%, sin desplazamiento. |
| Cita | **0,28 s**: de y+24 px a y final; opacidad 0→100%. | **0,20 s**: fundido a 0%, sin desplazamiento. |
| Crédito | **0,16 s**: fundido de 0 a 100%. | **0,12 s**: fundido de 100 a 0%. |
| Subtítulos | **0 s**: cambio directo, sincronizado con la voz. | **0 s**: cambio directo al terminar el tramo. |
| Marca de agua | **0,24 s**: fundido al empezar el video. | **0,16 s**: fundido al terminar el video. |

Curvas: entrada `easeOutCubic = 1 − (1 − t)³`; salida `easeInCubic = t³`, con `t` de 0 a 1. Sin rebote, giro, flash ni sonidos añadidos. Interpolar cada propiedad entre su valor inicial y final. Las opacidades de fondo indicadas son sus máximos: por ejemplo, durante una entrada al 50%, un fondo al 94% queda al 47%.

**Entre imágenes: corte directo, 0 s, como transición predeterminada.** Para dos fotografías de una misma secuencia se permite un fundido cruzado de **0,12 s**; no usarlo para ocultar un cambio de fuente o de persona. El fundido afecta solo al material visual, no a los subtítulos, marca o zócalo. Las fotos permanecen quietas salvo que la edición requiera un movimiento concreto. Ningún fragmento del mismo video debe superar **5 s continuos**, siguiendo la regla del proyecto.

Trabajar en segundos y ajustar a la tasa de cuadros del video: si el tiempo es 0, usar 0 cuadros; en otro caso, `máx(1, floor(segundos × fps + 0.5))`. A 30 fps, por ejemplo, 0,30 s = 9 cuadros; 0,12 s = 4 cuadros. No imponer otra tasa de cuadros para usar la identidad.

## 7. Reglas para automatizar

1. Elegir el formato; cargar colores y fuentes **incluidas**; escalar las medidas solo después.
2. La geometría exacta está en `formats.vertical.pieces` y `formats.horizontal.pieces`. Cada capa usa `box: [x,y,w,h]`. Los colores apuntan a `palette`; los estilos a `fonts`.
3. En cada capa de texto, reemplazar `sample` por el campo indicado en `content_key`. Las etiquetas fijas tienen `content_key: null`. Los ejemplos son maquetas, no información publicable. Rechazar corchetes de plantilla o campos obligatorios sin completar antes de exportar.
4. Medir con el archivo de fuente correcto. Respetar saltos de línea explícitos y envolver por palabras. Si una caja permite reducir tamaño, bajar de **2 en 2 px** hasta su mínimo; la interlínea baja en la misma proporción. No estirar letras ni truncar con puntos suspensivos.
5. Cuando no entra: detener esa pieza y solicitar texto más breve o dividirla. Cifras, citas, nombres y atribuciones no se reescriben automáticamente. Los subtítulos largos se segmentan por voz, sin cambiar sus tamaños.
6. Orden de capas sobre video: **material → crédito → zócalo → subtítulos → marca de agua**. Sobre placa: **fondo → contenido de dato o cita → subtítulos → marca de agua**. Dato, cita y zócalo son mutuamente excluyentes.
7. Conservar las franjas reservadas incluso cuando no haya subtítulos. No mover los componentes para llenar huecos.
8. Los tiempos base de `hold_s` son mínimos; aplicar las reglas de lectura del manual para textos largos. Crédito, subtítulos y marca duran lo que indiquen el material, la voz y el video, respectivamente.
9. PNG con alfa recta (RGBA), sRGB. Al componer, respetar el canal alfa; no convertir los huecos transparentes en negro. Las coordenadas del logo corresponden al lienzo PNG completo, incluido su pequeño margen transparente.

## 8. Archivos y comprobación

- `vista-general.jpg`: vista conjunta de los dos formatos.
- `muestras/vertical-video.png`, `vertical-dato.png`, `vertical-cita.png`: muestras **1080 × 1920**.
- `muestras/horizontal-video.png`, `horizontal-dato.png`, `horizontal-cita.png`: muestras **1920 × 1080**.
- `logos/`: seis PNG con transparencia, variantes clara y oscura.
- `fuentes/`: tres archivos TTF de las dos familias y sus licencias.
- `identidad.json`: especificación para la integración.
- `generar_kit.py`: generación reproducible con Python y Pillow; se ejecuta sin conexión. Incluye un control de tamaños, encaje de las muestras, separación de franjas y transparencia.

La cuadrícula y la palabra “VIDEO” de las muestras son un fondo neutro para mostrar las superposiciones. El sello “MAQUETA · CAMPOS SIN COMPLETAR” tampoco forma parte de la identidad de emisión. Las muestras de dato/cita no muestran subtítulos porque no tienen un tramo de voz asociado; las cajas correspondientes están definidas en el JSON.

Revisar cada exportación real con su contenido final: las comprobaciones de este kit verifican la geometría y las muestras, no la veracidad de los datos ni la legibilidad de cualquier texto posible.
