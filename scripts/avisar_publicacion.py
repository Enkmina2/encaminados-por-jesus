#!/usr/bin/env python3
"""Avisa por Telegram (bot del vigilante) de los contenidos nuevos de la web.

Compara datos/dias.json y datos/pasajes-siguientes.json tal como estaban en el commit ANTES
con como quedan en DESPUES, y manda un mensaje por cada novedad:
  - 📖 días nuevos (semana nueva): fechas, tema y versículo de cada día, y desde cuándo se ven;
  - 📜 pasaje de la semana nuevo: referencia y desde qué domingo se ve;
  - 🌍 «hoy_en_el_mundo» rellenado en un día que ya existía: fecha y frase.

Uso (lo lanza .github/workflows/avisar-publicacion.yml):
  ANTES=<sha> DESPUES=<sha> TELEGRAM_TOKEN=... TELEGRAM_CHAT_ID=... python3 scripts/avisar_publicacion.py
  python3 scripts/avisar_publicacion.py --simular     (solo enseña los mensajes, no envía nada)
  python3 scripts/avisar_publicacion.py --prueba      (añade «PRUEBA» al principio de cada mensaje)
Sin ANTES (o con el sha de ceros de una rama nueva) compara con el commit anterior a DESPUES.
"""
import datetime
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

DIAS = "datos/dias.json"
PASAJES = "datos/pasajes-siguientes.json"
MAX_TELEGRAM = 4000  # el límite real es 4096 caracteres por mensaje
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def leer_en_commit(commit, ruta):
    """JSON de `ruta` en `commit`; None si el archivo no existía o no se puede leer."""
    r = subprocess.run(["git", "show", f"{commit}:{ruta}"], capture_output=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout.decode("utf-8"))
    except ValueError as e:
        print(f"Aviso: {ruta} en {commit[:7]} no es un JSON válido ({e})")
        return None


