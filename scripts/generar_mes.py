#!/usr/bin/env python3
"""Genera los días de un mes en datos/dias.json, en una sola llamada al modelo.

Lectura: Nuevo Testamento en orden (empieza por datos/lectura.json).
Texto del versículo: datos/rvr1960-nt.json (RVR1960, verificado a mano). Si falta, se para.
Paralelo del Antiguo Testamento: datos/concordancia-at.json (openbible.info, CC BY).

Uso:  python scripts/generar_mes.py 2026-12        (mes concreto)
      python scripts/generar_mes.py                 (mes siguiente al actual)
Requiere la variable de entorno ANTHROPIC_API_KEY.
"""
import calendar
import datetime as dt
import json
import os
import re
import sys
import urllib.request

MODELO = "claude-haiku-5-5"
RUTA_DIAS = "datos/dias.json"
RUTA_LECTURA = "datos/lectura.json"
RUTA_TEXTOS = "datos/rvr1960-nt.json"
RUTA_PARALELOS = "datos/concordancia-at.json"

# Nombre en español del libro -> código del dataset de referencias cruzadas
CODIGO_NT = {"Mateo": "Matt", "Marcos": "Mark", "Lucas": "Luke", "Juan": "John", "Hechos": "Acts",
             "Romanos": "Rom", "1 Corintios": "1Cor", "2 Corintios": "2Cor", "Gálatas": "Gal",
             "Efesios": "Eph", "Filipenses": "Phil", "Colosenses": "Col", "1 Tesalonicenses": "1Thess",
             "2 Tesalonicenses": "2Thess", "1 Timoteo": "1Tim", "2 Timoteo": "2Tim", "Tito": "Titus",
             "Filemón": "Phlm", "Hebreos": "Heb", "Santiago": "Jas", "1 Pedro": "1Pet", "2 Pedro": "2Pet",
             "1 Juan": "1John", "2 Juan": "2John", "3 Juan": "3John", "Judas": "Jude", "Apocalipsis": "Rev"}

INSTRUCCIONES = """Eres el redactor de la web cristiana «Encaminados por Jesús», que defiende la unicidad de Dios:
el Padre, el Hijo y el Espíritu se revelan en una sola persona, Dios mismo hecho carne (1 Timoteo 3:16, Juan 1:14).
Escribe en español, con lenguaje sencillo y pastoral. Presenta esta enseñanza con claridad y apoyo bíblico,
y reconoce con honestidad que otras tradiciones cristianas la entienden de otra manera.
No inventes citas: cita solo el versículo que se te da y el paralelo del Antiguo Testamento que se te da.
Responde SOLO con JSON válido, sin texto fuera del JSON."""


def cargar(ruta, por_defecto):
    if not os.path.exists(ruta):
        return por_defecto
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def guardar(ruta, datos):
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write("\n")


def dias_del_mes(anio, mes):
    ultimo = calendar.monthrange(anio, mes)[1]
    return [dt.date(anio, mes, d).isoformat() for d in range(1, ultimo + 1)]


def referencia_codigo(ref):
    m = re.match(r"^(.+?)\s+(\d+):(\d+)$", ref)
    libro, cap, ver = m.group(1), m.group(2), m.group(3)
    return CODIGO_NT[libro] + "." + cap + "." + ver


def siguiente_versiculo(lectura, textos):
    """Devuelve la referencia del siguiente versículo con texto, o None si falta."""
    libro, cap, ver = lectura["libro"], lectura["capitulo"], lectura["versiculo"]
    ref = f"{libro} {cap}:{ver}"
    return ref if ref in textos else None


def avanzar(lectura, textos):
    """Pasa al versículo siguiente del libro (o al primero del capítulo siguiente)."""
    libro, cap, ver = lectura["libro"], lectura["capitulo"], lectura["versiculo"]
    if f"{libro} {cap}:{ver + 1}" in textos:
        lectura["versiculo"] = ver + 1
    elif f"{libro} {cap + 1}:1" in textos:
        lectura["capitulo"], lectura["versiculo"] = cap + 1, 1
    else:
        raise SystemExit(f"No hay texto para seguir después de {libro} {cap}:{ver}. Añádelo a {RUTA_TEXTOS}.")


