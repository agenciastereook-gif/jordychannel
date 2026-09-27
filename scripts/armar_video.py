#!/usr/bin/env python3
"""Arma un video a partir de una voz en off y una carpeta de imágenes
nombradas por su marca de tiempo (en segundos).

Cada imagen queda en pantalla desde su marca hasta la marca de la siguiente;
la última dura hasta el final del audio. Reemplaza el paso manual de
arrastrar imágenes en el editor.

Nombres válidos para las imágenes (png/jpg/webp):
    0.00.png   7.png   15.5.jpg      -> segundos
    00-07.png  01-15.50.png          -> minutos-segundos

Uso:
    python3 scripts/armar_video.py --audio voz.mp3 --imagenes imgs/ --salida short.mp4
    python3 scripts/armar_video.py ... --formato horizontal   # video largo 16:9
    python3 scripts/armar_video.py ... --subs voz.srt         # subtítulos quemados

Clip vertical de un tramo del video largo (reusa las mismas imágenes y el audio):
    python3 scripts/armar_video.py --audio voz.mp3 --imagenes imgs/ --subs voz.srt \
        --desde 02-10 --hasta 03-05 --salida clip1.mp4
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXTENSIONES = {".png", ".jpg", ".jpeg", ".webp"}
FORMATOS = {"vertical": (1080, 1920), "horizontal": (1920, 1080)}


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


SRT_TIEMPO = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")


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


def duracion_audio(ffmpeg, audio):
    salida = subprocess.run([ffmpeg, "-i", str(audio)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", salida)
    if not m:
        sys.exit(f"No pude leer la duración de {audio}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--audio", required=True, type=Path)
    p.add_argument("--imagenes", required=True, type=Path)
    p.add_argument("--salida", required=True, type=Path)
    p.add_argument("--formato", choices=FORMATOS, default="vertical")
    p.add_argument("--subs", type=Path, help="archivo .srt para quemar subtítulos")
    p.add_argument("--fondo", default="white", help="color de relleno (default: white)")
    p.add_argument("--desde", help="inicio del tramo (segundos o MM-SS) para sacar un clip")
    p.add_argument("--hasta", help="fin del tramo (segundos o MM-SS)")
    a = p.parse_args()

    ffmpeg = ffmpeg_bin()
    imagenes = []
    for f in a.imagenes.iterdir():
        if f.suffix.lower() in EXTENSIONES:
            t = marca_de_nombre(f.stem)
            if t is None:
                print(f"  (ignoro {f.name}: el nombre no es una marca de tiempo)")
            else:
                imagenes.append((t, f.resolve()))
    if not imagenes:
        sys.exit("No hay imágenes con nombre de marca de tiempo en la carpeta.")
    imagenes.sort()

    total = duracion_audio(ffmpeg, a.audio)
    desde = marca_de_nombre(a.desde) if a.desde else 0.0
    hasta = marca_de_nombre(a.hasta) if a.hasta else total
    if desde is None or hasta is None or not 0 <= desde < hasta:
        sys.exit("--desde/--hasta inválidos (usá segundos como 130 o minutos-segundos como 02-10).")
    hasta = min(hasta, total)
    if a.desde or a.hasta:
        previas = [im for im in imagenes if im[0] <= desde]
        imagenes = previas[-1:] + [im for im in imagenes if desde < im[0] < hasta]
        imagenes = [(t - desde, f) for t, f in imagenes]
        if a.subs:
            a.subs = recortar_srt(a.subs, desde, hasta)
    total = hasta - desde
    if not imagenes:
        sys.exit("No hay imágenes en ese tramo.")
    if imagenes[0][0] > 0:
        print(f"  Aviso: la primera imagen arranca en {imagenes[0][0]}s; la estiro hasta 0s.")
        imagenes[0] = (0.0, imagenes[0][1])

    ancho, alto = FORMATOS[a.formato]

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as lista:
        for i, (t, f) in enumerate(imagenes):
            fin = imagenes[i + 1][0] if i + 1 < len(imagenes) else total
            if fin <= t:
                continue
            ruta = str(f).replace("'", r"'\''")
            lista.write(f"file '{ruta}'\nduration {fin - t:.3f}\n")
        lista.write(f"file '{str(imagenes[-1][1])}'\n")  # el concat demuxer necesita repetir la última

    filtro = (f"scale={ancho}:{alto}:force_original_aspect_ratio=decrease,"
              f"pad={ancho}:{alto}:(ow-iw)/2:(oh-ih)/2:color={a.fondo},setsar=1,fps=30,format=yuv420p")
    if a.subs:
        srt = str(a.subs.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
        filtro += (f",subtitles='{srt}':force_style='Fontsize=14,Bold=1,Outline=2,"
                   f"MarginV={'60' if a.formato == 'vertical' else '30'}'")

    cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", lista.name, "-ss", f"{desde:.3f}", "-t", f"{total:.3f}", "-i", str(a.audio),
           "-vf", filtro, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(a.salida)]
    print(f"Armando {a.salida} ({a.formato}, {len(imagenes)} imágenes, {total:.1f}s)...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    Path(lista.name).unlink(missing_ok=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        if a.subs and "subtitles" in r.stderr:
            print("\nTu ffmpeg no soporta subtítulos quemados; probá sin --subs o instalá ffmpeg completo.")
        sys.exit(1)
    print("Listo.")


if __name__ == "__main__":
    main()
