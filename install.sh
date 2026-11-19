#!/bin/bash
# Instala los añadidos de wipi-extras en una Raspberry con WiPi Netbooter.
#
#   sudo ./install.sh osm        menú en pantalla con la foto del juego
#   sudo ./install.sh vmu        Visual Memory de los juegos dc2naomi en ficheros .vmu
#   sudo ./install.sh all        las dos cosas
#   sudo ./install.sh undo-osm   vuelve al menú y al netdimm_menu.py originales
#   sudo ./install.sh undo-vmu   vuelve al wipiloader.py original (los scripts se quedan, sin usarse)
#
# Se puede repetir sin miedo (por ejemplo tras actualizar WiPi): guarda los originales solo la primera vez.
set -e
cd "$(dirname "$0")"

PIFORCE=/sbin/piforce
NB=$PIFORCE/dm_netboot
MENU=$NB/homebrew/netbootmenu

backup() {   # copia el original solo si no hay ya una copia
    [ -e "$1.orig_osm" ] || cp -p "$1" "$1.orig_osm"
}

install_osm() {
    echo "== Menú con foto"
    python3 -c "import PIL" 2>/dev/null || echo "AVISO: falta python3-pil (Pillow); el menú saldrá sin fotos"
    backup "$MENU/netbootmenu.bin"
    backup "$MENU/netbootmenu.bin.dark"
    cp osm-fotos/netbootmenu_fotos.bin "$MENU/netbootmenu.bin.fotos"
    # El tema oscuro de WiPi copia netbootmenu.bin.dark encima de netbootmenu.bin: que sea también el de las fotos.
    cp osm-fotos/netbootmenu_fotos.bin "$MENU/netbootmenu.bin.dark"
    cp osm-fotos/netbootmenu_fotos.bin "$MENU/netbootmenu.bin"
    python3 osm-fotos/patch_netdimm_menu.py "$NB/scripts/netdimm_menu.py"
    python3 -m py_compile "$NB/scripts/netdimm_menu.py"
    md5sum "$MENU/netbootmenu.bin"
}

undo_osm() {
    echo "== Menú original"
    for f in "$MENU/netbootmenu.bin" "$MENU/netbootmenu.bin.dark" "$NB/scripts/netdimm_menu.py"; do
        [ -e "$f.orig_osm" ] && cp -p "$f.orig_osm" "$f" && echo "restaurado $f"
    done
}

install_vmu() {
    echo "== VMU en ficheros"
    cp vmu/dc2naomi_send.py vmu/dc2naomi_vmu.py "$PIFORCE/"
    python3 vmu/patch_wipiloader.py "$PIFORCE/wipiloader.py"
    python3 -m py_compile "$PIFORCE/wipiloader.py"
}

undo_vmu() {
    echo "== wipiloader.py original"
    [ -e "$PIFORCE/wipiloader.py.orig" ] && cp -p "$PIFORCE/wipiloader.py.orig" "$PIFORCE/wipiloader.py" && echo "restaurado"
}

case "$1" in
    osm) install_osm ;;
    vmu) install_vmu ;;
    all) install_osm; install_vmu ;;
    undo-osm) undo_osm ;;
    undo-vmu) undo_vmu ;;
    *) sed -n 2,12p "$0"; exit 1 ;;
esac
echo "Hecho."
