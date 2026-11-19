# Menú en pantalla (OSM) del WiPi con foto del juego

Versión del `netbootmenu` de DragonMinded, el menú que el WiPi Netbooter lanza en la NAOMI para elegir juego,
que enseña a la derecha de la lista la foto del juego seleccionado. Las fotos son las mismas que usa la web del WiPi:
el PNG de la columna 3 de `romsinfo.csv`, en `/var/www/html/images/`.

## Cómo funciona

- **En la Raspberry** (`wipi/patch_netdimm_menu.py`): el script del WiPi que lanza el menú
  (`/sbin/piforce/dm_netboot/scripts/netdimm_menu.py`) reduce cada foto a 256×256 como máximo (sin deformarla),
  la pasa a RGB565, la comprime con zlib y la añade **al final de la imagen del menú**, detrás de lo que carga la BIOS.
  En la configuración que ya le pasaba al menú (sección en `0x0D000000`) añade un campo más, `thumbs_offset`,
  con la posición de ese bloque. Las fotos convertidas se guardan en `/boot/config/osmthumbs/` y solo se vuelven a
  convertir si cambia el PNG.
- **En la NAOMI** (`netbootmenu/thumbs.c`): el menú lee de la NetDIMM (`cart_read`) solo la foto del juego que está
  bajo el cursor, cuando el cursor lleva 0,15 s quieto, la descomprime y la sube a una de dos texturas de 256×256.
  Así da igual cuántos juegos haya: no se gasta memoria principal ni de vídeo por cada uno, y el desplazamiento
  por la lista no se frena. Los nombres que llegarían a la foto se cortan con «...».
- Formato del bloque: ver el comentario de `netbootmenu/thumbs.h`.
- Si el script no encuentra Pillow (`python3-pil`) o una foto falla, el menú sale como siempre, sin foto.
  El script parcheado también funciona con el menú original (que ignora el campo nuevo).

## Instalación en una Raspberry con WiPi

Con el instalador del repositorio: `sudo ./install.sh osm` (y `sudo ./install.sh undo-osm` para volver atrás). A mano:

```
# copia de seguridad del menú que trae el WiPi
cp /sbin/piforce/dm_netboot/homebrew/netbootmenu/netbootmenu.bin /sbin/piforce/dm_netboot/homebrew/netbootmenu/netbootmenu.bin.orig_osm
cp netbootmenu_fotos.bin /sbin/piforce/dm_netboot/homebrew/netbootmenu/netbootmenu.bin
cp netbootmenu_fotos.bin /sbin/piforce/dm_netboot/homebrew/netbootmenu/netbootmenu.bin.dark   # (tras copiar el .dark original)
python3 patch_netdimm_menu.py /sbin/piforce/dm_netboot/scripts/netdimm_menu.py   # guarda .orig_osm
```

Ojo: al elegir el tema del menú en la web del WiPi se copia `netbootmenu.bin.dark` o `.light` encima de
`netbootmenu.bin`. El instalador pone también el menú con fotos como `.dark`, así que con el tema oscuro las fotos
siguen; con el claro sale el menú claro original, sin fotos. Una actualización del WiPi puede deshacer todo esto: hay que repetirlas. Para volver atrás, copiar los
`.orig_osm` encima.

## Compilar

Hace falta el toolchain de libnaomi (`setup/` de libnaomi: `download.sh`, `unpack.sh`, `make`) y, para el menú, sus
librerías zlib, bzip2, libpng y freetype (`make -C 3rdparty/<lib> install`). zlib 1.2.12 ya no está en zlib.net:
se baja de `https://zlib.net/fossils/zlib-1.2.12.tar.gz` a `3rdparty/zlib/download/`. Después:

```
source /opt/toolchains/naomi/env.sh
# IMPRESCINDIBLE para WiPi: protocolo de mensajes antiguo (sin esto el menú no puede cargar juegos)
(cd libnaomi && git apply ../osm-fotos/libnaomi-patch/packet-seeds-wipi.patch)
make -C libnaomi && make -C libnaomi install
make -C libnaomi/libnaomi/message && make -C libnaomi/libnaomi/message install
make -C osm-fotos/netbootmenu   # da netbootmenu.bin: copiarlo como osm-fotos/netbootmenu_fotos.bin
```

Con GCC 13 del sistema, el toolchain se compiló con `make CFLAGS="-O2 -fpermissive" CXXFLAGS="-O2 -fpermissive -std=gnu++14"`.

## Origen del código y agradecimientos

- **DragonMinded (Jennifer Taylor)**: autora del `netbootmenu`, de `netdimm_menu` y de libnaomi, publicados como
  dominio público (Unlicense). Este menú es su código con la foto añadida. Sus repositorios originales
  (`DragonMinded/netboot` y `DragonMinded/libnaomi`) ya no están en GitHub (noviembre de 2026); se usaron las copias de:
  - **[ArcadeHustle/netboot](https://github.com/ArcadeHustle/netboot)**, fork de netboot (commit `2008fa7`,
    enero de 2022), de donde sale `netbootmenu/`.
  - **[sega-dreamcast/libnaomi](https://github.com/sega-dreamcast/libnaomi)**, fork de libnaomi (commit `f32c2f4`),
    con el que se compila. Sus scripts del toolchain se basan en los de **KallistiOS**.
- **[WiPi Netbooter](https://github.com/chunksin/WiPiNetbooter)** (chunksin y colaboradores): integra el menú de
  DragonMinded, adapta `netdimm_menu.py` para leer `romsinfo.csv` y aporta las fotos de los juegos que se usan aquí.
- **zlib** (Jean-loup Gailly y Mark Adler), **libpng**, **bzip2** (Julian Seward), **FreeType** y **DejaVu Sans**,
  que usa el menú; **Pillow**, con el que la Raspberry convierte las fotos.

## Estado

Probado en la placa NAOMI 2 del mueble Crazy Taxi (WiPi en una Raspberry, NetDIMM en `10.0.0.4`) el 2026-11-19:
54 juegos en el menú, 53 con foto (uno no tiene imagen en el CSV); la primera vez la Pi tarda unos 7,5 s en convertir
las fotos y luego 0,1 s. «Está perfecto».

Cambios respecto al menú original: `thumbs.c`/`thumbs.h` (nuevos), `config.h` (campo `thumbs_offset`), `screens.c`
(dibujo de la foto, nombres cortados y el nombre como argumento de `%s` en vez de como formato), `Makefile`.
