#!/usr/bin/env python3
"""Crea la carpeta de un short nuevo y la abre.

    python scripts/nuevo_episodio.py "choque de trenes"

Crea episodios/AAAA-MM-DD-choque-de-trenes/ con:
    guion.md      -> pegás el guion de ChatGPT
    material/     -> tirás tus fotos y videos (cualquier nombre)
    (tu audio)    -> tirás tu grabación en la carpeta (cualquier nombre)
"""
import datetime
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:50] or "short"


def abrir(carpeta):
    try:
        if sys.platform.startswith("win"):
            os.startfile(carpeta)
        elif sys.platform == "darwin":
            subprocess.run(["open", carpeta])
        else:
            subprocess.run(["xdg-open", carpeta])
    except Exception:
        pass


def main():
    tema = " ".join(sys.argv[1:]).strip() or input("Tema del short: ").strip()
    base = f"{datetime.date.today():%Y-%m-%d}-{slug(tema)}"
    carpeta = RAIZ / "episodios" / base
    n = 2
    while carpeta.exists():
        carpeta = RAIZ / "episodios" / f"{base}-{n}"
        n += 1
    (carpeta / "material").mkdir(parents=True)
    (carpeta / "guion.md").write_text(
        f"# {tema}\n\n(Borrá esta línea y pegá acá el guion completo de ChatGPT, con la tabla.)\n",
        encoding="utf-8")
    (carpeta / "visual.md").write_text(
        "(Pegá acá el plan visual del Buscador visual. Es opcional.)\n", encoding="utf-8")
    (carpeta / "LEEME.txt").write_text(
        "1. Pegá el guion en guion.md y el plan visual en visual.md.\n"
        "2. Tirá tu grabación de voz en esta carpeta (cualquier nombre: mp3, m4a, wav...).\n"
        "3. Tirá las fotos y videos en la carpeta material (cualquier nombre).\n"
        "4. En Claude Code escribí: /short\n",
        encoding="utf-8")
    print(f"Listo: {carpeta}")
    abrir(carpeta)


if __name__ == "__main__":
    main()
