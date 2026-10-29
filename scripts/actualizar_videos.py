#!/usr/bin/env python3
"""Guarda en datos/videos.json los últimos vídeos del canal de YouTube.

Lee la lista pública del canal (RSS de YouTube, no necesita claves) y deja los 6
más recientes, sin el directo 24/7, que tiene su propia sección en la web.
Lo ejecuta GitHub Actions una vez al día (.github/workflows/videos.yml).
"""
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

CANAL = "UCba5HqD3ftT7QIRCyMqfXyA"  # @enkmina2
CUANTOS = 6
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "datos", "videos.json")
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "media": "http://search.yahoo.com/mrss/"}


def main():
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CANAL}"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
        raiz = ET.fromstring(r.read())
    videos = []
    for e in raiz.findall("a:entry", NS):
        titulo = e.findtext("a:title", "", NS).strip()
        if "24/7" in titulo:  # el directo ya tiene su sección
            continue
        vid = e.findtext("yt:videoId", "", NS)
        corto = "#shorts" in titulo.lower()
        videos.append({
            "id": vid,
            "titulo": titulo.replace("#Shorts", "").replace("#shorts", "").strip(),
            "fecha": e.findtext("a:published", "", NS)[:10],
            "corto": corto,
            "enlace": f"https://www.youtube.com/{'shorts/' + vid if corto else 'watch?v=' + vid}",
        })
        if len(videos) == CUANTOS:
            break
    if not videos:
        sys.exit("YouTube no devolvió vídeos; no se toca el archivo")
    nuevo = json.dumps({"canal": CANAL, "videos": videos}, ensure_ascii=False, indent=1)
    if os.path.exists(SALIDA) and open(SALIDA, encoding="utf-8").read() == nuevo:
        print("Sin vídeos nuevos")
        return
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(nuevo)
    print(f"Actualizados {len(videos)} vídeos; el último: {videos[0]['titulo']}")


if __name__ == "__main__":
    main()
