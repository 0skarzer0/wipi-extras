# wipi-extras

Añadidos para [WiPi Netbooter](https://github.com/chunksin/WiPiNetbooter), el netbooter en Raspberry Pi para placas
NAOMI, NAOMI 2 y Atomiswave por NetDIMM. Se instalan encima de un WiPi ya montado, guardando antes los ficheros
originales, y se pueden deshacer.

| Carpeta | Qué hace | Estado |
|---|---|---|
| [`osm-fotos/`](osm-fotos/README.md) | El menú en pantalla (OSM) enseña la foto del juego seleccionado, la misma de la web del WiPi; con receta para poner capturas a los juegos que no tienen | Probado en placa (NAOMI 2, mueble Crazy Taxi) |
| [`vmu/`](vmu/README.md) | Los juegos de Dreamcast convertidos con [dc2naomi](https://github.com/0skarzer0/dc2naomi) guardan su Visual Memory en un fichero `.vmu` junto a la imagen | En uso en dos Raspberry |
| [`initiald-cards/`](initiald-cards/README.md) | Emulación de las tarjetas de Initial D | Por empezar |

## Instalación

En la Raspberry, como root, con este repositorio copiado en ella (por ejemplo en `/root/wipi-extras`):

```
cd /root/wipi-extras
./install.sh osm        # menú con foto
./install.sh vmu        # VMU en ficheros
./install.sh all        # las dos cosas
./install.sh undo-osm   # deshacer el menú
./install.sh undo-vmu   # deshacer la VMU
```

Se puede volver a pasar sin problema, por ejemplo después de actualizar WiPi, que puede deshacer los cambios.
Los originales se guardan una sola vez como `*.orig_osm` (menú) y `wipiloader.py.orig` (VMU).

Más detalle, trampas aprendidas y cómo seguir: [`docs/HANDOFF.md`](docs/HANDOFF.md).

## Agradecimientos

- **[WiPi Netbooter](https://github.com/chunksin/WiPiNetbooter)** (chunksin y colaboradores): todo esto se apoya en
  él, en sus scripts (`netdimm_menu.py` adaptado a `romsinfo.csv`, `wipiloader.py`, `timehack.py`, que sirvió de
  modelo para la vigilancia de la VMU) y en sus fotos de los juegos.
- **DragonMinded (Jennifer Taylor)**: autora de las herramientas de netboot que usa WiPi, del `netbootmenu` y de
  libnaomi, publicados como dominio público. Sus repositorios ya no están en GitHub; se usaron las copias
  [ArcadeHustle/netboot](https://github.com/ArcadeHustle/netboot) y
  [sega-dreamcast/libnaomi](https://github.com/sega-dreamcast/libnaomi). Su libnaomi documenta además el protocolo
  de la NetDIMM con el que se lee la memoria de la placa.
- **KallistiOS**, en cuyos scripts se basa el toolchain de libnaomi; **zlib**, **libpng**, **bzip2**, **FreeType**,
  **DejaVu Sans** y **Pillow**, que usa el menú con fotos.
- **[libretro-thumbnails](https://github.com/libretro-thumbnails)**, de donde salen las capturas de partida de los
  juegos de Dreamcast que no tenían foto (`osm-fotos/imagenes/`).
- **Flycast**, **MaplePad** (mackieks), **libevmu** (Falco Girgis), **dcvmu-tool** (bucanero), **waterbear**
  (wtetzner) y **chao** (lordbananza), que sirvieron para la VMU (detalle en [`vmu/`](vmu/README.md)).
- **[dc2naomi](https://github.com/0skarzer0/dc2naomi)**, de donde salen los scripts de la VMU.
