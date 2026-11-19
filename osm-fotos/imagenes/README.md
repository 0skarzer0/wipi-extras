# Fotos para los juegos que no las traen (conversiones de Dreamcast)

El menú enseña la imagen de la columna 3 de `romsinfo.csv`. Las conversiones de dc2naomi (`dc-*_dc2naomi.bin.gz`)
no tenían, así que se les han puesto **capturas de partida** sacadas de la base de miniaturas de RetroArch,
como hacen los scrapers de los emuladores.

## Receta (2026-11-19)

1. En un PC con Internet: `./fetch_libretro.sh mapa-dc2naomi.tsv /tmp/imgs` baja las capturas
   (`Named_Snaps` de [libretro-thumbnails/Sega_-_Dreamcast](https://github.com/libretro-thumbnails/Sega_-_Dreamcast))
   y las deja con el nombre `dc-<juego>.png`. Con un tercer argumento se pueden pedir logos (`Named_Logos`),
   pantallas de título (`Named_Titles`) o carátulas (`Named_Boxarts`).
2. Mirar las imágenes (que sean del juego y de la versión correcta; el mapa elige la región cuyo título coincide).
3. Subir la carpeta y un `mapa.tsv` a la Raspberry y `python3 ../set_csv_images.py mapa.tsv carpeta --apply`
   (primero sin `--apply`, que solo enseña lo que haría; con `--replace` sustituye imágenes ya puestas).
   Copia los PNG a `/boot/config/images`, rellena la columna 3 de las dos copias del CSV y guarda
   `romsinfo.csv.bak_osmfotos`.
4. La caché de fotos del menú (`/boot/config/osmthumbs/`) se rehace sola la próxima vez que WiPi lanza el menú.

## Hecho

- Pi del mueble de palancas (`.250`): 28 juegos. Pi del Crazy Taxi (`.251`): 1 (Sega Rally 2).
  Quedan sin foto los dos RoboCop (`dc-robocop_dncd` y `dc-robocop_con`): son proyectos propios y no están en
  ninguna base.
- Las capturas de Karous, Radirgy y los shoot'em up verticales salen con barras negras a los lados (la pantalla
  vertical dentro de una captura 4:3); es así en la base.
- Las imágenes no se guardan en este repositorio (son de sus autores); `mapa-dc2naomi.tsv` y el script las
  reproducen.

## Créditos

- **[libretro-thumbnails](https://github.com/libretro-thumbnails)** (el equipo de libretro/RetroArch y quienes
  aportan las capturas): de ahí salen las imágenes. Las capturas, logos y títulos pertenecen a sus respectivos
  autores y editores.
