/**
 * Maestro IA — proxy seguro hacia Gemini (Cloudflare Workers).
 * La clave de la API vive solo aquí (secreto GEMINI_API_KEY), nunca en el navegador.
 *
 * Entrada (POST JSON):
 *   { mensaje: string, historial: [{rol:"user"|"model", texto:string}], idioma: "es"|"en",
 *     contexto: [{ref:string, rvr:string, kjv:string, cruzadas:[{ref,texto}]}] }
 * Salida: { respuesta: string }  |  { error: string }
 */

const MAX_MENSAJE = 1000;      // caracteres por mensaje del usuario
const MAX_HISTORIAL = 8;       // turnos previos que se reenvían
const MAX_CONTEXTO = 6000;     // caracteres de texto bíblico adjunto

const SISTEMA = {
  es: `Eres el «Maestro IA» del portal cristiano «Encaminados por Jesús». Ayudas a personas que quieren entender una frase, un versículo o una palabra de la Biblia, y conversas con ellas con calidez, humildad y claridad.

Reglas:
- Basa tus respuestas en la Biblia. Si se adjunta «Texto bíblico», úsalo como fuente principal y cita siempre la referencia (libro capítulo:versículo). No inventes versículos ni citas: si no estás seguro de una cita o de un dato, dilo.
- Distingue lo que el texto dice (observación) de lo que significa (interpretación) y de cómo aplicarlo (aplicación).
- Para palabras, explica el sentido en el idioma original (hebreo/griego) solo cuando estés seguro, con transliteración sencilla, y relaciónalo con el contexto.
- Lenguaje sencillo y pastoral. Respuestas breves (máx. ~250 palabras) salvo que pidan más. Puedes usar listas cortas y **negritas**. Termina, cuando venga al caso, con una pregunta breve para seguir profundizando.
- El portal sostiene la doctrina de la Unicidad de Dios. Cuando la pregunta toque ese tema, preséntala con respeto y con apoyo bíblico, y reconoce con honestidad que otras tradiciones cristianas lo entienden de otra manera.
- No hables de política ni des consejos médicos, legales o financieros. Si alguien está en crisis o corre peligro, anímale con cariño a buscar ayuda inmediata (servicios de emergencia o un pastor de confianza).
- Si piden algo ajeno a la Biblia o la fe, redirige amablemente.
- Responde en español.`,
  en: `You are the "AI Teacher" of the Christian portal "Encaminados por Jesús". You help people who want to understand a phrase, a verse or a word from the Bible, and you talk with them warmly, humbly and clearly.

Rules:
- Ground your answers in the Bible. If "Bible text" is attached, use it as your main source and always cite the reference (book chapter:verse). Never invent verses or quotes: if you are unsure about a quote or a fact, say so.
- Distinguish what the text says (observation) from what it means (interpretation) and how to apply it (application).
- For words, explain the original-language sense (Hebrew/Greek) only when you are sure, with simple transliteration, and tie it to the context.
- Simple, pastoral language. Short answers (max ~250 words) unless asked for more. Short lists and **bold** are fine. When appropriate, end with a brief question to go deeper.
- The portal holds the Oneness doctrine of God. When a question touches it, present it respectfully with biblical support, and honestly acknowledge that other Christian traditions understand it differently.
- No politics, and no medical, legal or financial advice. If someone is in crisis or danger, lovingly encourage them to seek immediate help (emergency services or a trusted pastor).
- If asked about something unrelated to the Bible or faith, kindly redirect.
- Answer in English.`,
};

function cors(env, req) {
  const permitidos = (env.ALLOWED_ORIGINS || "").split(",").map(s => s.trim()).filter(Boolean);
  const origen = req.headers.get("Origin") || "";
  const ok = permitidos.includes(origen);
  return {
    ok,
    headers: {
      "Access-Control-Allow-Origin": ok ? origen : permitidos[0] || "",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Max-Age": "86400",
      "Vary": "Origin",
    },
  };
}

const json = (obj, status, headers) =>
  new Response(JSON.stringify(obj), { status, headers: { ...headers, "Content-Type": "application/json; charset=utf-8" } });

const limpiar = (s, max) => String(s ?? "").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").trim().slice(0, max);

function textoContexto(contexto, idioma) {
  if (!Array.isArray(contexto) || !contexto.length) return "";
  let t = idioma === "en" ? "Bible text (public domain: RVR 1909 / KJV):\n" : "Texto bíblico (dominio público: RVR 1909 / KJV):\n";
  for (const c of contexto.slice(0, 4)) {
    t += `\n[${limpiar(c.ref, 60)}]\nRVR1909: ${limpiar(c.rvr, 1800)}\nKJV: ${limpiar(c.kjv, 1800)}\n`;
    for (const x of (Array.isArray(c.cruzadas) ? c.cruzadas : []).slice(0, 3))
      t += `  ↔ ${limpiar(x.ref, 40)}: ${limpiar(x.texto, 300)}\n`;
  }
  return t.slice(0, MAX_CONTEXTO);
}

export default {
  async fetch(req, env) {
    const c = cors(env, req);
    if (req.method === "OPTIONS") return new Response(null, { status: c.ok ? 204 : 403, headers: c.headers });
    if (req.method !== "POST") return json({ error: "Método no permitido" }, 405, c.headers);
    if (!c.ok) return json({ error: "Origen no permitido" }, 403, c.headers);
    if (!env.GEMINI_API_KEY) return json({ error: "Servicio no configurado" }, 500, c.headers);

    let cuerpo;
    try { cuerpo = await req.json(); } catch { return json({ error: "JSON no válido" }, 400, c.headers); }

    const idioma = cuerpo.idioma === "en" ? "en" : "es";
    const mensaje = limpiar(cuerpo.mensaje, MAX_MENSAJE);
    if (!mensaje) return json({ error: "Mensaje vacío" }, 400, c.headers);

    const historial = (Array.isArray(cuerpo.historial) ? cuerpo.historial : [])
      .slice(-MAX_HISTORIAL)
      .map(h => ({ role: h.rol === "model" ? "model" : "user", parts: [{ text: limpiar(h.texto, 2000) }] }))
      .filter(h => h.parts[0].text);
    // Gemini exige que la conversación empiece por «user»
    while (historial.length && historial[0].role !== "user") historial.shift();

    const ctx = textoContexto(cuerpo.contexto, idioma);
    const ultimo = (ctx ? ctx + "\n---\n" : "") + mensaje;

    const modelo = env.GEMINI_MODEL || "gemini-1.5-flash";
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(modelo)}:generateContent`;

    let r;
    try {
      r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-goog-api-key": env.GEMINI_API_KEY },
        body: JSON.stringify({
          systemInstruction: { parts: [{ text: SISTEMA[idioma] }] },
          contents: [...historial, { role: "user", parts: [{ text: ultimo }] }],
          generationConfig: { temperature: 0.5, maxOutputTokens: 1024 },
        }),
      });
    } catch {
      return json({ error: "No se pudo contactar con el servicio de IA" }, 502, c.headers);
    }
    if (!r.ok) return json({ error: r.status === 429 ? "Demasiadas consultas, inténtalo en un momento" : "Error del servicio de IA" }, 502, c.headers);

    const datos = await r.json();
    const respuesta = (datos.candidates?.[0]?.content?.parts || []).map(p => p.text || "").join("").trim();
    if (!respuesta) return json({ error: "Sin respuesta, reformula la pregunta" }, 502, c.headers);
    return json({ respuesta }, 200, c.headers);
  },
};
