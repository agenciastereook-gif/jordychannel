#!/usr/bin/env python3
"""Copia tus fotos/videos a la carpeta de imágenes con el nombre de su marca de tiempo,
según un archivo de asignación que arma Claude (y que vos podés corregir a mano).

Formato de asignacion.txt (una línea por marca; lo que va después de | es solo referencia):
    [0.00] material/lula_congreso.jpg | Lula firmó hoy el decreto...
    [3.40] IA | Las apuestas online movían millones...
    [6.10] material/celular_apuestas.mp4 | Desde el lunes...
    [9.00] = | (repite el archivo anterior: no genera corte)
    [12.40] INSERTAR material/clip.mp4 | (sonido original: corta la voz, pasa el clip, retoma)
    [12.40] INSERTAR material/clip.mp4 desde 0:05 hasta 0:12 | (solo ese tramo del clip)

    python3 scripts/asignar_material.py episodios/<carpeta>/asignacion.txt

Las rutas son relativas a la carpeta del episodio. Las marcas con "=" o "IA" se saltean, así
el archivo anterior sigue en pantalla. Las IA se listan al final: si algún día generás esa
imagen o animación, guardala en material/ y cambiá la línea por su ruta.

INSERTAR es para los [SONIDO ORIGINAL] del guion: la marca es el punto de la voz donde se corta
(el comienzo de la frase que sigue en el guion). La línea INSERTAR va además de la línea normal
de esa marca, no en su lugar.
"""
import re
import shutil
import sys
from pathlib import Path

LINEA = re.compile(r"^\s*\[(\d+(?:\.\d+)?)\]\s*([^|]+?)\s*(?:\|.*)?$")
INSERTAR = re.compile(r"^INSERTAR\s+(.+?)(?:\s+desde\s+([\d:.]+))?(?:\s+hasta\s+([\d:.]+))?$", re.I)


def segundos(txt):
    """'12' -> 12.0 ; '0:05' -> 5.0 ; '1:02.5' -> 62.5"""
    s = 0.0
    for x in txt.split(":"):
        s = s * 60 + float(x)
    return s


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    asignacion = Path(sys.argv[1])
    episodio = asignacion.parent
    destino = episodio / "imagenes"
    destino.mkdir(exist_ok=True)

    pendientes_ia, faltan, copiados, insertos = [], [], 0, 0
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
        ins = INSERTAR.match(archivo)
        if ins:
            origen = episodio / ins.group(1)
            if not origen.exists():
                faltan.append(f"[{marca}] {ins.group(1)}")
                continue
            for viejo in destino.glob(f"{marca}+insertar.*"):
                viejo.unlink()
            shutil.copy2(origen, destino / f"{marca}+insertar{origen.suffix.lower()}")
            rango = " ".join(str(segundos(x)) if x else "-" for x in (ins.group(2), ins.group(3)))
            (destino / f"{marca}+insertar.rango").write_text(rango + "\n")
            insertos += 1
            continue
        if archivo.upper() in ("IA", "DIBUJO"):
            pendientes_ia.append(linea.strip())
            continue
        origen = episodio / archivo
        if not origen.exists():
            faltan.append(f"[{marca}] {archivo}")
            continue
        for viejo in [v for v in destino.glob(f"{marca}.*") if "+insertar" not in v.name]:
            viejo.unlink()
        shutil.copy2(origen, destino / f"{marca}{origen.suffix.lower()}")
        copiados += 1

    print(f"Copiados {copiados} archivos a {destino}/")
    if insertos:
        print(f"{insertos} clips con sonido original para insertar.")
    if faltan:
        print("\nNo encontré estos archivos:\n  " + "\n  ".join(faltan))
    if pendientes_ia:
        print(f"\n{len(pendientes_ia)} marcas IA (opcional; mientras tanto sigue la imagen anterior):")
        print("\n".join(pendientes_ia))


if __name__ == "__main__":
    main()
