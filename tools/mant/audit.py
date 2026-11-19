import csv, os, re, collections, json
R = "/boot/roms"; I = "/var/www/html/images"
roms = {f: os.path.getsize(os.path.join(R, f)) for f in os.listdir(R) if os.path.isfile(os.path.join(R, f))}
gamefiles = {f: s for f, s in roms.items() if re.search(r"\.(bin|gz|zip|dat|lst|7z)$", f, re.I) or f.endswith(".bin.gz")}
others = sorted(f for f in roms if f not in gamefiles)
a = open("/boot/config/romsinfo.csv", "rb").read(); b = open("/var/www/html/csv/romsinfo.csv", "rb").read()
rows = [r for r in csv.reader(open("/var/www/html/csv/romsinfo.csv", newline="")) if len(r) > 12]
byrom = collections.defaultdict(list)
for r in rows: byrom[r[1]].append(r)
out = {"csv_iguales": a == b, "roms": len(gamefiles), "filas_csv": len(rows)}
out["rom_sin_fila"] = sorted(f for f in gamefiles if f not in byrom)
out["fila_repetida"] = sorted(f for f, v in byrom.items() if len(v) > 1 and f in gamefiles)
menu = [(f, byrom[f][0]) for f in sorted(gamefiles) if f in byrom]
out["fuera_del_menu_osm_no"] = sorted(f for f, r in menu if r[12] != "Yes")
out["sin_imagen"] = sorted(f for f, r in menu if not r[2] or not os.path.isfile(os.path.join(I, r[2])))
out["imagen_no_preview"] = sorted((f, r[2]) for f, r in menu if r[2] and not (r[2].startswith("pv-") or r[2].startswith("dc-")))
names = collections.defaultdict(list)
for f, r in menu: names[r[4].strip().lower()].append(f)
out["mismo_nombre"] = {k: v for k, v in names.items() if len(v) > 1}
sizes = collections.defaultdict(list)
for f in gamefiles: sizes[gamefiles[f]].append(f)
out["mismo_tamano"] = [v for v in sizes.values() if len(v) > 1]
imgs = collections.defaultdict(list)
for f, r in menu: imgs[r[2]].append((f, r[4]))
out["misma_imagen"] = {k: v for k, v in imgs.items() if len(v) > 1}
out["otros_ficheros"] = others[:40]
print(json.dumps(out, ensure_ascii=False, indent=0))
