# Arreglos para WiPi

## `patch_menulauncher.py` — "Communication Error!" en el menú

**Síntoma:** el menú de la NAOMI muestra *Communication Error! We seem to have lost communication with the controlling software*.

**Causa (19-11-2026, en las dos cabinas):** en modo normal, `/sbin/piforce/menulauncher.py` de WiPi lanza un `netdimm_menu`
nuevo cada vez que se pide el menú (web, arranque, LCD) y no cierra el anterior. Había 3 y 4 instancias a la vez
hablando con la misma NetDIMM. Con las capturas, el envío del menú tarda más (unos 10 MB en la .250), así que es más fácil
volver a pedirlo antes de que termine.

**Arreglo:** `sudo python3 patch_menulauncher.py` hace que el lanzador cierre las instancias previas antes de abrir otra
(es idempotente y guarda `menulauncher.py.orig`). El `pgrep` usa `[d]m_netboot` para no encontrarse a sí mismo
(con `dm_netboot` se mataba su propia shell).

**Arreglo inmediato a mano:** `for p in $(pgrep -f "[d]m_netboot/netdimm_menu"); do kill -9 $p; done` y volver a lanzar el menú una sola vez.

Gracias a chunksin por WiPi Netbooter y a DragonMinded por netboot/netdimm_menu.

## "Communication Error!" al elegir juego (menú con fotos)

**Causa:** `cart_read()` de libnaomi tiene las interrupciones desactivadas durante toda la lectura, y la NetDIMM habla con el
menú (peek/poke de los registros 0xC0DE10..60) mediante interrupciones. Con los logos (pocos KB) no se notaba; con las capturas
(decenas de KB comprimidas) la lectura de la foto dejaba sin atender a la NetDIMM y se perdía la comunicación al elegir juego.

**Arreglo:** `osm-fotos/netbootmenu/thumbs.c` lee la foto en trozos de 512 bytes (`THUMB_READ_CHUNK`), con las interrupciones
activas entre trozos. Nuevo `netbootmenu_fotos.bin` (md5 b14b1e07568ee12203c628105530c286).

## La causa real del "Communication Error!" al elegir juego: protocolo de mensajes distinto

Lo de la foto (sección anterior) no era la causa. La librería de mensajes de WiPi (`/sbin/piforce/dm_netboot/netdimm/message.py`)
es la versión antigua del protocolo de DragonMinded: los checksums de los registros 0xC0DE20/30/40 no llevan semilla.
La libnaomi actual (sega-dreamcast/libnaomi, con la que se compiló el menú con fotos) suma una semilla (3, 7 y 19).
La Pi descartaba todas las respuestas de la NAOMI como inválidas (cada sondeo agotaba los 2 s de `MAX_READ_TIMEOUT`)
y nunca recibía la elección del juego. A los 5 s el menú mostraba "Communication Error!".

Cómo se vio: con `netdimm_menu` parado, leyendo los registros desde la Pi: config `E9000003`, que solo es válido con la semilla 19.

**Arreglo:** compilar libnaomi con las semillas a 0 (`osm-fotos/libnaomi-patch/packet-seeds-wipi.patch`, en
`libnaomi/message/packet.c`; luego `make && make install` en `libnaomi/message` y volver a enlazar el menú).
Nuevo `netbootmenu_fotos.bin`: md5 b14b1e07568ee12203c628105530c286. Leer la foto por trozos se deja igualmente: no hace daño.

## "Communication Error!" que luego sí carga el juego (ROM .gz grandes)

Con el protocolo ya arreglado, en la .250 el error salía igual pero el juego acababa cargando. WiPi descomprime la ROM `.gz` antes
de contestar a la NAOMI (Akatsuki, 128 MB: 1,5 s de espera + 3,9 s descomprimiendo + 1,5 s = 7 s), y el menú solo esperaba 5 s
(`MAX_WAIT_FOR_COMMS` en `screens.c`). Se sube a 30 s. Menú: md5 b14b1e07568ee12203c628105530c286.
