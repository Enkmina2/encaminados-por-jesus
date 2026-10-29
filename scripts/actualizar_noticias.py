#!/usr/bin/env python3
"""Guarda en datos/noticias.json los últimos titulares de las fuentes aprobadas.

Solo el título, la fecha, el nombre de la fuente y el enlace a la noticia original:
no se copia ningún texto de los artículos. Lo ejecuta GitHub Actions cada día.
Para añadir una fuente: apruébala antes y añádela a FUENTES (nombre y su RSS).
"""
import email.utils
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

FUENTES = [
    ("Actualidad Evangélica", "https://actualidadevangelica.es/feed/"),
]
CUANTOS = 8
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "datos", "noticias.json")


def leer(nombre, url):
    pet = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (encaminados-por-jesus)"})
    with urllib.request.urlopen(pet, timeout=30) as r:
        raiz = ET.fromstring(r.read())
    for item in raiz.findall(".//item"):
        titulo, enlace = (item.findtext("title") or "").strip(), (item.findtext("link") or "").strip()
        if not titulo or not enlace.startswith("https://"):
            continue
        fecha = item.findtext("pubDate")
        fecha = email.utils.parsedate_to_datetime(fecha).date().isoformat() if fecha else ""
        yield {"titulo": titulo, "enlace": enlace, "fuente": nombre, "fecha": fecha}


def main():
    titulares = []
    for nombre, url in FUENTES:
        try:
            titulares += list(leer(nombre, url))
        except Exception as e:  # si una fuente falla, no se pierden las demás
            print(f"{nombre}: no se pudo leer ({e})")
    if not titulares:
        sys.exit("Ninguna fuente respondió; no se toca el archivo")
    titulares.sort(key=lambda t: t["fecha"], reverse=True)
    datos = {"instrucciones": "Lo genera scripts/actualizar_noticias.py cada día. No editar a mano.",
             "fuentes": [n for n, _ in FUENTES], "titulares": titulares[:CUANTOS]}
    nuevo = json.dumps(datos, ensure_ascii=False, indent=1)
    if os.path.exists(SALIDA) and open(SALIDA, encoding="utf-8").read() == nuevo:
        print("Sin titulares nuevos")
        return
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(nuevo)
    print(f"{len(datos['titulares'])} titulares; el último: {titulares[0]['titulo']}")


if __name__ == "__main__":
    main()