def llamar_modelo(prompt):
    cuerpo = json.dumps({
        "model": MODELO, "max_tokens": 8000,
        "system": INSTRUCCIONES,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=cuerpo, method="POST", headers={
        "content-type": "application/json", "anthropic-version": "2023-06-01",
        "x-api-key": os.environ["ANTHROPIC_API_KEY"]})
    with urllib.request.urlopen(req, timeout=180) as r:
        respuesta = json.load(r)
    texto = "".join(b.get("text", "") for b in respuesta["content"] if b["type"] == "text")
    return json.loads(texto[texto.index("{"): texto.rindex("}") + 1])


def main():
    if len(sys.argv) > 1:
        anio, mes = map(int, sys.argv[1].split("-"))
    else:
        hoy = dt.date.today()
        anio, mes = (hoy.year + (hoy.month // 12), hoy.month % 12 + 1)

    dias = cargar(RUTA_DIAS, {"instrucciones": [], "dias": []})
    existentes = {x["fecha"] for x in dias["dias"]}
    pendientes = [f for f in dias_del_mes(anio, mes) if f not in existentes]
    if not pendientes:
        print(f"Todo el mes {anio}-{mes:02d} ya existe. No hay nada que hacer.")
        return

    textos = cargar(RUTA_TEXTOS, {})
    paralelos = cargar(RUTA_PARALELOS, {})
    lectura = cargar(RUTA_LECTURA, {"libro": "Mateo", "capitulo": 1, "versiculo": 1})

    # Un versículo por día pendiente, en orden de lectura
    refs = []
    for _ in pendientes:
        ref = siguiente_versiculo(lectura, textos)
        if ref is None:
            raise SystemExit(f"Falta el texto RVR1960 de {lectura['libro']} {lectura['capitulo']}:{lectura['versiculo']} en {RUTA_TEXTOS}.")
        refs.append((lectura["libro"], lectura["capitulo"], lectura["versiculo"], ref))
        avanzar(lectura, textos)

    # Una sola llamada para todo el mes
    lineas = []
    for fecha, (libro, cap, ver, ref) in zip(pendientes, refs):
        par = paralelos.get(referencia_codigo(ref), [])
        lineas.append(f"- {fecha} | {ref} | «{textos[ref]}» | paralelos AT: {', '.join(par) or 'ninguno'}")
    prompt = (
        "Escribe un día por línea del calendario. Para cada fecha devuelve un objeto con esta forma exacta:\n"
        '{"dias":[{"fecha":"AAAA-MM-DD","tema":"...","estudio":{"resumen":"...","parrafos":["...","..."]},'
        '"para_hoy":"..."}]}\n'
        "El tema es breve. El resumen es una frase. Los párrafos son dos o tres. «para_hoy» es una acción concreta. "
        "En el estudio, relaciona el versículo del Nuevo Testamento con uno de los paralelos del Antiguo Testamento indicados.\n\n"
        + "\n".join(lineas)
    )
    generado = llamar_modelo(prompt)
    por_fecha = {x["fecha"]: x for x in generado["dias"]}

    nuevos = []
    for fecha, (libro, cap, ver, ref) in zip(pendientes, refs):
        g = por_fecha.get(fecha)
        if not g:
            raise SystemExit(f"El modelo no devolvió el día {fecha}. No se ha escrito nada.")
        concordancia = [{"cita": c, "frase": "", "frase_en": ""} for c in paralelos.get(referencia_codigo(ref), [])[:2]]
        nuevos.append({
            "fecha": fecha, "tema": g["tema"], "tema_en": "",
            "versiculo": {"referencia": ref, "texto": textos[ref], "texto_en": ""},
            "hoy_en_el_mundo": "", "hoy_en_el_mundo_en": "",
            "estudio": {"parrafos": g["estudio"]["parrafos"], "parrafos_en": [],
                        "resumen": g["estudio"]["resumen"], "resumen_en": ""},
            "para_hoy": g["para_hoy"], "para_hoy_en": "",
            "concordancia": concordancia, "aprobado": True,
        })

    dias["dias"].extend(nuevos)
    guardar(RUTA_DIAS, dias)
    guardar(RUTA_LECTURA, lectura)
    print(f"Escritos {len(nuevos)} días de {anio}-{mes:02d}: {nuevos[0]['fecha']} a {nuevos[-1]['fecha']}. "
          f"Siguiente lectura: {lectura['libro']} {lectura['capitulo']}:{lectura['versiculo']}.")


if __name__ == "__main__":
    main()
