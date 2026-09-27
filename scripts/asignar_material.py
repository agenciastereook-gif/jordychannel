#!/usr/bin/env python3
"""Copia tus fotos/videos a la carpeta de imágenes con el nombre de su marca de tiempo,
según un archivo de asignación que arma Claude (y que vos podés corregir a mano).

Formato de asignacion.txt (una línea por marca; lo que va después de | es solo referencia):
    [0.00] material/lula_congreso.jpg | Lula firmó hoy el decreto...
    [3.40] DIBUJO | Las apuestas online movían millones...
    [6.10] material/celular_apuestas.mp4 | Desde el lunes...
    [9.00] = | (repite el archivo anterior: no genera corte)

    python3 scripts/asignar_material.py episodios/<carpeta>/asignacion.txt

Las rutas son relativas a la carpeta del episodio. Las marcas con DIBUJO se listan al final
para generarlas con Higgsfield (prompts/02_imagenes.md). Las marcas con "=" se saltean, así
el archivo anterior sigue en pantalla.
"""
import re
import shutil
import sys
from pathlib import Path

LINEA = re.compile(r"^\s*\[(\d+(?:\.\d+)?)\]\s*([^|]+?)\s*(?:\|.*)?$")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    asignacion = Path(sys.argv[1])
    episodio = asignacion.parent
    destino = episodio / "imagenes"
    destino.mkdir(exist_ok=True)

    dibujos, faltan, copiados = [], [], 0
    for n, linea in enumerate(asignacion.read_text(encoding="utf-8").splitlines(), 1):
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        m = LINEA.match(linea)
        if not m:
            print(f"  línea {n} no entendida: {linea}")
            continue
        marca, archivo = f"{float(m.group(1)):.2f}", m.group(2)
        if archivo == "=":
            continue
        if archivo.upper() == "DIBUJO":
            dibujos.append(linea.strip())
            continue
        origen = episodio / archivo
        if not origen.exists():
            faltan.append(f"[{marca}] {archivo}")
            continue
        for viejo in destino.glob(f"{marca}.*"):
            viejo.unlink()
        shutil.copy2(origen, destino / f"{marca}{origen.suffix.lower()}")
        copiados += 1

    print(f"Copiados {copiados} archivos a {destino}/")
    if faltan:
        print("\nNo encontré estos archivos:\n  " + "\n  ".join(faltan))
    if dibujos:
        print(f"\nFaltan {len(dibujos)} dibujos (pasáselos a prompts/02_imagenes.md):")
        print("\n".join(d.replace(" DIBUJO |", "").replace("DIBUJO", "") for d in dibujos))


if __name__ == "__main__":
    main()
