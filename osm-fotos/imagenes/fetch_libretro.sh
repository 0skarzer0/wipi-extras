#!/bin/bash
# Baja de libretro-thumbnails (Sega_-_Dreamcast) las capturas de partida de los juegos de un mapa.tsv y las deja
# con el nombre de imagen del mapa. Se ejecuta en un PC con Internet (las Raspberry no tienen).
#
#   ./fetch_libretro.sh mapa-dc2naomi.tsv CARPETA_DE_SALIDA [Named_Snaps|Named_Logos|Named_Titles|Named_Boxarts]
#
# Solo baja los ficheros que hacen falta (clon parcial, sin las ~5000 imágenes del repositorio).
# Luego: set_csv_images.py en la Raspberry (ver ../README.md).
set -e
MAPA="$1"; OUT="$2"; TIPO="${3:-Named_Snaps}"
[ -f "$MAPA" ] && [ -n "$OUT" ] || { sed -n 2,8p "$0"; exit 1; }
WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
GIT_LFS_SKIP_SMUDGE=1 git clone -q --filter=blob:none --no-checkout --depth 1 \
    https://github.com/libretro-thumbnails/Sega_-_Dreamcast "$WORK/r"
cd "$WORK/r"
grep -v '^#' "$MAPA" | cut -f3 | sed "s#^#$TIPO/#; s#\$#.png#" > "$WORK/paths"
git checkout -q HEAD --pathspec-from-file="$WORK/paths"
# Los duplicados por región son enlaces simbólicos a otro fichero: bajar también el destino.
for i in 1 2 3; do
    : > "$WORK/targets"
    for f in "$TIPO"/*; do
        [ -L "$f" ] && [ ! -e "$f" ] && echo "$TIPO/$(readlink "$f")" >> "$WORK/targets"
    done
    [ -s "$WORK/targets" ] || break
    git checkout -q HEAD --pathspec-from-file="$WORK/targets"
done
mkdir -p "$OUT"
while IFS=$'\t' read -r rom png nombre _; do
    case "$rom" in \#*|"") continue;; esac
    cp -L "$TIPO/$nombre.png" "$OUT/$png" || echo "FALTA: $nombre"
done < "$MAPA"
echo "Imágenes en $OUT"
