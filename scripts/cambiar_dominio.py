#!/usr/bin/env python3
"""Cambia la dirección de la web cuando tengas tu propio dominio.

Uso:  python scripts/cambiar_dominio.py encaminadosporjesus.com

Sustituye la dirección actual (https://enkmina2.github.io/encaminados-por-jesus/)
por https://TU-DOMINIO/ en index.html, sitemap.xml y robots.txt, y crea el
archivo CNAME que GitHub Pages necesita. Las imágenes, fuentes y datos usan
rutas relativas, así que no hay que tocarlos.

Después: configurar el DNS del dominio y GitHub Pages (pasos en CLAUDE.md).
"""
import os
import re
import sys

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ARCHIVOS = ["index.html", "sitemap.xml", "robots.txt"]


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"[a-z0-9-]+(\.[a-z0-9-]+)+", sys.argv[1].lower()):
        sys.exit("Uso: python scripts/cambiar_dominio.py encaminadosporjesus.com")
    dominio = sys.argv[1].lower()
    nueva = f"https://{dominio}/"
    with open(os.path.join(RAIZ, "index.html"), encoding="utf-8") as f:
        actual = re.search(r'<link rel="canonical" href="([^"]+)"', f.read()).group(1)
    if actual == nueva:
        sys.exit(f"La web ya usa {nueva}")
    for nombre in ARCHIVOS:
        ruta = os.path.join(RAIZ, nombre)
        with open(ruta, encoding="utf-8") as f:
            texto = f.read()
        n = texto.count(actual)
        with open(ruta, "w", encoding="utf-8", newline="\n") as f:
            f.write(texto.replace(actual, nueva))
        print(f"{nombre}: {n} cambios")
    with open(os.path.join(RAIZ, "CNAME"), "w", encoding="utf-8") as f:
        f.write(dominio + "\n")
    print(f"CNAME creado con {dominio}. Dirección nueva: {nueva}")


if __name__ == "__main__":
    main()
