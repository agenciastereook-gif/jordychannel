#!/usr/bin/env python3
"""Convierte el .srt que exporta TurboScribe (o Whisper) en una lista limpia
de marcas de tiempo para pegar debajo del prompt de imágenes.

    python scripts/srt_a_marcas.py voz.srt --salida marcas.txt

Salida:
    [0.00] Hoy Wanda Nara rompió el silencio...
    [3.42] Y lo hizo en un móvil en vivo...

--min-seg junta frases muy cortas para no generar una imagen cada medio segundo
(default 2.0 s, como el ritmo de los videos de referencia).
"""
import argparse
import re
import sys
from pathlib import Path

TIEMPO = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")


def seg(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def main():
    p = argparse.ArgumentParser()
    p.add_argument("srt", type=Path)
    p.add_argument("--min-seg", type=float, default=2.0)
    p.add_argument("--salida", type=Path, help="archivo de salida (UTF-8); sin esto, imprime")
    a = p.parse_args()

    bloques = []
    for bloque in re.split(r"\n\s*\n", a.srt.read_text(encoding="utf-8-sig").strip()):
        lineas = bloque.strip().splitlines()
        for i, l in enumerate(lineas):
            m = TIEMPO.search(l)
            if m:
                texto = " ".join(lineas[i + 1:]).strip()
                if texto:
                    bloques.append([seg(*m.groups()[:4]), seg(*m.groups()[4:]), texto])
                break

    unidos = []
    for ini, fin, texto in bloques:
        if unidos and unidos[-1][1] - unidos[-1][0] < a.min_seg:
            unidos[-1][1] = fin
            unidos[-1][2] += " " + texto
        else:
            unidos.append([ini, fin, texto])

    lineas = "".join(f"[{ini:.2f}] {texto}\n" for ini, _, texto in unidos)
    if a.salida:
        a.salida.write_text(lineas, encoding="utf-8")
        print(f"Listo: {a.salida} ({len(unidos)} marcas)")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(lineas, end="")


if __name__ == "__main__":
    main()
