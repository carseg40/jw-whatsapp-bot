import os, re, time, tldextract, textwrap, requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from bs4 import BeautifulSoup
from readability import Document
from waitress import serve

# -------------------------
# Config básica
# -------------------------
ALLOWED_DOMAIN = "jw.org"
USER_AGENT = "Mozilla/5.0 (personal-use-bot; respectful)"
TIMEOUT = 10
MAX_CHARS = 1500
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_REQ = 5

rate_memory = {}

app = Flask(__name__)

def rate_limited(phone):
    now = time.time()
    window = rate_memory.get(phone, [])
    window = [t for t in window if now - t < RATE_LIMIT_WINDOW]
    if len(window) >= RATE_LIMIT_MAX_REQ:
        rate_memory[phone] = window
        return True
    window.append(now)
    rate_memory[phone] = window
    return False

def is_allowed_url(url: str) -> bool:
    try:
        ext = tldextract.extract(url)
        domain = ".".join([p for p in [ext.domain, ext.suffix] if p])
        return domain.endswith(ALLOWED_DOMAIN)
    except Exception:
        return False

def fetch_page(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text

def clean_text(txt: str) -> str:
    txt = re.sub(r"\s+\n", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    txt = re.sub(r"[ \t]{2,}", " ", txt)
    return txt.strip()

def extract_main_text(html: str) -> str:
    try:
        doc = Document(html)
        summary_html = doc.summary(html_partial=True)
        soup = BeautifulSoup(summary_html, "lxml")
        text = soup.get_text("\n")
        text = clean_text(text)
        if len(text) > 150:
            return text
    except Exception:
        pass

    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = soup.get_text("\n")
    return clean_text(text)

def summarize_text(text: str, max_sentences: int = 6) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    summary = " ".join(sentences[:max_sentences]).strip()
    if len(summary) > MAX_CHARS:
        summary = summary[:MAX_CHARS].rsplit(" ", 1)[0] + "…"
    return summary

def find_snippets(text: str, phrase: str, radius: int = 120) -> str:
    text_low = text.lower()
    phrase_low = phrase.lower()
    hits = []
    start = 0
    while True:
        idx = text_low.find(phrase_low, start)
        if idx == -1 or len(hits) >= 5:
            break
        s = max(0, idx - radius)
        e = min(len(text), idx + len(phrase) + radius)
        snippet = text[s:e].replace("\n", " ")
        hits.append("… " + snippet.strip() + " …")
        start = idx + len(phrase)
    if not hits:
        return "No encontré esa frase exacta en la página."
    joined = "\n\n".join(hits)
    if len(joined) > MAX_CHARS:
        joined = joined[:MAX_CHARS].rsplit(" ", 1)[0] + "…"
    return joined

HELP_TEXT = textwrap.dedent("""
Comandos disponibles:

1) resumen <URL>
   Resume el contenido principal de esa URL.

2) buscar "<frase>" <URL>
   Muestra fragmentos donde aparece la frase.

3) explica <URL> "<tema>"
   Explica brevemente el contenido centrado en un tema.

Ejemplos:
- resumen https://www.jw.org/es/...
- buscar "amor al projimo" https://www.jw.org/es/...
- explica https://www.jw.org/es/... "contexto historico"
""").strip()

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    from_number = request.form.get("From", "unknown")
    body = (request.form.get("Body") or "").strip()

    resp = MessagingResponse()
    msg = resp.message()

    if rate_limited(from_number):
        msg.body("Has enviado varias solicitudes seguidas. Intenta de nuevo en un minuto.")
        return str(resp)

    if not body:
        msg.body("Envía 'ayuda' para ver los comandos.")
        return str(resp)

    try:
        if body.lower().startswith("resumen "):
            url = body.split(None, 1)[1].strip()
            if not is_allowed_url(url):
                msg.body("Solo puedo analizar páginas de jw.org.")
                return str(resp)
            html = fetch_page(url)
            text = extract_main_text(html)
            out = "Resumen:\n" + summarize_text(text)
            msg.body(out)

        elif body.lower().startswith("buscar "):
            m = re.search(r'buscar\s+"([^"]+)"\s+(\S+)', body, flags=re.IGNORECASE)
            if not m:
                msg.body('Formato correcto:\nbuscar "frase" <URL>')
                return str(resp)
            phrase, url = m.group(1), m.group(2)
            if not is_allowed_url(url):
                msg.body("Solo puedo analizar páginas de jw.org.")
                return str(resp)
            html = fetch_page(url)
            text = extract_main_text(html)
            out = f'Coincidencias para "{phrase}":\n\n' + find_snippets(text, phrase)
            msg.body(out)

        elif body.lower().startswith("explica "):
            m = re.search(r'explica\s+(\S+)\s+"([^"]+)"', body, flags=re.IGNORECASE)
            if not m:
                msg.body('Formato correcto:\nexplica <URL> "tema"')
                return str(resp)
            url, tema = m.group(1), m.group(2)
            if not is_allowed_url(url):
                msg.body("Solo puedo analizar páginas de jw.org.")
                return str(resp)
            html = fetch_page(url)
            text = extract_main_text(html)
            base = summarize_text(text, max_sentences=8)
            out = f'Explicación sobre "{tema}":\n{base}'
            msg.body(out)

        elif body.lower() in ("ayuda", "help", "menu"):
            msg.body(HELP_TEXT)

        else:
            msg.body("No entendí.\n\n" + HELP_TEXT)

    except requests.HTTPError as e:
        msg.body(f"Error HTTP ({e.response.status_code}).")
    except requests.RequestException:
        msg.body("No pude conectar con la URL.")
    except Exception:
        msg.body("Ocurrió un error procesando tu solicitud.")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    serve(app, host="0.0.0.0", port=port)
