#!/usr/bin/env python3
"""Pone la imagen de cada juego en romsinfo.csv de WiPi (columna 3) y copia los PNG a la carpeta de imágenes.

Uso (en la Raspberry, como root):
    python3 set_csv_images.py MAPA.tsv CARPETA_CON_LOS_PNG            # solo enseña lo que haría
    python3 set_csv_images.py MAPA.tsv CARPETA_CON_LOS_PNG --apply    # lo hace
    ... --apply --replace    # además sustituye los PNG que ya existan con esos nombres

MAPA.tsv: una línea por juego, `fichero_del_juego.bin.gz<TAB>imagen.png` (las demás columnas, si las hay, se ignoran).

- Edita /boot/config/romsinfo.csv y /var/www/html/csv/romsinfo.csv (las dos copias que usa WiPi) a nivel de texto:
  solo cambia la columna 3 de la fila de ese juego, y solo si está vacía; el resto de la fila y del fichero queda
  byte por byte igual (comillas, saltos de línea).
- Antes guarda una copia de cada CSV como romsinfo.csv.bak_osmfotos (solo la primera vez).
- Copia los PNG a /boot/config/images (la web del WiPi la ve como /var/www/html/images) sin pisar ninguno que ya exista
  con ese nombre y distinto, salvo con --replace (útil para cambiar, por ejemplo, logos por capturas de partida).
- Se puede repetir: lo que ya está puesto se salta.
"""
import os
import shutil
import sys

CSVS = ["/boot/config/romsinfo.csv", "/var/www/html/csv/romsinfo.csv"]
IMAGES = "/boot/config/images"


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    replace = "--replace" in sys.argv
    if len(args) != 2:
        print(__doc__)
        return 1
    mapfile, pngdir = args

    wanted = {}
    with open(mapfile, encoding="utf-8") as fp:
        for line in fp:
            line = line.rstrip("\r\n")
            if not line or line.startswith("#"):
                continue
            cols = line.split("\t")
            wanted[cols[0]] = cols[1]

    problems = 0
    for name, image in wanted.items():
        if not os.path.isfile(os.path.join(pngdir, image)):
            print(f"FALTA el PNG {image} ({name})")
            problems += 1
    if problems:
        return 1

    seen_csv = set()
    for path in CSVS:
        real = os.path.realpath(path)
        if real in seen_csv:
            print(f"{path}: es el mismo fichero que otro ya tratado")
            continue
        seen_csv.add(real)
        with open(path, "rb") as fp:
            data = fp.read()
        changed = 0
        for name, image in wanted.items():
            old = ("," + name + ",,").encode("utf-8")
            new = ("," + name + "," + image + ",").encode("utf-8")
            n = data.count(old)
            if n == 0:
                if ("," + name + "," + image + ",").encode("utf-8") in data:
                    continue  # ya puesta
                print(f"{path}: no hay fila de {name} con la imagen vacía")
                continue
            if n > 1:
                print(f"{path}: {name} sale {n} veces, no toco nada de ese juego")
                continue
            data = data.replace(old, new)
            changed += 1
        print(f"{path}: {changed} filas {'cambiadas' if apply else 'por cambiar'}")
        if apply and changed:
            backup = path + ".bak_osmfotos"
            if not os.path.exists(backup):
                shutil.copy2(path, backup)
            with open(path + ".tmp", "wb") as fp:
                fp.write(data)
            os.replace(path + ".tmp", path)

    for image in sorted(set(wanted.values())):
        dest = os.path.join(IMAGES, image)
        src = os.path.join(pngdir, image)
        if os.path.exists(dest):
            with open(src, "rb") as a, open(dest, "rb") as b:
                same = a.read() == b.read()
            if same:
                continue
            if not replace:
                print(f"{dest} ya existe y es distinta: no la piso (usa --replace para sustituirla)")
                continue
            print(f"{'sustituyo' if apply else 'sustituiría'} {image}")
            if apply:
                shutil.copy2(src, dest)
            continue
        print(f"{'copio' if apply else 'copiaría'} {image}")
        if apply:
            shutil.copy2(src, dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
