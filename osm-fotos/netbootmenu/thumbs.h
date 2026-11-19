#ifndef __THUMBS_H
#define __THUMBS_H

#ifdef __cplusplus
extern "C" {
#endif

#include <naomi/ta.h>

// Picture of the selected game, shown on the right of the game list.
//
// The host (netdimm_menu.py) appends the pictures to the end of the menu ROM, after
// everything the BIOS loads, and puts their position in config_t.thumbs_offset.
// They are read from the DIMM with cart_read() only when needed, so the number of
// games does not use up main or video memory.
//
// Format (all little endian), at thumbs_offset in the ROM:
//   char magic[4] = "THM1"
//   uint32_t count                 same as the number of games in the list
//   entry[count]:
//     uint32_t offset              position of the picture in the ROM, 0 = no picture
//     uint32_t length              zlib-compressed length
//     uint16_t width, height       at most THUMB_SIZE x THUMB_SIZE
//   pictures: zlib(RGB565 pixels, width * height, rows top to bottom)

#define THUMB_SIZE 256

// Returns nonzero if the host sent any pictures.
int thumbs_init(unsigned int games_count);

// Picture for a game; 0 if it has none. Sets *width and *height to the picture size
// inside the THUMB_SIZE square texture.
texture_description_t *thumbs_get(unsigned int game, int *width, int *height);

#ifdef __cplusplus
}
#endif

#endif
