#!/usr/bin/env python3
"""Genera una imagen con ChatGPT (Codex CLI, con la cuenta de Jordy) y la deja en material/ del short.

    python scripts/generar_imagen.py episodios/<carpeta> "qué tiene que mostrar" [nombre]

Vertical 9:16, sin texto escrito y sin personas reales identificables (esas van con foto o video real).
Anota el crédito en material/creditos.json. Tarda alrededor de un minuto.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    material = Path(sys.argv[1]) / "material"
    material.mkdir(parents=True, exist_ok=True)
    desc = sys.argv[2]
    nombre = (sys.argv[3] if len(sys.argv) > 3 else f"ia_{time.strftime('%H%M%S')}") + ".png"
    codex = shutil.which("codex")
    if not codex:
        sys.exit("No está instalado Codex (ChatGPT). Corré INSTALAR.bat.")
    prompt = (f"Generá UNA imagen vertical 9:16 con tu herramienta de generación de imágenes y guardala como "
              f"{nombre} en esta carpeta. Fotografía realista, estilo fotoperiodismo, luz natural; nunca dibujo ni "
              f"ilustración. Sin texto escrito dentro de la imagen. No representes a personas reales identificables. "
              f"La imagen: {desc}")
    subprocess.run([codex, "exec", "--skip-git-repo-check", "--ephemeral", "-s", "workspace-write",
                    "-C", str(material), "-"], input=prompt, text=True, encoding="utf-8",
                   capture_output=True, timeout=600)
    if not (material / nombre).exists():
        sys.exit("ChatGPT no generó la imagen.")
    creditos = material / "creditos.json"
    datos = json.loads(creditos.read_text(encoding="utf-8")) if creditos.exists() else {}
    datos[nombre] = {"fuente": "Imagen generada con IA (ChatGPT)", "segura": "ia", "para": desc}
    creditos.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    print(material / nombre)


if __name__ == "__main__":
    main()
