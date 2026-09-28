#!/usr/bin/env python3
"""Anima una imagen con IA en esta PC (Wan2GP, gratis, sin límite) y deja el video al lado de la imagen.

    python scripts/animar_imagen.py episodios/<carpeta>/material/ia_123.png "qué se mueve"

Usa la instalación de F:\\IA\\Wan2GP (su propio Python). Tarda varios minutos por clip de 5 s.
Imprime la ruta del video.
"""
import os
import subprocess
import sys
from pathlib import Path

WAN = Path(os.environ.get("WAN2GP", r"F:\IA\Wan2GP"))
MODELO = "ti2v_2_2_fastwan"  # Wan 2.2 5B en 3 pasos: el que entra cómodo en una RTX 3060 de 12 GB

# lo corre el Python de Wan2GP (el de este proyecto no tiene torch)
TRABAJO = r'''
import sys
from pathlib import Path
from shared.api import init
imagen, prompt, salida = sys.argv[1:4]
s = init(root=Path("."), cli_args=["--attention", "sdpa", "--profile", "4"], output_dir=Path(salida).parent)
r = s.submit_task({"model_type": "%s", "prompt": prompt, "image_start": imagen, "image_prompt_type": "S",
                   "resolution": "720x1280", "video_length": "5s"}).result()
if not r.success:
    sys.exit("\n".join(e.message for e in r.errors))
Path(r.generated_files[-1]).replace(salida)
''' % MODELO


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    imagen = Path(sys.argv[1]).resolve()
    salida = imagen.with_suffix(".mp4")
    py = WAN / "venv" / "Scripts" / "python.exe"
    if not py.exists():
        sys.exit("No está instalado Wan2GP (F:\\IA\\Wan2GP).")
    prompt = ("Vertical 9:16 news b-roll, realistic motion, steady camera, no text. " + sys.argv[2])
    r = subprocess.run([str(py), "-c", TRABAJO, str(imagen), prompt, str(salida)], cwd=WAN)
    if r.returncode != 0 or not salida.exists():
        sys.exit("No se pudo animar la imagen.")
    print(salida)


if __name__ == "__main__":
    main()
