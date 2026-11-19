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
