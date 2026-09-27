#!/usr/bin/env python3
"""Arma un video a partir de una voz en off y una carpeta de imágenes y/o videos
nombrados por su marca de tiempo (en segundos).

Cada archivo queda en pantalla desde su marca hasta la marca del siguiente;
el último dura hasta el final del audio. Se pueden mezclar dibujos, fotos reales
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
SRT_TIEMPO = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")


def ffmpeg_bin():
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


def filtro_encuadre(ancho, alto, fondo):
    """Encaja cualquier imagen/video en el cuadro: fondo desenfocado o color liso."""
    fin = f"setsar=1,fps={FPS},format=yuv420p"
    if fondo == "blur":
        return (f"split[a][b];"
                f"[a]scale={ancho}:{alto}:force_original_aspect_ratio=increase,crop={ancho}:{alto},"
                f"boxblur=30:3[bg];"
                f"[b]scale={ancho}:{alto}:force_original_aspect_ratio=decrease[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2,{fin}")
    return (f"scale={ancho}:{alto}:force_original_aspect_ratio=decrease,"
            f"pad={ancho}:{alto}:(ow-iw)/2:(oh-ih)/2:color={fondo},{fin}")


def render_tramo(ffmpeg, archivo, dur, offset, salida, vf):
    """Renderiza un tramo mudo de `dur` segundos con un solo archivo."""
    if archivo.suffix.lower() in VIDEOS:
        largo = duracion(ffmpeg, archivo)
        entrada = ["-ss", f"{offset % largo:.3f}"] if offset else []
        entrada += ["-stream_loop", "-1", "-i", str(archivo)]
    else:
        entrada = ["-loop", "1", "-framerate", str(FPS), "-i", str(archivo)]
    cmd = [ffmpeg, "-y", *entrada, "-t", f"{dur:.3f}", "-filter_complex", vf, "-an",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(salida)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:])
        sys.exit(f"Falló el tramo de {archivo.name}")


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

    ancho, alto = FORMATOS[a.formato]
    vf = filtro_encuadre(ancho, alto, a.fondo)
    total = hasta - desde
    n_vid = sum(1 for f, *_ in tramos if f.suffix.lower() in VIDEOS)
    print(f"Armando {a.salida} ({a.formato}, {len(tramos)} tramos, {n_vid} videos, {total:.1f}s)...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        lista = tmp / "lista.txt"
        with lista.open("w") as l:
            for i, (f, ini, fin, off) in enumerate(tramos):
                parte = tmp / f"{i:04d}.mp4"
                render_tramo(ffmpeg, f, fin - ini, off, parte, vf)
                l.write(f"file '{parte}'\n")
        mudo = tmp / "mudo.mp4"
        r = subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                            "-c", "copy", str(mudo)], capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-1500:])
            sys.exit("Falló la unión de tramos.")

        cmd = [ffmpeg, "-y", "-i", str(mudo), "-ss", f"{desde:.3f}", "-t", f"{total:.3f}",
               "-i", str(a.audio), "-map", "0:v", "-map", "1:a"]
        if a.subs:
            srt = str(a.subs.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
            cmd += ["-vf", f"subtitles='{srt}':force_style='Fontsize=14,Bold=1,Outline=2,"
                           f"MarginV={'60' if a.formato == 'vertical' else '30'}'",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20"]
        else:
            cmd += ["-c:v", "copy"]
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(a.salida)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-2000:])
            if a.subs and "subtitles" in r.stderr:
                print("\nTu ffmpeg no soporta subtítulos quemados; probá sin --subs o instalá ffmpeg completo.")
            sys.exit(1)
    print("Listo.")


if __name__ == "__main__":
    main()
