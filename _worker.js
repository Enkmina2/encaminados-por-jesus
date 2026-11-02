/**
 * Maestro IA — Cloudflare Worker con soporte para Static Assets y proxy a Groq / Gemini.
 * Si es POST: procesa la consulta con la IA.
 * Si es GET: sirve la web y los archivos estáticos.
 */

const MAX_MENSAJE = 1000;
const MAX_HISTORIAL = 8;
const MAX_CONTEXTO = 6000;

const SISTEMA = {
  es: `Eres el «Maestro IA» del portal cristiano «Encaminados por Jesús». Ayudas a personas que quieren entender una frase, un versículo o una palabra de la Biblia, y conversas con ellas con calidez, humildad y claridad.

Reglas:
- Basa tus respuestas en la Biblia. Si se adjunta «Texto bíblico», úsalo como fuente principal y cita siempre la referencia (libro capítulo:versículo). No inventes versículos ni citas: si no estás seguro de una cita o de un dato, dilo.
- Distingue lo que el texto dice (observación) de lo que significa (interpretación) y de cómo aplicarlo (aplicación).
- Idiomas originales y raíces bíblicas (hebreo y griego):
  * Si el pasaje es del Antiguo Testamento, explica el término en su hebreo original (o arameo).
  * Si el pasaje es del Nuevo Testamento, explica el término en griego y, siempre que aporte riqueza y contexto, haz referencia a su trasfondo o raíz en el hebreo del Antiguo Testamento (por ejemplo: fe/pistis conectada a emunah; gracia/charis a chesed; Espíritu/pneuma a ruach; salvación a Yeshua).
  * Usa siempre una transliteración fonética sencilla y comprensible en cursiva o negrita para que cualquier lector pueda pronunciarla y entender su significado esencial en el contexto.
- Lenguaje sencillo y pastoral. Respuestas breves (máx. ~250 palabras) salvo que pidan más. Puedes usar listas cortas y **negritas**. Termina, cuando venga al caso, con una pregunta breve para seguir profundizando.
- El portal sostiene la doctrina de la Unicidad de Dios. Cuando la pregunta toque ese tema, preséntala con respeto y con apoyo bíblico, y reconoce con honestidad que otras tradiciones cristianas lo entienden de otra manera.
- No hables de política ni des consejos médicos, legales o financieros. Si alguien está en crisis o corre peligro, anímale con cariño a buscar ayuda inmediata (servicios de emergencia o un pastor de confianza).
- Si piden algo ajeno a la Biblia o la fe, redirige amablemente.
- Responde en español.`,
  en: `You are the "AI Teacher" of the Christian portal "Encaminados por Jesús". You help people who want to understand a phrase, a verse or a word from the Bible, and you talk with them warmly, humbly and clearly.

Rules:
- Ground your answers in the Bible. If "Bible text" is attached, use it as your main source and always cite the reference (book chapter:verse). Never invent verses or quotes: if you are unsure about a quote or a fact, say so.
- Distinguish what the text says (observation) from what it means (interpretation) and how to apply it (application).
- Original languages and biblical roots (Hebrew and Greek):
  * For Old Testament passages, explain the original Hebrew (or Aramaic).
  * For New Testament passages, explain the Greek term and, whenever enriching, connect it to its Old Testament Hebrew roots and background (e.g., faith/pistis to emunah; grace/charis to chesed; Spirit/pneuma to ruach; salvation to Yeshua).
  * Always provide simple, readable phonetic transliterations so any reader can understand their essential biblical meaning in context.
- Simple, pastoral language. Short answers (max ~250 words) unless asked for more. Short lists and **bold** are fine. When appropriate, end with a brief question to go deeper.
- The portal holds the Oneness doctrine of God. When a question touches it, present it respectfully with biblical support, and honestly acknowledge that other Christian traditions understand it differently.
- No politics, and no medical, legal or financial advice. If someone is in crisis or danger, lovingly encourage them to seek immediate help (emergency services or a trusted pastor).
- If asked about something unrelated to the Bible or faith, kindly redirect.
- Answer in English.`,
};

function corsHeaders(req) {
  const origen = req.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origen,
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  };
}

const json = (obj, status, headers = {}) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { ...headers, "Content-Type": "application/json; charset=utf-8" },
  });

