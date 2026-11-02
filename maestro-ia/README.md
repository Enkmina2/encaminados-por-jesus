# Maestro IA — Backend Cloudflare Worker

Este directorio contiene el proxy seguro para el asistente bíblico «Maestro IA» de Encaminados por Jesús.

## ¿Por qué un Worker?
- **Seguridad**: La clave `GEMINI_API_KEY` se mantiene privada en Cloudflare y nunca se expone en el navegador.
- **Coste cero**: Cloudflare Workers incluye 100.000 peticiones gratuitas al día.
- **Rápido**: Se ejecuta en el borde de la red (edge) con latencia mínima.

## Despliegue en 3 pasos

1. **Instalar dependencias e iniciar sesión en Cloudflare:**
   ```bash
   cd maestro-ia
   npx wrangler login
   ```

2. **Configurar la clave de Gemini:**
   Obtén una clave gratuita en [Google AI Studio](https://aistudio.google.com/):
   ```bash
   npx wrangler secret put GEMINI_API_KEY
   ```
   (Pega tu clave de API cuando lo solicite).

3. **Publicar el worker:**
   ```bash
   npx wrangler deploy
   ```
   Te devolverá una URL pública (ejemplo: `https://maestro-ia.<tu-subdominio>.workers.dev`).

4. **Conectar con la web:**
   Abre [estudio.html](file:///c:/Users/salga/encaminados-por-jesus/estudio.html) y pon tu URL en la constante `API_URL`:
   ```javascript
   const API_URL = "https://maestro-ia.<tu-subdominio>.workers.dev";
   ```

*Nota: Mientras `API_URL` esté vacía, `estudio.html` funciona en **modo local/biblioteca**, buscando versículos y referencias cruzadas sin requerir IA.*
