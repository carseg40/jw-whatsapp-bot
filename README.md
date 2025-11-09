# JW WhatsApp Bot (Uso personal)

Bot que analiza **solo páginas específicas de `jw.org`** mediante comandos enviados desde WhatsApp.  
Este bot es legal porque **no hace scraping masivo**, **no recorre el sitio**, y **solo procesa URLs que el usuario envía manualmente**, extrayendo y resumiendo su contenido de forma limitada.

✅ Uso personal  
✅ Hosting gratuito en Render  
✅ Conexión vía Twilio WhatsApp Sandbox  
✅ No descarga ni indexa el sitio entero

---

## ✅ Comandos disponibles

### **1) Resumir una página**
resumen <URL>

makefile
Copiar código

Ejemplo:
resumen https://www.jw.org/es/biblioteca/articulos/...

yaml
Copiar código

---

### **2) Buscar una frase dentro del contenido**
buscar "frase" <URL>

makefile
Copiar código

Ejemplo:
buscar "reino de dios" https://www.jw.org/es/...

yaml
Copiar código

---

### **3) Explicar un tema basado en la página**
explica <URL> "tema"

makefile
Copiar código

Ejemplo:
explica https://www.jw.org/es/... "contexto histórico"

markdown
Copiar código

---

## ✅ Instalación en Render (hosting gratis)

1. Crear un repositorio en GitHub  
2. Subir estos archivos:
   - `app.py`
   - `requirements.txt`
   - `render.yaml`
3. Entrar a https://render.com  
4. Crear un **New Web Service** y conectar tu repositorio  
5. Render tomará automáticamente:
   - `requirements.txt` para instalar dependencias  
   - `render.yaml` para saber cómo iniciar la app  
6. Render te dará una URL tipo:
https://tu-app.onrender.com

yaml
Copiar código

---

## ✅ Conexión con Twilio WhatsApp Sandbox

1. Crear cuenta en Twilio: https://www.twilio.com/whatsapp  
2. Activar el sandbox enviando el código a su número  
3. En la configuración del sandbox, en **WHEN A MESSAGE COMES IN**, colocar:
https://TU-APP.onrender.com/whatsapp

yaml
Copiar código
4. Guardar

Ahora el bot responde a cualquier mensaje enviado a tu número de sandbox en WhatsApp.

---

## ✅ Notas

- Solo funciona con URLs de `jw.org`
- Tiene límite de peticiones por minuto para evitar abuso  
- Está pensado solo para **uso personal y educativo**  
- Para producción real deberías usar WhatsApp Cloud API

---

## ✅ Listo
Con esto tendrás el bot funcionando en WhatsApp las 24 horas sin pagar hosting.
