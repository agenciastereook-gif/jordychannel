#!/usr/bin/env python3
"""Transcribe la voz en la compu (gratis, sin internet después de la primera vez)
y genera el .srt con marcas de tiempo. Reemplaza a TurboScribe.

    python scripts/transcribir.py episodios/<carpeta>/voz.m4a

Genera voz.srt al lado del audio, cortado en frases de ~2 a 4 segundos
(el ritmo de cambio de imagen). La primera vez baja el modelo de voz (~500 MB).

Necesita: pip install faster-whisper
"""
import argparse
import sys
from pathlib import Path

try:
    from faster_whisper import WhisperModel
except ImportError:
    sys.exit("Falta faster-whisper. Corré instalar.bat (o: pip install faster-whisper)")

PUNTUACION = (".", ",", "?", "!", ";", ":")


def fmt(s):
    ms = round(s * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("audio", type=Path)
    p.add_argument("--modelo", default="small", help="tiny/base/small/medium (más grande = más preciso y lento)")
    p.add_argument("--min", type=float, default=2.0, help="duración mínima de cada frase (s)")
    p.add_argument("--max", type=float, default=4.0, help="duración máxima de cada frase (s)")
    a = p.parse_args()

    print(f"Transcribiendo {a.audio.name} (modelo {a.modelo})...")
    modelo = WhisperModel(a.modelo, device="cpu", compute_type="int8")
    segmentos, _ = modelo.transcribe(str(a.audio), language="es", word_timestamps=True, vad_filter=True)

    bloques, actual = [], []
    for seg in segmentos:
        for w in seg.words:
            actual.append(w)
            dur = actual[-1].end - actual[0].start
            corte = w.word.strip().endswith(PUNTUACION)
            if dur >= a.max or (dur >= a.min and corte):
                bloques.append(actual)
                actual = []
    if actual:
        bloques.append(actual)

    salida = a.audio.with_suffix(".srt")
    with salida.open("w", encoding="utf-8") as f:
        for i, b in enumerate(bloques, 1):
            texto = "".join(w.word for w in b).strip()
            f.write(f"{i}\n{fmt(b[0].start)} --> {fmt(b[-1].end)}\n{texto}\n\n")
    print(f"Listo: {salida} ({len(bloques)} frases)")


if __name__ == "__main__":
    main()
