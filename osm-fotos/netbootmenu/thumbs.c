#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <zlib.h>
#include <naomi/cart.h>
#include <naomi/ta.h>
#include "config.h"
#include "thumbs.h"

// Bytes read from the cart at a time with interrupts disabled (see thumbs_load).
#define THUMB_READ_CHUNK 512

typedef struct __attribute__((__packed__))
{
    uint32_t offset;
    uint32_t length;
    uint16_t width;
    uint16_t height;
} thumb_entry_t;

static thumb_entry_t *entries = 0;
static unsigned int entry_count = 0;

// Two textures: the one on screen is never rewritten while it may still be drawn.
static texture_description_t *textures[2] = { 0, 0 };
static int texture_game[2] = { -1, -1 };
static int texture_width[2];
static int texture_height[2];
static int next_texture = 0;

static uint16_t *pixels = 0;
static uint8_t *packed = 0;
static unsigned int packed_size = 0;

int thumbs_init(unsigned int games_count)
{
    config_t *config = get_config();
    if (config->thumbs_offset == 0 || games_count == 0)
    {
        return 0;
    }

    uint32_t header[2];
    cart_read(header, config->thumbs_offset, sizeof(header));
    if (memcmp(&header[0], "THM1", 4) != 0 || header[1] != games_count)
    {
        printf("Pictures: bad header at %08lX\n", config->thumbs_offset);
        return 0;
    }

    entries = malloc(sizeof(thumb_entry_t) * games_count);
    pixels = malloc(THUMB_SIZE * THUMB_SIZE * 2);
    if (entries == 0 || pixels == 0)
    {
        return 0;
    }
    cart_read(entries, config->thumbs_offset + 8, sizeof(thumb_entry_t) * games_count);
    entry_count = games_count;

    for (int i = 0; i < 2; i++)
    {
        void *vram = ta_texture_malloc(THUMB_SIZE, 16);
        if (vram == 0)
        {
            entry_count = 0;
            return 0;
        }
        textures[i] = ta_texture_desc_direct(vram, THUMB_SIZE, TA_TEXTUREMODE_RGB565);
    }

    return 1;
}

texture_description_t *thumbs_get(unsigned int game, int *width, int *height)
{
    if (game >= entry_count)
    {
        return 0;
    }

    for (int i = 0; i < 2; i++)
    {
        if (texture_game[i] == (int)game)
        {
            *width = texture_width[i];
            *height = texture_height[i];
            return textures[i];
        }
    }

    thumb_entry_t *entry = &entries[game];
    if (entry->offset == 0 || entry->width == 0 || entry->height == 0 || entry->width > THUMB_SIZE || entry->height > THUMB_SIZE)
    {
        return 0;
    }

    if (entry->length > packed_size)
    {
        free(packed);
        packed_size = (entry->length + 4095) & ~4095;
        packed = malloc(packed_size);
        if (packed == 0)
        {
            packed_size = 0;
            return 0;
        }
    }

    // The DIMM is read in whole 32-bit words.
    // cart_read() keeps interrupts disabled for the whole read, and the net dimm talks to us
    // (peek/poke of the message registers) through interrupts. Reading a big picture in one go
    // starves it and the menu ends in "Communication Error!", so read it in small pieces.
    {
        uint32_t total = (entry->length + 3) & ~3;
        uint32_t done = 0;
        while (done < total)
        {
            uint32_t chunk = total - done;
            if (chunk > THUMB_READ_CHUNK) { chunk = THUMB_READ_CHUNK; }
            cart_read((uint8_t *)packed + done, entry->offset + done, chunk);
            done += chunk;
        }
    }

    // Unpack straight into the top left corner of the square texture.
    static uint16_t row[THUMB_SIZE];
    z_stream stream;
    memset(&stream, 0, sizeof(stream));
    if (inflateInit(&stream) != Z_OK)
    {
        return 0;
    }
    stream.next_in = packed;
    stream.avail_in = entry->length;

    memset(pixels, 0, THUMB_SIZE * THUMB_SIZE * 2);
    int ok = 1;
    for (int y = 0; y < entry->height && ok; y++)
    {
        stream.next_out = (uint8_t *)row;
        stream.avail_out = entry->width * 2;
        int ret = inflate(&stream, Z_SYNC_FLUSH);
        if ((ret != Z_OK && ret != Z_STREAM_END) || stream.avail_out != 0)
        {
            ok = 0;
            break;
        }
        memcpy(&pixels[y * THUMB_SIZE], row, entry->width * 2);
    }
    inflateEnd(&stream);
    if (!ok)
    {
        printf("Pictures: game %d is corrupt\n", game);
        entry->offset = 0;
        return 0;
    }

    int which = next_texture;
    next_texture = 1 - next_texture;
    ta_texture_load(textures[which]->vram_location, THUMB_SIZE, 16, pixels);
    texture_game[which] = game;
    texture_width[which] = entry->width;
    texture_height[which] = entry->height;

    *width = entry->width;
    *height = entry->height;
    return textures[which];
}
