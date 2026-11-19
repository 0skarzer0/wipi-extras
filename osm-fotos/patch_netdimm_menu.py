#!/usr/bin/env python3
"""Adds the game pictures to WiPi's netdimm_menu.py (DragonMinded's on-screen menu launcher).

Usage: python3 patch_netdimm_menu.py /sbin/piforce/dm_netboot/scripts/netdimm_menu.py

Keeps a copy of the original as netdimm_menu.py.orig_osm (only the first time) and can be
run again safely: it refuses a file that is already patched. The menu ROM must be the one
built from netbootmenu/ in this repository (config_t.thumbs_offset); the original menu
ignores the pictures, so the patched script also works with it.
"""
import os
import shutil
import sys

THUMBS_CODE = r'''

# --- Game pictures for the on-screen menu (dc2naomi/osm) -----------------------------
# Each game's picture is the PNG of its romsinfo.csv row (column 3) from WiPi's image
# folder, reduced to fit 256x256 and stored as zlib(RGB565). They are cached in
# OSM_THUMBS_CACHE so that only new or changed pictures are converted.
OSM_IMAGES_DIR = '/var/www/html/images'
OSM_THUMBS_CACHE = '/boot/config/osmthumbs'
OSM_THUMB_SIZE = 256


def osm_thumb(image: str, verbose: bool) -> Optional[Tuple[int, int, bytes]]:
    import zlib
    if not image:
        return None
    path = os.path.join(OSM_IMAGES_DIR, image)
    if not os.path.isfile(path):
        return None
    st = os.stat(path)
    cachename = os.path.join(OSM_THUMBS_CACHE, "{}.{}.{}.t1".format(image.replace('/', '_'), int(st.st_mtime), st.st_size))
    try:
        with open(cachename, "rb") as fp:
            data = fp.read()
        width, height = struct.unpack("<HH", data[:4])
        return width, height, data[4:]
    except (OSError, struct.error):
        pass
    try:
        from PIL import Image
    except ImportError:
        print("Pictures: python3-pil is not installed, menu without pictures")
        return None
    try:
        img = Image.open(path)
        img.load()
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            back = Image.new("RGBA", img.size, (0, 0, 0, 255))
            back.alpha_composite(img)
            img = back
        img = img.convert("RGB")
        img.thumbnail((OSM_THUMB_SIZE, OSM_THUMB_SIZE), Image.LANCZOS)
        width, height = img.size
        rgb = img.tobytes()
        out = bytearray(width * height * 2)
        j = 0
        for i in range(0, len(rgb), 3):
            pixel = ((rgb[i] >> 3) << 11) | ((rgb[i + 1] >> 2) << 5) | (rgb[i + 2] >> 3)
            out[j] = pixel & 0xFF
            out[j + 1] = pixel >> 8
            j += 2
        packed = zlib.compress(bytes(out), 9)
    except Exception as e:
        print(f"Pictures: could not convert {image}: {e}")
        return None
    try:
        os.makedirs(OSM_THUMBS_CACHE, exist_ok=True)
        for old in os.listdir(OSM_THUMBS_CACHE):
            if old.startswith(image.replace('/', '_') + ".") and old.endswith(".t1"):
                os.remove(os.path.join(OSM_THUMBS_CACHE, old))
        with open(cachename + ".tmp", "wb") as fp:
            fp.write(struct.pack("<HH", width, height) + packed)
        os.replace(cachename + ".tmp", cachename)
    except OSError as e:
        if verbose:
            print(f"Pictures: could not cache {image}: {e}")
    return width, height, packed


def osm_thumbs_blob(images: List[str], base: int, verbose: bool) -> bytes:
    """The block appended to the menu ROM at file offset base (see netbootmenu/thumbs.h)."""
    count = len(images)
    header_len = 8 + 12 * count
    entries = b""
    data = b""
    found = 0
    for image in images:
        thumb = osm_thumb(image, verbose)
        if thumb is None:
            entries += struct.pack("<IIHH", 0, 0, 0, 0)
            continue
        width, height, packed = thumb
        offset = base + header_len + len(data)
        entries += struct.pack("<IIHH", offset, len(packed), width, height)
        data += packed
        while len(data) & 3:
            data += b"\0"
        found += 1
    print(f"Pictures: {found} of {count} games")
    return b"THM1" + struct.pack("<I", count) + entries + data
# --------------------------------------------------------------------------------------
'''

EDITS = [
    # The image column of romsinfo.csv goes with each game.
    ("filedict[row[1]] = row[4], row[16], row[14], row[0], row[12]",
     "filedict[row[1]] = row[4], row[16], row[14], row[0], row[12], row[2]"),
    ("games: List[Tuple[str, str, bytes, str]] = []",
     "games: List[Tuple[str, str, bytes, str, str]] = []"),
    ("games.append((fullname, value[0].replace(\"(\",\"\").replace(\")\",\"\"), \"{:<4}\".format(value[1]).encode(), value[2]))",
     "games.append((fullname, value[0].replace(\"(\",\"\").replace(\")\",\"\"), \"{:<4}\".format(value[1]).encode(), value[2], value[5]))"),
    ("for index, (filename, name, serial, openjvs) in enumerate(games):",
     "for index, (filename, name, serial, openjvs, image) in enumerate(games):"),
    # One more field at the end of config_t: where the pictures are.
    ("\"<IIIIIIIIBBBBBBBBBBBBIII\",",
     "\"<IIIIIIIIBBBBBBBBBBBBIIII\","),
    ("            force_players if (force_players is not None) else 0,\n        )",
     "            force_players if (force_players is not None) else 0,\n            0,\n        )"),
    # Append the pictures after the menu and point the config at them.
    ("""                menudata = add_or_update_section(FileBytes(fp), 0x0D000000, config, verbose=verbose)
""",
     """                menudata = add_or_update_section(FileBytes(fp), 0x0D000000, config, verbose=verbose)
                try:
                    # The config has the same size with any offset, so the ROM keeps its length.
                    menubytes = bytes(menudata[:])
                    base = (len(menubytes) + 3) & ~3
                    thumbs = osm_thumbs_blob([g[4] for g in games], base, verbose)
                    config = config[:56] + struct.pack("<I", base) + config[60:]
                    fp.seek(0)
                    menubytes = bytes(add_or_update_section(FileBytes(fp), 0x0D000000, config, verbose=verbose)[:])
                    menudata = menubytes + (b"\\0" * (base - len(menubytes))) + thumbs
                except Exception as e:
                    print(f"Pictures: disabled ({e})")
"""),
]

ANCHOR = "\ndef main() -> int:"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    path = sys.argv[1]
    with open(path, encoding="utf-8") as fp:
        text = fp.read()
    if "osm_thumbs_blob" in text:
        print("Already patched")
        return 0
    for old, new in EDITS:
        if text.count(old) != 1:
            print(f"Not found exactly once, WiPi's netdimm_menu.py changed?\n  {old.strip()[:90]}")
            return 1
        text = text.replace(old, new)
    if text.count(ANCHOR) != 1:
        print("main() not found")
        return 1
    text = text.replace(ANCHOR, THUMBS_CODE + ANCHOR)
    backup = path + ".orig_osm"
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
    with open(path + ".tmp", "w", encoding="utf-8") as fp:
        fp.write(text)
    os.replace(path + ".tmp", path)
    print(f"Patched {path} (original in {backup})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
