#!/usr/bin/env python3
"""Mantenimiento de ROMs y romsinfo.csv de WiPi (wipi-extras). Uso: python3 mant.py PLAN.json [--apply]
PLAN: {"borrar": [ficheros de /boot/roms], "borrar_vmu_huerfanas": true, "borrar_temporales": true,
       "filas_nuevas": [fila csv completa en texto], "imagen": {rom: png}, "copiar_png": [png en la carpeta del script],
       "quitar_filas_sin_rom": true}
Copia los CSV a romsinfo.csv.bak_mant-AAAAMMDD-HHMMSS antes de tocarlos. Las líneas que no cambian quedan byte a byte igual."""
import csv, glob, io, json, os, shutil, sys, time
R = "/boot/roms"; IMG = "/boot/config/images"
CSVS = ["/boot/config/romsinfo.csv", "/var/www/html/csv/romsinfo.csv"]
plan = json.load(open(sys.argv[1])); apply = "--apply" in sys.argv; here = os.path.dirname(os.path.abspath(sys.argv[1]))
def rm(p):
    print(("BORRO " if apply else "borraría ") + p + "  (%d bytes)" % os.path.getsize(p))
    if apply: os.remove(p)
for f in plan.get("borrar", []):
    p = os.path.join(R, f)
    if os.path.exists(p): rm(p)
    else: print("no existe:", f)
if plan.get("borrar_temporales"):
    for p in sorted(glob.glob(R + "/*.tmp") + glob.glob(R + "/*.old-*") + glob.glob(R + "/*.old")): rm(p)
if plan.get("borrar_vmu_huerfanas"):
    for p in sorted(glob.glob(R + "/*.vmu")):
        base = p[:-4]
        if not os.path.exists(base + ".bin.gz") or os.path.basename(base) + ".bin.gz" in plan.get("borrar", []):
            rm(p)
for png in plan.get("copiar_png", []):
    print(("copio " if apply else "copiaría ") + png)
    if apply: shutil.copy2(os.path.join(here, png), os.path.join(IMG, png))
stamp = time.strftime("%Y%m%d-%H%M%S")
for path in CSVS:
    lines = open(path, "rb").read().decode("utf-8").splitlines(keepends=True)
    out = []; quitadas = 0; cambiadas = 0
    nl = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"
    present = set(r[1] for r in csv.reader(io.StringIO("".join(lines))) if len(r) > 1)
    for ln in lines:
        r = next(csv.reader(io.StringIO(ln)), [])
        if len(r) > 2 and r[1] != "romname":
            exists = os.path.exists(os.path.join(R, r[1])) and not (r[1] in plan.get("borrar", []))
            if plan.get("quitar_filas_sin_rom") and not exists:
                print("%s: quito fila %s | %s" % (path, r[1], r[4])); quitadas += 1; continue
            if r[1] in plan.get("imagen", {}) and r[2] != plan["imagen"][r[1]]:
                old = "," + r[1] + "," + r[2] + ","; new = "," + r[1] + "," + plan["imagen"][r[1]] + ","
                if ln.count(old) == 1: ln = ln.replace(old, new); cambiadas += 1; print("%s: imagen de %s -> %s" % (path, r[1], plan["imagen"][r[1]]))
        out.append(ln)
    if out and not out[-1].endswith(("\n", "\r")): out[-1] += nl
    for row in plan.get("filas_nuevas", []):
        rom = next(csv.reader(io.StringIO(row)))[1]
        if rom in present: print("%s: ya hay fila de %s" % (path, rom)); continue
        out.append(row + nl); print("%s: añado %s" % (path, rom)); cambiadas += 1
    print("%s: %d filas quitadas, %d cambios" % (path, quitadas, cambiadas))
    if apply and (quitadas or cambiadas):
        shutil.copy2(path, path + ".bak_mant-" + stamp)
        open(path + ".tmpw", "wb").write("".join(out).encode("utf-8")); os.replace(path + ".tmpw", path)
