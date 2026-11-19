#!/usr/bin/env python3
"""Hace que /sbin/piforce/menulauncher.py (WiPi) cierre los netdimm_menu que ya estén corriendo
antes de lanzar uno nuevo en modo normal.

Sin esto, cada vez que se pide "lanzar menú" (web, arranque, LCD) queda otra instancia más
hablando con la misma NetDIMM y el menú de la NAOMI acaba en "Communication Error!".
Es idempotente y guarda menulauncher.py.orig la primera vez. Uso: sudo python3 patch_menulauncher.py
"""
import os, shutil, sys
P = "/sbin/piforce/menulauncher.py"
MARK = "# wipi-extras: cerrar instancias previas"
s = open(P).read()
if MARK in s:
    # versión anterior del parche (su pgrep se encontraba a sí mismo): se corrige
    s2 = s.replace("pgrep -f dm_netboot/netdimm_menu", "pgrep -f [d]m_netboot/netdimm_menu")
    if s2 != s:
        open(P + ".tmp", "w").write(s2); os.replace(P + ".tmp", P); print("parche corregido")
    else:
        print("ya estaba parcheado")
    sys.exit(0)
old = "    print(\"Starting netdimm_menu script in default mode\")\n"
if s.count(old) != 1:
    print("no encuentro el punto a parchear; no toco nada"); sys.exit(1)
new = old + ("    " + MARK + "\n"
             "    os.system(\"for p in $(pgrep -f [d]m_netboot/netdimm_menu); do kill -9 $p; done\")\n"
             "    sleep(1)\n")
if not os.path.exists(P + ".orig"):
    shutil.copy2(P, P + ".orig")
open(P + ".tmp", "w").write(s.replace(old, new))
os.replace(P + ".tmp", P)
print("parcheado")