def fecha_larga(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{SEMANA[d.weekday()]} {d.day} de {MESES[d.month - 1]}"


def hoy_en_espana():
    """Fecha de hoy en España (UTC+1 en invierno, UTC+2 en verano; basta para decidir el día)."""
    ahora = datetime.datetime.now(datetime.timezone.utc)
    verano = 3 < ahora.month < 11  # aproximación suficiente: solo afecta cerca de medianoche
    return (ahora + datetime.timedelta(hours=2 if verano else 1)).date()


def linea_margen(primera_fecha, hoy=None):
    """Recuerda hasta cuándo se pueden pedir cambios, o avisa de que ya se ve en la web."""
    hoy = hoy or hoy_en_espana()
    inicio = datetime.date.fromisoformat(primera_fecha)
    if inicio <= hoy:
        return "Ya se ve en la web (empieza hoy o antes): si quieres cambiar algo, pídelo cuanto antes."
    return f"Tienes margen para pedir cambios hasta el {fecha_larga((inicio - datetime.timedelta(days=1)).isoformat())}."


def texto_hoy(valor):
    """«hoy_en_el_mundo» puede venir como texto o como lista de frases."""
    if isinstance(valor, list):
        return " ".join(str(x).strip() for x in valor if str(x).strip())
    return str(valor or "").strip()


def por_fecha(datos, lista, clave):
    return {x[clave]: x for x in ((datos or {}).get(lista) or []) if isinstance(x, dict) and x.get(clave)}


def aviso_dias_nuevos(antes, despues):
    nuevas = sorted(set(despues) - set(antes))
    if not nuevas:
        return None
    lineas = [f"📖 Nueva semana publicada ({len(nuevas)} días: {fecha_larga(nuevas[0])} – {fecha_larga(nuevas[-1])})", ""]
    for f in nuevas:
        d = despues[f]
        v = d.get("versiculo") or {}
        lineas.append(f"• {fecha_larga(f)}: {d.get('tema', '(sin tema)')}")
        lineas.append(f"  {v.get('referencia', '(sin versículo)')}" + (f" — «{v['texto']}»" if v.get("texto") else ""))
    lineas += ["", f"Se verán en la web cada uno en su fecha, desde el {fecha_larga(nuevas[0])}.",
               linea_margen(nuevas[0])]
    return "\n".join(lineas)


def aviso_pasajes_nuevos(antes, despues):
    nuevos = sorted(set(despues) - set(antes))
    if not nuevos:
        return None
    lineas = ["📜 Pasaje de la semana preparado", ""]
    for desde in nuevos:
        p = despues[desde]
        lineas.append(f"• {p.get('referencia', '?')} ({len(p.get('versiculos') or [])} versículos): se verá desde el {fecha_larga(desde)}")
    lineas += ["", linea_margen(nuevos[0])]
    return "\n".join(lineas)


def avisos_hoy_en_el_mundo(antes, despues):
    """Un aviso por cada día que ya existía y al que se le ha rellenado (o cambiado) la frase."""
    avisos = []
    for f in sorted(set(antes) & set(despues)):
        nuevo = texto_hoy(despues[f].get("hoy_en_el_mundo"))
        if nuevo and nuevo != texto_hoy(antes[f].get("hoy_en_el_mundo")):
            avisos.append(f"🌍 Hoy en el mundo — {fecha_larga(f)}\n\n{nuevo}")
    return avisos


def preparar_avisos(antes_commit, despues_commit):
    dias_a = por_fecha(leer_en_commit(antes_commit, DIAS), "dias", "fecha")
    dias_d = por_fecha(leer_en_commit(despues_commit, DIAS), "dias", "fecha")
    pas_a = por_fecha(leer_en_commit(antes_commit, PASAJES), "pasajes", "desde")
    pas_d = por_fecha(leer_en_commit(despues_commit, PASAJES), "pasajes", "desde")
    avisos = [aviso_dias_nuevos(dias_a, dias_d), aviso_pasajes_nuevos(pas_a, pas_d),
              *avisos_hoy_en_el_mundo(dias_a, dias_d)]
    return [a for a in avisos if a]


def trocear(texto):
    """Parte un mensaje largo por líneas para no pasar del límite de Telegram."""
    trozos, actual = [], ""
    for linea in texto.split("\n"):
        if actual and len(actual) + len(linea) + 1 > MAX_TELEGRAM:
            trozos.append(actual)
            actual = ""
        actual = f"{actual}\n{linea}" if actual else linea
    return [*trozos, actual] if actual else trozos


def enviar(texto, token, chat):
    datos = urllib.parse.urlencode({"chat_id": chat, "text": texto, "disable_web_page_preview": "true"}).encode()
    with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", data=datos, timeout=30) as r:
        if json.load(r).get("ok") is not True:
            raise RuntimeError("Telegram no aceptó el mensaje")


def commit_anterior(despues):
    r = subprocess.run(["git", "rev-parse", f"{despues}~1"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def main():
    simular, prueba = "--simular" in sys.argv, "--prueba" in sys.argv
    despues = os.environ.get("DESPUES") or "HEAD"
    antes = os.environ.get("ANTES", "").strip()
    if not antes or set(antes) == {"0"}:
        antes = commit_anterior(despues)
    if not antes:
        print("No hay commit anterior con el que comparar; no se avisa de nada")
        return 0

    avisos = preparar_avisos(antes, despues)
    print(f"Comparando {antes[:7]} → {despues[:7] if len(despues) > 7 else despues}: {len(avisos)} aviso(s)")
    if not avisos:
        return 0
    mensajes = [m for a in avisos for m in trocear(("🧪 PRUEBA\n\n" if prueba else "") + a)]
    if simular:
        for m in mensajes:
            print("-" * 40 + "\n" + m)
        return 0

    token, chat = os.environ.get("TELEGRAM_TOKEN", "").strip(), os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        print("Faltan los secretos TELEGRAM_TOKEN / TELEGRAM_CHAT_ID; no se puede avisar")
        return 1
    fallos = 0
    for m in mensajes:
        try:
            enviar(m, token, chat)
        except Exception as e:  # nunca se imprime la URL: lleva el token
            fallos += 1
            print(f"No se pudo enviar un mensaje por Telegram ({type(e).__name__})")
    print(f"Enviados {len(mensajes) - fallos} de {len(mensajes)} mensajes")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
