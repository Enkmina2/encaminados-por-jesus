/* Traducción al español del banner de cookies (Cookie Compliance de hu-manity).
   La cuenta gratuita solo trae los textos en inglés. Si la web está en español (epj-idioma ≠ "en"), este
   script cambia cada texto conocido del banner por su traducción; en inglés deja el original.
   No toca el funcionamiento del banner ni lo que elige el visitante: solo el texto que se ve.
   Los textos en inglés salen de la API de hu-manity (DefaultUserTextJSON y DefaultCategoryJSON de la app
   enkmina2githubio-c393e51). Si hu-manity cambia alguno, ese texto concreto se verá en inglés hasta
   añadirlo aquí. */
(() => {
  const ES = {
    // vista principal
    "We believe your data is your property and support your right to privacy and transparency.":
      "Creemos que tus datos te pertenecen y defendemos tu derecho a la privacidad y a la transparencia.",
    "To provide you the best experience on our website, we use cookies or similar technologies. Select a data access level to decide for which purposes we may use and share your data.":
      "Para ofrecerte la mejor experiencia en nuestra web, usamos cookies o tecnologías similares. Elige un nivel de acceso a tus datos para decidir con qué fines podemos usarlos y compartirlos.",
    "Private": "Privado",
    "Balanced": "Equilibrado",
    "Personalized": "Personalizado",
    "Customize": "Personalizar",
    "Save my preferences": "Guardar mis preferencias",
    "Privacy policy": "Política de privacidad",
    "Do Not Sell": "No vender mis datos",
    "Highest level of privacy. Data accessed for necessary site operations only. Data shared with 3rd parties to ensure the site is secure and works on your device.":
      "Máximo nivel de privacidad. Solo se accede a los datos necesarios para el funcionamiento de la web. Los datos se comparten con terceros únicamente para que la web sea segura y funcione en tu dispositivo.",
    "Balanced experience. Data accessed for content personalisation and site optimisation. Data shared with 3rd parties may be used to track you and store your preferences for this site.":
      "Experiencia equilibrada. Se accede a los datos para personalizar el contenido y optimizar la web. Los datos compartidos con terceros pueden usarse para seguirte y guardar tus preferencias en esta web.",
    "Highest level of personalization. Data accessed to make ads and media more relevant. Data shared with 3rd parties may be use to track you on this site and other sites you visit.":
      "Máximo nivel de personalización. Se accede a los datos para que los anuncios y el contenido multimedia sean más relevantes. Los datos compartidos con terceros pueden usarse para seguirte en esta web y en otras que visites.",
    "Why am I seeing this banner?": "¿Por qué veo este aviso?",
    "What should a Privacy Policy page include?": "¿Qué debe incluir una página de política de privacidad?",
    "What consent choices do I have?": "¿Qué opciones de consentimiento tengo?",
    "Tell me about my saved consent.": "Infórmame sobre mi consentimiento guardado.",
    "What are the benefits of data sharing?": "¿Qué ventajas tiene compartir datos?",
    // contenido bloqueado
    "Accept": "Aceptar",
    "We need your permission before this content can load.": "Necesitamos tu permiso para cargar este contenido.",
    "It will receive your IP address and may set cookies.": "Recibirá tu dirección IP y puede instalar cookies.",
    "You can change your choice at any time.": "Puedes cambiar tu elección en cualquier momento.",
    "a third-party service": "un servicio de terceros",
    // preferencias
    "Consent Preferences": "Preferencias de consentimiento",
    "Use the toggles below to specify your data sharing purposes for this website.":
      "Usa los interruptores de abajo para indicar con qué fines compartes tus datos con esta web.",
    // nivel de acceso
    "Your Data Access Level": "Tu nivel de acceso a los datos",
    "You choose the level of data access you want to give to this website, whether you want the highest level of privacy, or the highest level of personalisation.":
      "Tú eliges el nivel de acceso a tus datos que das a esta web: desde el máximo nivel de privacidad hasta el máximo nivel de personalización.",
    "Higher levels of access mean that you trust this website to use your data responsibly.":
      "Un nivel de acceso más alto significa que confías en que esta web usará tus datos de forma responsable.",
    "Rejects all access and gives you highest level of privacy.": "Rechaza todo el acceso y te da el máximo nivel de privacidad.",
    "Accepts some access and gives you a balanced experience.": "Acepta parte del acceso y te da una experiencia equilibrada.",
    "Accepts all access and gives you the highest level of personalisation.": "Acepta todo el acceso y te da el máximo nivel de personalización.",
    // ventajas
    "Benefits of data sharing": "Ventajas de compartir datos",
    "Your data access level represents your consent to allow this site to access your data. Different access levels benefit you in different ways. The lowest level of access is required to ensure the site works properly and is secure. The second level of access can make your experience more convenient by allowing this site to remember your preferences and suggest new products and services based on what you like. The highest level of access can make your experience more personalised by helping this site suggest new products and services from this site and other sites, which may be more relevant to your personal interests.":
      "Tu nivel de acceso a los datos representa tu consentimiento para que esta web acceda a ellos. Cada nivel te beneficia de una forma distinta. El nivel más bajo es necesario para que la web funcione correctamente y sea segura. El segundo nivel puede hacer tu experiencia más cómoda, ya que permite a esta web recordar tus preferencias y sugerirte nuevos productos y servicios según lo que te gusta. El nivel más alto puede hacer tu experiencia más personalizada, ayudando a esta web a sugerirte nuevos productos y servicios de esta y de otras webs que pueden ser más relevantes para tus intereses.",
    "Higher levels of access enable a better browsing experience for you, and may also help support this site through advertising revenues.":
      "Los niveles de acceso más altos te ofrecen una mejor experiencia de navegación y también pueden ayudar a mantener esta web gracias a los ingresos por publicidad.",
    // tipos de datos
    "Your Data Types": "Tus tipos de datos",
    "Here’s a summary of the data types we may collect about you, and the ways that data can be used.":
      "Este es un resumen de los tipos de datos que podemos recoger sobre ti y de las formas en que pueden usarse.",
    "Anonymous data is data that cannot be used to identify you like device type, browser version, and referer or affiliate URL.":
      "Los datos anónimos son datos que no sirven para identificarte, como el tipo de dispositivo, la versión del navegador y la URL de procedencia o de afiliado.",
    "Pseudonymous data can be used to track you as a UniqueID or UID that is not tied directly to your personal information.":
      "Los datos seudónimos pueden usarse para seguirte mediante un identificador único (UniqueID o UID) que no está vinculado directamente a tu información personal.",
    "Personal data can be used to build a profile about you on this and other websites, who may use it to identify you.":
      "Los datos personales pueden usarse para crear un perfil sobre ti en esta y en otras webs, que pueden usarlo para identificarte.",
    // derechos
    "Know your rights": "Conoce tus derechos",
    "To comply with the latest data protection laws, this site asks you for consent per purpose category, which gives you control over which 3rd parties have access to your data (through cookies or other tracking technologies).":
      "Para cumplir las leyes de protección de datos más recientes, esta web te pide el consentimiento por categoría de finalidad, lo que te permite controlar qué terceros tienen acceso a tus datos (mediante cookies u otras tecnologías de seguimiento).",
    "This site supports your right to privacy and transparency. To comply with rights afforded to you under the latest data protection laws, this site maintains a record of your consent and allows you to exercise your rights as a data subject through the Privacy Contact section below.":
      "Esta web defiende tu derecho a la privacidad y a la transparencia. Para cumplir los derechos que te reconocen las leyes de protección de datos más recientes, esta web guarda un registro de tu consentimiento y te permite ejercer tus derechos como interesado a través del apartado «Contacto de privacidad» que hay más abajo.",
    "Consent is presumed not to be freely given if it does not allow separate consent to be given to different personal data processing operations.":
      "Se presume que el consentimiento no se ha dado libremente cuando no permite autorizar por separado las distintas operaciones de tratamiento de datos personales.",
    "Each controller shall maintain a record of processing activities and shall make the record available to the supervisory authority on request.":
      "Cada responsable llevará un registro de las actividades de tratamiento y lo pondrá a disposición de la autoridad de control cuando esta lo solicite.",
    "GDPR Recital 43": "Considerando 43 del RGPD",
    "GDPR Article 7": "Artículo 7 del RGPD",
    // protección y métricas
    "Protection & Metrics": "Protección y métricas",
    "View your consent record, and the list of 3rd parties blocked and allowed based on your settings.":
      "Consulta el registro de tu consentimiento y la lista de terceros bloqueados y permitidos según tus ajustes.",
    "Privacy Protection": "Protección de la privacidad",
    "Services Allowed": "Servicios permitidos",
    "Services Blocked": "Servicios bloqueados",
    "Your Consent Metrics": "Datos de tu consentimiento",
    "Date of Consent": "Fecha del consentimiento",
    "Data Access Level": "Nivel de acceso a los datos",
    "Consent ID": "ID del consentimiento",
    "Duration of Consent": "Duración del consentimiento",
    "Purpose Categories": "Categorías de finalidad",
    "Duration": "Duración",
    // documento y contacto
    "Privacy Paper": "Documento de privacidad",
    "Learn more about how we promote privacy and respect your right to control your data as your property.":
      "Descubre cómo promovemos la privacidad y respetamos tu derecho a controlar tus datos como algo tuyo.",
    "Privacy Contact": "Contacto de privacidad",
    "Reach out to us with any questions or concerns about your data privacy. Use the information below to get in touch.":
      "Escríbenos si tienes cualquier pregunta o inquietud sobre la privacidad de tus datos. Usa la información de abajo para ponerte en contacto.",
    "Other Ways to Opt Out": "Otras formas de oponerte",
    "Your Data Rights": "Tus derechos sobre tus datos",
    "File a Complaint": "Presentar una reclamación",
    // categorías
    "Basic Operations": "Operaciones básicas",
    "Content Personalisation": "Personalización de contenidos",
    "Site Optimisation": "Optimización de la web",
    "Ad Personalisation": "Personalización de anuncios",
    "Data Accessed": "Datos a los que se accede",
    "This type of sharing is necessary for us to access the data we need to make sure the website is secure and working properly.":
      "Este tipo de uso compartido es necesario para acceder a los datos que necesitamos para que la web sea segura y funcione correctamente.",
    "When enabled, you allow us to save your preferences and create a profile about you so we can deliver personalized content.":
      "Si lo activas, nos permites guardar tus preferencias y crear un perfil sobre ti para ofrecerte contenido personalizado.",
    "When enabled, this allows us to monitor your behavior so we can analyze and improve the services on our website for all visitors.":
      "Si lo activas, nos permites observar tu comportamiento para analizar y mejorar los servicios de nuestra web para todos los visitantes.",
    "When enabled, you allow us to share data with our advertising partners that build profiles about you across multiple websites.":
      "Si lo activas, nos permites compartir datos con nuestros socios publicitarios, que crean perfiles sobre ti a través de varias webs.",
    "Anonymous data like browser name and version": "Datos anónimos, como el nombre y la versión del navegador",
    "Pseudonymous data like authentication token": "Datos seudónimos, como el token de autenticación",
    "Personal data like your IP address and location": "Datos personales, como tu dirección IP y tu ubicación",
    "Anonymous data like device type, model and operating system": "Datos anónimos, como el tipo de dispositivo, el modelo y el sistema operativo",
    "Pseudonymous data like site browsing preferences": "Datos seudónimos, como tus preferencias de navegación en la web",
    "Personal data like content, search and purchase history": "Datos personales, como tu historial de contenidos, búsquedas y compras",
    "Anonymous data like the address of the previously visited website (HTTP Referer)": "Datos anónimos, como la dirección de la web visitada anteriormente (HTTP Referer)",
    "Pseudonymous data like website activity identifiers": "Datos seudónimos, como los identificadores de actividad en la web",
    "Personal data like your age, gender and demographics": "Datos personales, como tu edad, tu sexo y tus datos demográficos",
    "Anonymous data like affiliate referral links": "Datos anónimos, como los enlaces de referencia de afiliados",
    "Pseudonymous data like identifiers used to track and profile users": "Datos seudónimos, como los identificadores usados para seguir y perfilar a los usuarios",
    // botones sin texto visible (aria-label)
    "Close notice": "Cerrar aviso",
    "Download Consent": "Descargar consentimiento",
  };
  // textos con partes variables ({service}, {category}, números)
  const PATRONES = [
    [/^This content from (.+) is blocked$/, (m, s) => `Este contenido de ${s} está bloqueado`],
    [/^This sets your consent for (.+) on this website, not only for this content\.$/,
      (m, c) => `Esto guarda tu consentimiento para «${ES[c] || c}» en toda esta web, no solo para este contenido.`],
    [/^(.+) privacy policy$/, (m, s) => `Política de privacidad de ${s}`],
    [/^(\d+) days?$/, (m, n) => `${n} ${n === "1" ? "día" : "días"}`],
    [/^(\d+) months?$/, (m, n) => `${n} ${n === "1" ? "mes" : "meses"}`],
  ];
  const norm = t => t.replace(/[​ ]/g, " ").replace(/\s+/g, " ").trim();
  const traducir = t => {
    const n = norm(t);
    if (!n) return null;
    if (Object.prototype.hasOwnProperty.call(ES, n)) return ES[n];
    const sinDosPuntos = n.replace(/\s*:$/, "");  // «Data Accessed:» → «Datos a los que se accede:»
    if (sinDosPuntos !== n && Object.prototype.hasOwnProperty.call(ES, sinDosPuntos)) return ES[sinDosPuntos] + ":";
    for (const [re, f] of PATRONES) if (re.test(n)) return n.replace(re, f);
    return null;
  };
  const enEspanol = () => { try { return localStorage.getItem("epj-idioma") !== "en"; } catch (e) { return true; } };
  // el banner pone clases hu-… también en <body>: se excluyen body y html para no recorrer toda la web
  const BANNER = "#hu, [id^='hu-']:not(body):not(html), [class*='hu-']:not(body):not(html)";
  const ATRIBUTOS = ["aria-label", "title"];
  const original = new WeakMap();  // nodo de texto → texto original en inglés
  // conserva los espacios de alrededor del texto original
  const conEspacios = (orig, nuevo) => orig.match(/^\s*/)[0] + nuevo + orig.match(/\s*$/)[0];

  const textoNodo = (n, es) => {
    const actual = n.nodeValue;
    let orig = original.get(n);
    if (orig === undefined || (actual !== orig && actual !== conEspacios(orig, traducir(orig)))) {
      if (!traducir(actual)) { original.delete(n); return; }  // texto desconocido: se deja como está
      orig = actual; original.set(n, orig);
    }
    const quiero = es ? conEspacios(orig, traducir(orig)) : orig;
    if (actual !== quiero) n.nodeValue = quiero;
  };
  const atributosElemento = (el, es) => ATRIBUTOS.forEach(a => {
    if (!el.hasAttribute(a)) return;
    const clave = "huOrig" + (a === "title" ? "Title" : "Aria");
    const actual = el.getAttribute(a);
    if (el.dataset[clave] === undefined || (actual !== el.dataset[clave] && actual !== traducir(el.dataset[clave]))) {
      if (!traducir(actual)) return;
      el.dataset[clave] = actual;
    }
    const quiero = es ? traducir(el.dataset[clave]) : el.dataset[clave];
    if (actual !== quiero) el.setAttribute(a, quiero);
  });
  const procesar = raiz => {
    const es = enEspanol();
    const w = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) textoNodo(n, es);
    [raiz, ...raiz.querySelectorAll("[aria-label], [title]")].forEach(el => el.nodeType === 1 && atributosElemento(el, es));
  };
  const raices = () => [...document.querySelectorAll(BANNER)].filter(el => !el.parentElement || !el.parentElement.closest(BANNER));
  const todo = () => raices().forEach(procesar);

  let pendiente = false;
  new MutationObserver(cambios => {
    if (pendiente) return;
    if (!cambios.some(c => { const el = c.target.nodeType === 1 ? c.target : c.target.parentElement;
      return (el && el.closest(BANNER)) || [...c.addedNodes].some(n => n.nodeType === 1 && (n.matches(BANNER) || n.querySelector(BANNER))); })) return;
    pendiente = true;
    requestAnimationFrame(() => { pendiente = false; todo(); });
  }).observe(document.documentElement, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATRIBUTOS });
  document.addEventListener("idioma-cambiado", todo);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", todo); else todo();
})();
