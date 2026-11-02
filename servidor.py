#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor local para «Encaminados por Jesús» con proxy integrado para Groq y Gemini.
Reemplaza a 'python -m http.server 8000' y elimina los problemas de CORS y saturación.

Uso:
    python servidor.py
    (Abre automáticamente http://localhost:8000/estudio.html)
"""

import http.server
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

PUERTO = 8000
BASE = Path(__file__).resolve().parent

SISTEMA = {
    "es": """Eres el «Maestro IA» del portal cristiano «Encaminados por Jesús». Ayudas a personas que quieren entender una frase, un versículo o una palabra de la Biblia, y conversas con ellas con calidez, humildad y claridad.

Reglas:
- Basa tus respuestas en la Biblia. Cita siempre la referencia (libro capítulo:versículo). No inventes versículos.
- Distingue observación, interpretación y aplicación práctica.
- Idiomas originales: si el pasaje es del AT, explica el hebreo. Si es del NT, explica el griego y conéctalo con el trasfondo hebreo del AT (ej: gracia con chesed; fe con emunah; Espíritu con ruach; salvación con Yeshua). Usa transliteración fonética sencilla en cursiva o negrita.
- Lenguaje pastoral, cercano y claro. Respuestas breves (~250 palabras). Puedes usar listas cortas y **negritas**.
- Doctrina: El portal sostiene la Unicidad de Dios. Preséntala con amor y base bíblica, reconociendo con respeto otras posturas.
- Responde en español.""",
    "en": """You are the "AI Teacher" of the Christian portal "Encaminados por Jesús". You help people understand Bible verses, words, and concepts with warmth, pastoral clarity, and humility. Ground your answers in scripture, explain Greek terms and their Hebrew roots, and keep answers concise (~250 words) in English."""
}

def consultar_groq(key, mensaje, historial, idioma):
    url = "https://api.groq.com/openai/v1/chat/completions"
    messages = [{"role": "system", "content": SISTEMA.get(idioma, SISTEMA["es"])}]
    for h in (historial or [])[-6:]:
        messages.append({"role": "assistant" if h.get("rol") == "model" else "user", "content": h.get("texto", "")})
    messages.append({"role": "user", "content": mensaje})

    # Probar llama-3.3-70b-versatile o fallback a llama-3.1-8b-instant
    modelos = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    ultimo_error = None
    for modelo in modelos:
        payload = json.dumps({
            "model": modelo,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 1024
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "User-Agent": "EncaminadosPorJesus/1.0"
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            ultimo_error = e
            if e.code == 404:
                continue
            raise e
    if ultimo_error:
        raise ultimo_error

def consultar_gemini(key, mensaje, historial, idioma):
    modelos = ["gemini-3.8-flash", "gemini-2.0-flash"]
    contents = []
    for h in (historial or [])[-6:]:
        contents.append({"role": "model" if h.get("rol") == "model" else "user", "parts": [{"text": h.get("texto", "")}]})
    while contents and contents[0]["role"] != "user":
        contents.pop(0)
    contents.append({"role": "user", "parts": [{"text": mensaje}]})

    payload = json.dumps({
        "systemInstruction": {"parts": [{"text": SISTEMA.get(idioma, SISTEMA["es"])}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.5, "maxOutputTokens": 1024}
    }).encode("utf-8")

    ultimo_error = None
    for modelo in modelos:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={key}"
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            ultimo_error = e
            if e.code == 404:
                continue
            raise e
    if ultimo_error:
        raise ultimo_error

class Manejador(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/chat":
            longitud = int(self.headers.get("Content-Length", 0))
            cuerpo = json.loads(self.rfile.read(longitud).decode("utf-8"))
            mensaje = cuerpo.get("mensaje", "").strip()
            historial = cuerpo.get("historial", [])
            idioma = cuerpo.get("idioma", "es")
            key = cuerpo.get("key", "").strip() or os.environ.get("GROQ_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")

            if not key:
                self.enviar_json({"error": "No hay clave configurada. Añade tu clave de Groq o Gemini en la página."}, 400)
                return

            try:
                # Si la clave empieza por 'gsk_', es de Groq; si no, de Gemini
                if key.startswith("gsk_"):
                    respuesta = consultar_groq(key, mensaje, historial, idioma)
                else:
                    respuesta = consultar_gemini(key, mensaje, historial, idioma)
                self.enviar_json({"respuesta": respuesta})
            except urllib.error.HTTPError as e:
                err_txt = e.read().decode("utf-8", errors="ignore")
                print(f"[Error API {e.code}]: {err_txt}", file=sys.stderr)
                try:
                    j_err = json.loads(err_txt)
                    msg = j_err.get("error", {}).get("message") or err_txt
                except Exception:
                    msg = err_txt
                self.enviar_json({"error": msg or f"Error del proveedor ({e.code})"}, 502)
            except Exception as e:
                print(f"[Error interno]: {e}", file=sys.stderr)
                self.enviar_json({"error": str(e)}, 500)
        else:
            self.send_error(404)

    def enviar_json(self, obj, status=200):
        datos = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

if __name__ == "__main__":
    os.chdir(str(BASE))
    server = http.server.ThreadingHTTPServer(("", PUERTO), Manejador)
    print("=" * 60)
    print(f" Servidor de Encaminados por Jesús activo en:")
    print(f" 👉 http://localhost:{PUERTO}/estudio.html")
    print(f" 👉 Proxy IA integrado en /api/chat (Groq + Gemini)")
    print(" Presiona Ctrl + C para detener.")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
