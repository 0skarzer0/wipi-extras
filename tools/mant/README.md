# Mantenimiento de ROMs y CSV de WiPi

- `audit.py`: cruza `/boot/roms` con los dos `romsinfo.csv` y lista ROMs sin fila, filas sin ROM,
  juegos sin imagen o con logo en vez de captura, ficheros del mismo tamaño e imágenes compartidas.
- `mant.py PLAN.json [--apply]`: sin `--apply` solo enseña lo que haría. Borra ficheros, temporales (`*.tmp`, `*.old*`) y
  `.vmu` huérfanas (sin su `.bin.gz`), quita filas sin ROM, añade filas y cambia imágenes en los dos CSV
  (copia `romsinfo.csv.bak_mant-FECHA` antes). Las líneas que no cambian quedan byte a byte igual.

## Limpieza del 19-11-2026
- .250: borrados KOF XI normal (se deja el UNLOCKED) y un `.tmp` de Giant Gram 4 a medias (180 MB). Quitadas 8 filas sin ROM.
- .251: borrados OutRun 2006 c5, c6 y c7 (queda c8), el `.old` de Daytona, `dc-td6….vmu.tmp` y `sega_rally2_dc2naomi.vmu` (nombre
  antiguo, sin ROM). Quitadas 8 filas sin ROM. Añadidos Airline Pilots e Initial D (CTaxi, VCard). OutRun 2006 (`h-orc2c8`) pasa a la
  captura de OutRun 2 de Xbox (libretro-thumbnails `Microsoft_-_Xbox`). Airline Pilots: `Sega_-_Naomi`.
- `daytona_native_naomi.bin.gz` (.251) no se dio de alta: descomprimido es idéntico a `h-Daytona_USA_(MODEL2).bin.gz`.
