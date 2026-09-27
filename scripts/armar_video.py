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
    if imagenes[0][0] > 0:
        print(f"  Aviso: la primera imagen arranca en {imagenes[0][0]}s; la estiro hasta 0s.")
        imagenes[0] = (0.0, imagenes[0][1])

    total = duracion_audio(ffmpeg, a.audio)
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

    cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", lista.name, "-i", str(a.audio),
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
