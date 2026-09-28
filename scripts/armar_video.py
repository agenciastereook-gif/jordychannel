#!/usr/bin/env python3
"""Arma un video a partir de una voz en off y una carpeta de imágenes y/o videos
nombrados por su marca de tiempo (en segundos).

Cada archivo queda en pantalla desde su marca hasta la marca del siguiente;
el último dura hasta el final del audio. Se pueden mezclar fotos reales, imágenes
y videos en la misma carpeta. Los videos van sin su audio (manda la voz en off)
y si son más cortos que su tramo, se repiten.

Nombres válidos (png/jpg/webp · mp4/mov/webm/m4v):
    0.00.png   7.png   15.5.jpg   22.mp4   -> segundos
    00-07.png  01-15.50.mov                -> minutos-segundos

Uso:
    python3 scripts/armar_video.py --audio voz.mp3 --imagenes imgs/ --salida short.mp4
    python3 scripts/armar_video.py ... --formato horizontal   # video largo 16:9
    python3 scripts/armar_video.py ... --subs voz.srt         # subtítulos quemados
    python3 scripts/armar_video.py ... --fondo white          # relleno blanco en vez de desenfocado

Clip vertical de un tramo del video largo (reusa los mismos archivos y el audio):
    python3 scripts/armar_video.py --audio voz.mp3 --imagenes imgs/ --subs voz.srt \\
        --desde 02-10 --hasta 03-05 --salida clip1.mp4
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

IMAGENES = {".png", ".jpg", ".jpeg", ".webp"}
VIDEOS = {".mp4", ".mov", ".webm", ".m4v"}
FORMATOS = {"vertical": (1080, 1920), "horizontal": (1920, 1080)}
FPS = 30
MAX_VIDEO = 5.0  # segundos seguidos de un mismo video antes de un microcorte
SALTO = 0.5      # cuánto del video se saltea en cada microcorte
SRT_TIEMPO = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")


def ffmpeg_bin():
    """Un ffmpeg que pueda usar la placa NVIDIA (mucho más rápido); si ninguno puede, el primero que haya."""
    global X264
    candidatos = [shutil.which("ffmpeg")]
    try:
        import imageio_ffmpeg
        candidatos.append(imageio_ffmpeg.get_ffmpeg_exe())
    except ImportError:
        pass
    for ff in filter(None, candidatos):
        r = subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=s=256x256:d=0.2",
                            "-c:v", "h264_nvenc", "-f", "null", "-"], capture_output=True)
        if r.returncode == 0:
            X264 = ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "{crf}"]
            return ff
    return ffmpeg_bin_cpu()


X264 = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "{crf}"]


def codec(crf):
    return [x.replace("{crf}", str(crf)) for x in X264]


def ffmpeg_bin_cpu():
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("No encontré ffmpeg. Instalalo (brew install ffmpeg / winget install ffmpeg) "
                 "o corré: pip install imageio-ffmpeg")


def marca_de_nombre(nombre):
    """'7.50' -> 7.5 ; '01-15.50' -> 75.5 ; None si no es una marca."""
    m = re.fullmatch(r"(\d+)-(\d+(?:\.\d+)?)", nombre)
    if m:
        return int(m.group(1)) * 60 + float(m.group(2))
    m = re.fullmatch(r"\d+(?:\.\d+)?", nombre)
    return float(nombre) if m else None


def fmt_srt(s):
    ms = round(s * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def recortar_srt(origen, desde, hasta):
    """Devuelve la ruta de un .srt temporal con solo el tramo [desde, hasta], corrido a 0."""
    salida, n = [], 0
    for bloque in re.split(r"\n\s*\n", origen.read_text(encoding="utf-8-sig").strip()):
        lineas = bloque.strip().splitlines()
        for i, l in enumerate(lineas):
            m = SRT_TIEMPO.search(l)
            if not m:
                continue
            g = [int(x) for x in m.groups()]
            ini = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
            fin = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
            if fin > desde and ini < hasta:
                n += 1
                salida.append(f"{n}\n{fmt_srt(max(ini, desde) - desde)} --> "
                              f"{fmt_srt(min(fin, hasta) - desde)}\n" + "\n".join(lineas[i + 1:]))
            break
    tmp = tempfile.NamedTemporaryFile("w", suffix=".srt", delete=False, encoding="utf-8")
    tmp.write("\n\n".join(salida) + "\n")
    tmp.close()
    return Path(tmp.name)


def duracion(ffmpeg, archivo):
    salida = subprocess.run([ffmpeg, "-i", str(archivo)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", salida)
    if not m:
        sys.exit(f"No pude leer la duración de {archivo}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def filtro_encuadre(ancho, alto, fondo, k=""):
    """Encaja cualquier imagen/video en el cuadro: fondo desenfocado o color liso.
    k distingue las etiquetas internas cuando van muchos tramos en el mismo grafo."""
    fin = f"setsar=1,fps={FPS},format=yuv420p"
    if fondo == "blur":
        return (f"split[a{k}][b{k}];"
                f"[a{k}]scale={ancho // 8}:{alto // 8}:force_original_aspect_ratio=increase,crop={ancho // 8}:{alto // 8},"
                f"boxblur=4:2,scale={ancho}:{alto}[bg{k}];"  # desenfoque en chico: mismo efecto, mucho más rápido
                f"[b{k}]scale={ancho}:{alto}:force_original_aspect_ratio=decrease[fg{k}];"
                f"[bg{k}][fg{k}]overlay=(W-w)/2:(H-h)/2,{fin}")
    return (f"scale={ancho}:{alto}:force_original_aspect_ratio=decrease,"
            f"pad={ancho}:{alto}:(ow-iw)/2:(oh-ih)/2:color={fondo},{fin}")


MOVIMIENTOS = ["zoom_in", "pan_der", "zoom_out", "pan_izq", "pan_arriba", "pan_abajo"]
ZOOM = 0.12  # cuánto se acerca/desplaza en todo el tramo


def movimiento(mov, dur, ancho, alto):
    """Movimiento de cámara (Ken Burns) sobre el cuadro ya encuadrado, para que ninguna foto quede quieta."""
    d = max(0.5, dur)
    if mov in ("zoom_in", "zoom_out"):
        z = f"(1+{ZOOM}*t/{d:.3f})" if mov == "zoom_in" else f"(1+{ZOOM}-{ZOOM}*t/{d:.3f})"
        return (f",scale=w='trunc({ancho}*{z}/2)*2':h='trunc({alto}*{z}/2)*2':eval=frame:flags=bicubic,"
                f"crop={ancho}:{alto},setsar=1")
    if mov and mov.startswith("pan_"):
        p = f"t/{d:.3f}"
        x = {"pan_der": f"(iw-ow)*{p}", "pan_izq": f"(iw-ow)*(1-{p})"}.get(mov, "(iw-ow)/2")
        y = {"pan_abajo": f"(ih-oh)*{p}", "pan_arriba": f"(ih-oh)*(1-{p})"}.get(mov, "(ih-oh)/2")
        return (f",scale={int(ancho * (1 + ZOOM)) // 2 * 2}:{int(alto * (1 + ZOOM)) // 2 * 2},"
                f"crop={ancho}:{alto}:x='{x}':y='{y}',setsar=1")
    return ""


def filtro_de(archivo, encuadres, ancho, alto, fondo, k="", dur=0):
    """Encuadre + movimiento. Las fotos siempre se mueven (el movimiento de encuadre.json o uno alternado);
    los videos ya tienen el suyo."""
    e = encuadres.get(archivo.name, {})
    base = encuadre_de(e, ancho, alto, fondo, k)
    if archivo.suffix.lower() in VIDEOS:
        return base
    mov = e.get("mov") or MOVIMIENTOS[int(k or 0) % len(MOVIMIENTOS)]
    return base + movimiento(mov, dur, ancho, alto)


def encuadre_de(e, ancho, alto, fondo, k=""):
    """Encuadre según encuadre.json (lo arma el editor de Estudio):
    blur (fondo desenfocado), centrado (fondo liso) o recorte (x, y, w, h en fracciones del original)."""
    modo = e.get("modo") or ("recorte" if fondo == "blur" else "centrado")  # Jordy prefiere pantalla completa
    c = e.get("crop")
    if modo == "recorte" and c:
        return (f"crop=iw*{c['w']:.4f}:ih*{c['h']:.4f}:iw*{c['x']:.4f}:ih*{c['y']:.4f},"
                f"scale={ancho}:{alto},setsar=1,fps={FPS},format=yuv420p")
    if modo == "recorte":  # sin recuadro elegido: llena la pantalla, centrado
        return (f"scale={ancho}:{alto}:force_original_aspect_ratio=increase,crop={ancho}:{alto},"
                f"setsar=1,fps={FPS},format=yuv420p")
    return filtro_encuadre(ancho, alto, "blur" if modo == "blur" else ("black" if fondo == "blur" else fondo), k)


def entrada_tramo(ffmpeg, archivo, dur, offset):
    """Argumentos de entrada de un tramo: el archivo, desde su offset, durante `dur` segundos."""
    if archivo.suffix.lower() in VIDEOS:
        largo = duracion(ffmpeg, archivo)
        entrada = ["-ss", f"{offset % largo:.3f}"] if offset else []
        entrada += ["-stream_loop", "-1"]
    else:
        entrada = ["-loop", "1", "-framerate", str(FPS)]
    return entrada + ["-t", f"{dur:.3f}", "-i", str(archivo)]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--audio", required=True, type=Path)
    p.add_argument("--imagenes", required=True, type=Path, help="carpeta con imágenes y/o videos")
    p.add_argument("--salida", required=True, type=Path)
    p.add_argument("--formato", choices=FORMATOS, default="vertical")
    p.add_argument("--subs", type=Path, help="archivo .srt para quemar subtítulos")
    p.add_argument("--fondo", default="blur",
                   help="relleno cuando el archivo no tiene la proporción del video: "
                        "blur (desenfocado, default) o un color (white, black...)")
    p.add_argument("--desde", help="inicio del tramo (segundos o MM-SS) para sacar un clip")
    p.add_argument("--hasta", help="fin del tramo (segundos o MM-SS)")
    a = p.parse_args()

    ffmpeg = ffmpeg_bin()
    medios = []
    for f in a.imagenes.iterdir():
        if f.suffix.lower() in IMAGENES | VIDEOS:
            t = marca_de_nombre(f.stem)
            if t is None:
                print(f"  (ignoro {f.name}: el nombre no es una marca de tiempo)")
            else:
                medios.append((t, f.resolve()))
    if not medios:
        sys.exit("No hay imágenes ni videos con nombre de marca de tiempo en la carpeta.")
    medios.sort()

    total_audio = duracion(ffmpeg, a.audio)
    desde = marca_de_nombre(a.desde) if a.desde else 0.0
    hasta = marca_de_nombre(a.hasta) if a.hasta else total_audio
    if desde is None or hasta is None or not 0 <= desde < hasta:
        sys.exit("--desde/--hasta inválidos (usá segundos como 130 o minutos-segundos como 02-10).")
    hasta = min(hasta, total_audio)
    if a.subs and (a.desde or a.hasta):
        a.subs = recortar_srt(a.subs, desde, hasta)

    # Tramos (archivo, inicio, fin, offset) dentro de [desde, hasta];
    # offset = cuánto del archivo ya pasó (para arrancar un video a mitad en un clip)
    tramos = []
    for i, (t, f) in enumerate(medios):
        fin = medios[i + 1][0] if i + 1 < len(medios) else hasta
        ini, fin = max(t, desde), min(fin, hasta)
        if fin > ini:
            tramos.append((f, ini, fin, ini - t))
    if not tramos:
        sys.exit("No hay archivos en ese tramo.")
    if tramos[0][1] > desde:
        f, ini, fin, off = tramos[0]
        print(f"  Aviso: el primer archivo arranca en {ini:.2f}s; lo estiro hasta el comienzo.")
        tramos[0] = (f, desde, fin, off)

    # Un video ajeno no queda más de MAX_VIDEO segundos seguidos: microcorte (salta SALTO segundos)
    cortados = []
    for f, ini, fin, off in tramos:
        k = 0
        while f.suffix.lower() in VIDEOS and fin - ini > MAX_VIDEO:
            cortados.append((f, ini, ini + MAX_VIDEO, off + k * SALTO))
            ini, off, k = ini + MAX_VIDEO, off + MAX_VIDEO, k + 1
        cortados.append((f, ini, fin, off + k * SALTO))
    tramos = cortados

    ancho, alto = FORMATOS[a.formato]
    encuadre = a.imagenes / "encuadre.json"
    encuadres = json.loads(encuadre.read_text(encoding="utf-8")) if encuadre.exists() else {}
    total = hasta - desde
    n_vid = sum(1 for f, *_ in tramos if f.suffix.lower() in VIDEOS)
    print(f"Armando {a.salida} ({a.formato}, {len(tramos)} tramos, {n_vid} videos, {total:.1f}s)...")

    # Como El Recorte: una sola pasada de ffmpeg. Todos los tramos entran juntos, se encuadran,
    # se unen (concat) y reciben las capas encima; se comprime una sola vez.
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cmd, grafo = [ffmpeg, "-y"], []
        for i, (f, ini, fin, off) in enumerate(tramos):
            cmd += entrada_tramo(ffmpeg, f, fin - ini, off)
            grafo.append(f"[{i}:v]{filtro_de(f, encuadres, ancho, alto, a.fondo, i, fin - ini)}[t{i}]")
        grafo.append("".join(f"[t{i}]" for i in range(len(tramos))) + f"concat=n={len(tramos)}:v=1:a=0[base]")
        voz = len(tramos)
        cmd += ["-ss", f"{desde:.3f}", "-t", f"{total:.3f}", "-i", str(a.audio)]
        # Capas extra del editor de Estudio (solo en el video completo, no en clips de un tramo):
        # videos/fotos encima, textos (PNG ya dibujados) y audios mezclados con la voz.
        capas_json = a.imagenes / "capas.json"
        capas = {} if (a.desde or a.hasta) or not capas_json.exists() else \
            json.loads(capas_json.read_text(encoding="utf-8"))
        v, entrada = "[base]", voz + 1
        for k, c in enumerate(capas.get("videos", []) + capas.get("textos", [])):
            dur = max(0.1, c["fin"] - c["ini"])
            es_video = Path(c["archivo"]).suffix.lower() in VIDEOS
            cmd += (["-stream_loop", "-1"] if es_video else ["-loop", "1", "-framerate", str(FPS)]) + \
                ["-t", f"{dur:.3f}", "-i", c["archivo"]]
            w, h = int(c.get("w", 1) * ancho) // 2 * 2, int(c.get("h", 1) * alto) // 2 * 2
            grafo.append(f"[{entrada}:v]scale={w}:{h},setsar=1,format=rgba,"
                         f"setpts=PTS-STARTPTS+{c['ini']:.3f}/TB[c{k}]")
            grafo.append(f"{v}[c{k}]overlay={int(c.get('x', 0) * ancho)}:{int(c.get('y', 0) * alto)}:"
                         f"eof_action=pass:enable='between(t,{c['ini']:.3f},{c['fin']:.3f})'[v{k}]")
            v, entrada = f"[v{k}]", entrada + 1
        if a.subs:
            srt = str(a.subs.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
            grafo.append(f"{v}subtitles='{srt}':force_style='Fontsize=14,Bold=1,Outline=2,"
                         f"MarginV={'60' if a.formato == 'vertical' else '30'}'[vs]")
            v = "[vs]"
        mezcla = [f"[{voz}:a]"]
        for k, c in enumerate(capas.get("audios", [])):
            cmd += ["-i", c["archivo"]]
            ms = int(c["ini"] * 1000)
            recorte = f"atrim=0:{c['fin'] - c['ini']:.3f}," if c.get("fin") else ""
            grafo.append(f"[{entrada}:a]{recorte}adelay={ms}|{ms},volume={c.get('vol', 1):.2f}[a{k}]")
            mezcla.append(f"[a{k}]")
            entrada += 1
        a_salida = f"{voz}:a"
        if len(mezcla) > 1:
            grafo.append("".join(mezcla) + f"amix=inputs={len(mezcla)}:duration=first:normalize=0[am]")
            a_salida = "[am]"
        guion_ff = tmp / "grafo.txt"  # en archivo: con muchos tramos no entra en la línea de comandos
        guion_ff.write_text(";\n".join(grafo), encoding="utf-8")
        cmd += ["-/filter_complex", str(guion_ff), "-map", v, "-map", a_salida, *codec(20), "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(a.salida)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-2000:])
            if a.subs and "subtitles" in r.stderr:
                print("\nTu ffmpeg no soporta subtítulos quemados; probá sin --subs o instalá ffmpeg completo.")
            sys.exit(1)
    if a.subs and (a.desde or a.hasta):
        a.subs.unlink(missing_ok=True)  # srt temporal del recorte
    print("Listo.")


if __name__ == "__main__":
    main()
