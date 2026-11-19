#!/usr/bin/env python3
"""Makes WiPi send the *_dc2naomi* images with dc2naomi_send.py (each game's Visual Memory in a .vmu file).

Usage: python3 patch_wipiloader.py /sbin/piforce/wipiloader.py

Keeps a copy of the original as wipiloader.py.orig (only the first time). Running it again on a patched file does
nothing. Games that are not *_dc2naomi* are sent exactly as before.
"""
import os
import shutil
import sys

OLD = """    loaderCommand = 'sudo python3 /sbin/piforce/dm_netboot/netdimm_send '+activedimm+' '+romfile+' --disable-crc'
    os.system(loaderCommand)
"""

NEW = """    # dc2naomi: Dreamcast games keep their Visual Memory in JUEGO_dc2naomi.vmu next to the image
    # (https://github.com/0skarzer0/wipi-extras, vmu/). The original file is wipiloader.py.orig
    if exists('/sbin/piforce/dc2naomi_vmu.py'):
        os.system('sudo python3 /sbin/piforce/dc2naomi_vmu.py stop '+activedimm)
    if '_dc2naomi' in romfile and exists('/sbin/piforce/dc2naomi_send.py'):
        loaderCommand = 'sudo python3 /sbin/piforce/dc2naomi_send.py '+activedimm+' '+romfile
    else:
        loaderCommand = 'sudo python3 /sbin/piforce/dm_netboot/netdimm_send '+activedimm+' '+romfile+' --disable-crc'
    os.system(loaderCommand)
"""


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    path = sys.argv[1]
    with open(path, encoding="utf-8") as fp:
        text = fp.read()
    if "dc2naomi_send.py" in text:
        print("Already patched")
        return 0
    if text.count(OLD) != 1:
        print("The netdimm_send lines were not found exactly once: WiPi's wipiloader.py changed?")
        return 1
    text = text.replace(OLD, NEW)
    if "def exists(" not in text and "import exists" not in text:
        text = "from os.path import exists\n" + text if not text.startswith("#!") else \
            text.replace("\n", "\nfrom os.path import exists\n", 1)
    backup = path + ".orig"
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
    with open(path + ".tmp", "w", encoding="utf-8") as fp:
        fp.write(text)
    os.replace(path + ".tmp", path)
    print(f"Patched {path} (original in {backup})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