const limpiar = (s, max) =>
  String(s ?? "").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").trim().slice(0, max);

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

async function procesarChat(req, env) {
  const ch = corsHeaders(req);
  let cuerpo;
  try { cuerpo = await req.json(); } catch { return json({ error: "JSON no válido" }, 400, ch); }

  const keyGroq = env.GROQ_API_KEY || (cuerpo.key && cuerpo.key.startsWith("gsk_") ? cuerpo.key : "");
  const keyGemini = env.GEMINI_API_KEY || (cuerpo.key && !cuerpo.key.startsWith("gsk_") ? cuerpo.key : "");

  if (!keyGroq && !keyGemini) {
    return json({ error: "Servicio no configurado: falta GROQ_API_KEY en Cloudflare" }, 500, ch);
  }

  const idioma = cuerpo.idioma === "en" ? "en" : "es";
  const mensaje = limpiar(cuerpo.mensaje, MAX_MENSAJE);
  if (!mensaje) return json({ error: "Mensaje vacío" }, 400, ch);

  const historial = (Array.isArray(cuerpo.historial) ? cuerpo.historial : [])
    .slice(-MAX_HISTORIAL)
    .map(h => ({ role: h.rol === "model" ? "model" : "user", parts: [{ text: limpiar(h.texto, 2000) }] }))
    .filter(h => h.parts[0].text);
  while (historial.length && historial[0].role !== "user") historial.shift();

  const ctx = textoContexto(cuerpo.contexto, idioma);
  const ultimo = (ctx ? ctx + "\n---\n" : "") + mensaje;

  let respuesta = "";

  // 1. Probar Groq con cascada rápida: openai/gpt-oss-120b -> openai/gpt-oss-20b
  if (keyGroq) {
    const groqMessages = [
      { role: "system", content: SISTEMA[idioma] },
      ...historial.map(h => ({ role: h.role === "model" ? "assistant" : "user", content: h.parts[0].text })),
      { role: "user", content: ultimo }
    ];

    const modelos = [env.GROQ_MODEL, "openai/gpt-oss-120b", "openai/gpt-oss-20b"].filter(Boolean);
    for (const mod of modelos) {
      try {
        const r = await fetch("https://api.groq.com/openai/v1/chat/completions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${keyGroq}`
          },
          body: JSON.stringify({
            model: mod,
            messages: groqMessages,
            temperature: 0.5,
            max_tokens: 1024
          })
        });
        if (r.ok) {
          const d = await r.json();
          respuesta = d.choices?.[0]?.message?.content?.trim() || "";
          if (respuesta) break;
        }
      } catch (e) {
        console.warn(`Groq ${mod} err:`, e);
      }
    }
  }

  // 2. Respaldo transparente en Gemini si Groq no responde
  if (!respuesta && keyGemini) {
    const modelosGemini = [env.GEMINI_MODEL, "gemini-2.0-flash", "gemini-3.8-flash"].filter(Boolean);
    for (const mod of modelosGemini) {
      try {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(mod)}:generateContent`;
        const r = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json", "x-goog-api-key": keyGemini },
          body: JSON.stringify({
            contents: [...historial, { role: "user", parts: [{ text: ultimo }] }],
            systemInstruction: { parts: [{ text: SISTEMA[idioma] }] },
            generationConfig: { temperature: 0.5, maxOutputTokens: 1024 }
          })
        });
        if (r.ok) {
          const d = await r.json();
          respuesta = d.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || "";
          if (respuesta) break;
        }
      } catch (e) {
        console.warn(`Gemini ${mod} err:`, e);
      }
    }
  }

  if (!respuesta) {
    return json({ error: "Reintenta en un momento por favor." }, 502, ch);
  }

  return json({ respuesta }, 200, ch);
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const ch = corsHeaders(req);

    if (req.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: ch });
    }

    // Petición POST o ruta de API -> Procesa la IA
    if (req.method === "POST" || url.pathname.startsWith("/api/")) {
      return procesarChat(req, env);
    }

    // Si Cloudflare tiene static assets configurados, sirve los archivos web
    if (env.ASSETS && typeof env.ASSETS.fetch === "function") {
      return env.ASSETS.fetch(req);
    }

    return new Response("Maestro IA activo", { status: 200, headers: ch });
  }
};
