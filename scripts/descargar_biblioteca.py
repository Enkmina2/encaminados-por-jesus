#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descarga y prepara la biblioteca bíblica de dominio público del Maestro IA.

Fuentes (verificadas):
  - Reina-Valera 1909 (SpaRV) y King James (KJV): scrollmapper/bible_databases (dominio público)
  - Referencias cruzadas: OpenBible.info (licencia CC-BY, derivadas del Treasury of Scripture Knowledge)

Salida (un archivo por libro, para que el navegador cargue solo lo que necesita):
  datos/biblioteca/textos/rvr1909/GEN.json   ->  {"1": ["versículo 1", "versículo 2", ...], "2": [...]}
  datos/biblioteca/textos/kjv/GEN.json
  datos/biblioteca/referencias/GEN.json      ->  {"1.1": ["HEB.11.3", "JHN.1.1-JHN.1.3", ...]}

Las traducciones con derechos de autor (NVI, LBLA, ESV...) NO se incluyen.
Uso:  python scripts/descargar_biblioteca.py
"""

import csv
import io
import json
import urllib.request
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
BIB = BASE / "datos" / "biblioteca"
CACHE = BASE / "datos" / "biblioteca" / "_descargas"   # ignorada por git

RAW = "https://raw.githubusercontent.com/scrollmapper/bible_databases/master/formats/json/{}.json"
TEXTOS = {"rvr1909": "SpaRV", "kjv": "KJV"}
XREF_ZIP = "https://a.openbible.info/data/cross-references.zip"
REFS_POR_VERSO = 6

# Los 66 libros en orden canónico (los mismos IDs que libros.json)
IDS = ("GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG "
       "ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT "
       "ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV").split()

# Abreviaturas de OpenBible.info -> ID propio
OB = dict(zip(
    ("Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song "
     "Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal Matt Mark Luke John Acts "
     "Rom 1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas 1Pet 2Pet 1John 2John 3John "
     "Jude Rev").split(), IDS))


def descargar(url, destino):
    if destino.exists():
        return destino.read_bytes()
    print(f"  descargando {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        datos = r.read()
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(datos)
    return datos


def guardar(ruta, obj):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def textos():
    for clave, nombre in TEXTOS.items():
        print(f"Texto {clave} ({nombre})")
        datos = json.loads(descargar(RAW.format(nombre), CACHE / f"{nombre}.json"))
        libros = datos["books"]
        if len(libros) != 66:
            raise SystemExit(f"{nombre}: se esperaban 66 libros y hay {len(libros)}")
        total = 0
        for id_, libro in zip(IDS, libros):
            caps = {}
            for cap in libro["chapters"]:
                versos = sorted(cap["verses"], key=lambda v: v["verse"])
                caps[str(cap["chapter"])] = [v["text"].strip() for v in versos]
                total += len(versos)
            guardar(BIB / "textos" / clave / f"{id_}.json", caps)
        print(f"  {total} versículos")


def ref_ob(s):
    """'Prov.8.22' -> 'PRO.8.22'; devuelve None si no se reconoce."""
    p = s.split(".")
    if len(p) != 3 or p[0] not in OB:
        return None
    return f"{OB[p[0]]}.{p[1]}.{p[2]}"


def referencias():
    print("Referencias cruzadas (OpenBible.info)")
    z = zipfile.ZipFile(io.BytesIO(descargar(XREF_ZIP, CACHE / "cross-references.zip")))
    nombre = next(n for n in z.namelist() if n.endswith(".txt"))
    acum = {}
    with z.open(nombre) as f:
        for fila in csv.reader(io.TextIOWrapper(f, encoding="utf-8"), delimiter="\t"):
            if len(fila) < 3 or fila[0].startswith("From"):
                continue
            origen = ref_ob(fila[0])
            partes = [ref_ob(x) for x in fila[1].split("-")]
            if not origen or not all(partes):
                continue
            try:
                votos = int(fila[2])
            except ValueError:
                continue
            destino = "-".join(partes)
            libro, cap, ver = origen.split(".")
            acum.setdefault(libro, {}).setdefault(f"{cap}.{ver}", []).append((votos, destino))
    total = 0
    for libro, versos in acum.items():
        salida = {}
        for k, lista in versos.items():
            lista.sort(key=lambda x: -x[0])
            salida[k] = [d for v, d in lista[:REFS_POR_VERSO] if v > 0]
            total += len(salida[k])
        guardar(BIB / "referencias" / f"{libro}.json", {k: v for k, v in salida.items() if v})
    print(f"  {total} referencias")


def indice():
    ruta = BIB / "indice.json"
    idx = json.loads(ruta.read_text(encoding="utf-8"))
    idx["version"] = "2.0"
    idx["formato"] = "un archivo por libro: {carpeta}/{ID}.json"
    idx["fuentes"] = [
        {"id": "rvr1909", "nombre": "Reina Valera 1909", "idioma": "es", "dominioPublico": True, "carpeta": "textos/rvr1909"},
        {"id": "kjv", "nombre": "King James Version", "idioma": "en", "dominioPublico": True, "carpeta": "textos/kjv"},
        {"id": "tsk", "nombre": "Referencias cruzadas (OpenBible.info, CC-BY)", "tipo": "referencias", "carpeta": "referencias"},
    ]
    ruta.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    textos()
    referencias()
    indice()
    print("Listo.")
