# Visual Memory (VMU) en ficheros, con WiPi Netbooter

Los juegos convertidos con la VMU emulada guardan en una tarjeta que vive en la memoria de la NAOMI y se pierde al
apagar. Con estos dos scripts en la Raspberry del netbooter, cada juego tiene su tarjeta en un fichero junto a su
imagen y no se pierde nada:

```
/boot/roms/nmus7_dc2naomi.bin.gz     la imagen
/boot/roms/nmus7_dc2naomi.vmu        su Visual Memory (128 KB; se crea sola la primera vez que el juego guarda)
```

El `.vmu` es un volcado plano de la tarjeta, el mismo formato que usan los emuladores: se puede copiar, guardar
como copia de seguridad o cambiar por otro.

## Cómo funciona

- **Al cargar el juego**, `dc2naomi_send.py` hace lo mismo que `netdimm_send` y, de paso, mete el `.vmu` en el hueco
  que la imagen reserva para la tarjeta (si aún no hay fichero, una tarjeta vacía formateada). El loader la copia a
  la memoria antes de arrancar el juego.
- **Mientras se juega**, `dc2naomi_vmu.py` se queda vigilando: el residente cuenta las escrituras en la tarjeta y
  cuando el juego termina de guardar, el script lee por la NetDIMM solo los bloques que han cambiado y actualiza el
  fichero. Tarda unos 2 segundos por bloque (un guardado de 10 bloques, unos 20 s; uno de 24, cerca de un minuto).
- **Al cargar otro juego**, se hace una última comprobación antes de enviarlo.

**Si se apaga el mueble justo después de guardar, antes de que el fichero se actualice, ese guardado se pierde.**
Registro: `/var/log/dc2naomi_vmu.log`.

## Instalación

Probado con WiPi Netbooter en una Raspberry (Python 3.7), NAOMI 2 y NetDIMM 3.17.

Con el instalador del repositorio: `sudo ./install.sh vmu` (copia los dos scripts a `/sbin/piforce/` y cambia en
`/sbin/piforce/wipiloader.py`, guardando antes `wipiloader.py.orig`, las dos líneas que envían el juego). Volver atrás:
`sudo ./install.sh undo-vmu`.

A mano:
1. Copiar `dc2naomi_send.py` y `dc2naomi_vmu.py` a `/sbin/piforce/`.
2. `python3 patch_wipiloader.py /sbin/piforce/wipiloader.py`: cambia

   ```python
       loaderCommand = 'sudo python3 /sbin/piforce/dm_netboot/netdimm_send '+activedimm+' '+romfile+' --disable-crc'
       os.system(loaderCommand)
   ```

   por

   ```python
       if exists('/sbin/piforce/dc2naomi_vmu.py'):
           os.system('sudo python3 /sbin/piforce/dc2naomi_vmu.py stop '+activedimm)
       if '_dc2naomi' in romfile and exists('/sbin/piforce/dc2naomi_send.py'):
           loaderCommand = 'sudo python3 /sbin/piforce/dc2naomi_send.py '+activedimm+' '+romfile
       else:
           loaderCommand = 'sudo python3 /sbin/piforce/dm_netboot/netdimm_send '+activedimm+' '+romfile+' --disable-crc'
       os.system(loaderCommand)
   ```

   Los juegos que no son `*_dc2naomi*` se envían exactamente como antes. Una actualización de WiPi puede deshacer
   este cambio: hay que volver a ponerlo.
3. La imagen tiene que llevar la VMU y su hueco. El conversor de dc2naomi lo pone al crearla, y a una imagen ya hecha
   se lo añade `tools/addvmu.py JUEGO.bin.gz NUEVO.bin.gz app/loader.bin`, en el repositorio
   [dc2naomi](https://github.com/0skarzer0/dc2naomi). Una imagen sin hueco se envía sin tocar.

Sin WiPi: `python3 dc2naomi_send.py IP JUEGO_dc2naomi.bin.gz` (necesita las herramientas de netboot de
DragonMinded, que WiPi trae en `/sbin/piforce/dm_netboot`).

Instalado y en uso en las dos Raspberry del usuario (mueble Crazy Taxi y mueble estándar), 2026-11-10.

## De dónde vienen estos scripts

Son los de la carpeta [`wipi/` de dc2naomi](https://github.com/0skarzer0/dc2naomi/tree/main/wipi) (commit `5d02e67`,
idénticos a los instalados en las dos Raspberry el 2026-11-19). dc2naomi los sigue usando para construir su programa
de Windows y meterlos en su zip, así que **un cambio en uno hay que llevarlo al otro** hasta que dc2naomi pase a
tomarlos de aquí.

Agradecimientos: el formato de la tarjeta y las respuestas maple siguen las de **Flycast**; para entender la VMU
sirvieron también [MaplePad](https://github.com/mackieks/MaplePad) (mackieks),
[libevmu](https://github.com/gyrovorbis/libevmu) (Falco Girgis), [dcvmu-tool](https://github.com/bucanero/dcvmu-tool)
(bucanero), [waterbear](https://github.com/wtetzner/waterbear) (wtetzner) y [chao](https://github.com/lordbananza/chao)
(lordbananza). El script de vigilancia está hecho a imagen del `timehack.py` de WiPi, y el envío usa las herramientas
de netboot de **DragonMinded** que trae WiPi.
