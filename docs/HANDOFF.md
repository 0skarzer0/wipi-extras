# HANDOFF: estado, montaje y trampas

Para retomar el trabajo en otra sesión (Claude u otra persona).

## Montaje del usuario

- **Mueble Crazy Taxi (NAOMI 2, volante):** Raspberry con WiPi en `192.168.68.251` (antes `.60`; se cambió el
  2026-11-19 porque otro aparato de la red cogía la `.60`), NetDIMM en `10.0.0.4`.
- **Mueble estándar (palancas):** Raspberry en `192.168.68.250`, NetDIMM en `10.0.0.3`.
- Usuario `root`. La contraseña la da el usuario (`info.txt` de su carpeta `Documents\dc2naomi`); **nunca** se
  escribe en el repositorio.
- Las Raspberry no tienen salida a Internet (no resuelven `github.com`) ni reloj: la hora sale de 2022 (tar avisa de
  fechas «en el futuro»: no pasa nada). Para llevar el repositorio, un `.tgz` subido por SSH.
- Desde la sesión se llega a ellas por SSH a través de la app de escritorio (carpeta `dc2naomi` conectada).

## Estado (2026-11-19)

- **osm-fotos:** instalado y probado en la Pi del Crazy Taxi: «está perfecto». 54 juegos, 53 con foto. Después se
  pasó `./install.sh osm` y `./install.sh vmu` (repo copiado en `/root/wipi-extras`): `netbootmenu.bin`, `.fotos` y
  `.dark` son el menú con fotos (con el tema oscuro se conservan) y los originales están en `*.orig_osm`.
  Instalado también en la `.250` (mueble estándar) el mismo día con `./install.sh osm`: 169 juegos en el menú,
  139 con foto; las 30 sin foto son conversiones de Dreamcast con la columna de la imagen vacía en el CSV. Las fotos
  ya quedaron convertidas en caché (la primera vez, 68 s en esa Pi). El menú que estaba abierto en ese momento sigue
  siendo el viejo hasta que WiPi lo vuelva a lanzar.
- **Fotos de las conversiones de Dreamcast (2026-11-19, tarde):** capturas de partida de libretro-thumbnails en los
  juegos `dc-*` sin imagen: 28 en la `.250` y 1 en la `.251` (ver `osm-fotos/imagenes/README.md`). Ahora todos los
  juegos del menú tienen foto (`.251`: 54 de 54; `.250`: 167 de 169) salvo `dc-robocop_dncd` y `dc-robocop_con`. Los
  PNG nuevos se llaman `dc-<juego>.png` en `/boot/config/images`; copias de los CSV en `romsinfo.csv.bak_osmfotos`.
  El usuario pidió capturas de gameplay, no logos; el resto de juegos (NAOMI/Atomiswave) conservan los logos del WiPi.
- **vmu:** instalado en las dos Raspberry (desde dc2naomi, 2026-11-10); los scripts de aquí son idénticos.
- **initiald-cards:** sin empezar.

## Trampas aprendidas

- **Subir ficheros por SSH:** un envoltorio de `ssh` que redirige la entrada a `/dev/null` (para que no se quede
  esperando) **sube ficheros vacíos** si se usa con `cat > fichero`. Le pasó al menú el 2026-11-19: el
  `netbootmenu.bin` quedó vacío un minuto. Para subir, un `ssh ... "cat > X" < local` sin otra redirección, y comprobar
  siempre el md5 en la Pi antes de usar el fichero.
- **`pkill -f netdimm_menu` por SSH** se mata a sí mismo (la orden remota contiene el texto). Usar un patrón que no
  aparezca en la propia orden (por ejemplo `pkill -f "[n]etdimm_menu"`).
- **Lanzar el menú a mano** (reinicia la placa con el menú):
  `setsid nohup python3 /sbin/piforce/dm_netboot/netdimm_menu 10.0.0.4 /boot/roms --verbose > /root/osm.log 2>&1 < /dev/null &`.
  El registro sale vacío un buen rato: Python lo guarda en búfer.
- **Tema del menú:** `switchmode.py` de WiPi copia `netbootmenu.bin.light` o `.dark` encima de `netbootmenu.bin`.
- **Código de DragonMinded:** `DragonMinded/netboot` y `DragonMinded/libnaomi` han desaparecido de GitHub
  (noviembre de 2026). En la Pi solo está el menú compilado. Copias usadas: `ArcadeHustle/netboot` (`2008fa7`) y
  `sega-dreamcast/libnaomi` (`f32c2f4`).
- **Toolchain de libnaomi:** `setup/download.sh`, `unpack.sh` y `make CFLAGS="-O2 -fpermissive"
  CXXFLAGS="-O2 -fpermissive -std=gnu++14"` (con GCC 13 del sistema; unos 45 min con 2 núcleos). Hace falta `texinfo`.
  Luego `make -C 3rdparty/{zlib,libbz2,libpng,freetype} install` (zlib 1.2.12 hay que bajarlo de
  `https://zlib.net/fossils/` a `3rdparty/zlib/download/`) y volver a compilar e instalar libnaomi.
- El `netdimm_menu.py` de WiPi lee `/var/www/html/csv/romsinfo.csv`: entran los juegos NAOMI/Atomiswave con la
  columna 13 a `Yes` y la imagen en `/boot/roms`; la foto es la columna 3.

## Ideas pendientes

- Foto para los dos RoboCop (`dc-robocop_dncd`, `dc-robocop_con`): no hay en ninguna base; el usuario debe pasar una
  imagen o decidir cuál usar.
- Versión clara del menú con fotos: el binario `.light` de WiPi se diferencia del `.dark` en pocos bytes (seguramente
  los colores; sin comprobar).
- Que dc2naomi tome los scripts de la VMU de aquí, para no tener dos copias.
- Tarjetas de Initial D.

## 2026-11-19: previews para todos
Ver `osm-fotos/imagenes/README.md` (sección "Previews de TODOS los juegos"). Estado: .250 170/170 y .251 54/54 con foto, salvo
`h-jvstest` (.251, logo) y los 4 roms sin captura. Trampas: `device_bash` limita a 45 s y mata lo que queda en segundo plano; subir ficheros
grandes en trozos de 4 MB con `put*.sh` y unir con `cat`; no usar `grep csv` sobre la salida del script (470 líneas).

## 2026-11-19: "Communication Error!" en las dos NAOMI
Había varias instancias de `netdimm_menu` a la vez (WiPi no cierra la anterior en modo normal). Se arregló con `fixes/patch_menulauncher.py`
(aplicado en .250 y .251) y se dejó una sola instancia en cada Pi. Ver `fixes/README.md`.
Segunda causa (al elegir juego): lectura de la foto con `cart_read` de una vez = interrupciones desactivadas demasiado tiempo.
Se lee en trozos de 512 B (ver `fixes/README.md`). Menú nuevo instalado en .250 y .251.
CAUSA REAL: protocolo de mensajes. WiPi usa checksums sin semilla; la libnaomi nueva usa semillas 3/7/19. Se compila libnaomi con
semillas 0 (`osm-fotos/libnaomi-patch/`). Si se recompila el menú, NO olvidar este parche o el menú no podrá cargar juegos.
