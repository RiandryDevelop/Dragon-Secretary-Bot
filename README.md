# 🐉 Dragon_Secretary – Telegram Productivity Bot con Gemini AI

**Dragon_Secretary** es un bot de Telegram inteligente y productivo que actúa como un asistente personal con personalidad de dragón 🐲✨.
Permite gestionar **notas**, **recordatorios**, **eventos en Google Calendar** y conversar de forma natural usando **Gemini AI**.

> Diseñado para ser **proactivo**, **amigable** y **orientado a productividad**, combinando automatización, IA generativa y servicios cloud.

---

## 🚀 Funcionalidades principales

* 🤖 Chat inteligente con **Gemini AI**
* 📝 Notas rápidas por usuario
* ⏰ Recordatorios locales en Telegram
* 📅 Sincronización con Google Calendar
* 🔔 Notificaciones automáticas
* 🧠 Detección automática de eventos desde texto
* 👤 Contexto de conversación por usuario
* 🌍 Soporte de zona horaria (configurable)

---

## 📋 Comandos disponibles

| Comando                              | Descripción                |
| ------------------------------------ | -------------------------- |
| `/start`                             | Mensaje inicial del bot    |
| `/help`                              | Lista completa de comandos |
| `/saludo`                            | Saludo casual              |
| `/hora`                              | Hora actual                |
| `/chiste`                            | Chiste aleatorio           |
| `/nota <texto>`                      | Guarda una nota            |
| `/vernotas`                          | Muestra tus notas          |
| `/recordar YYYY-MM-DD HH:MM <texto>` | Crea un recordatorio       |
| `/verrecordatorios`                  | Lista recordatorios        |
| `/auth`                              | Autoriza Google Calendar   |
| `/eventos`                           | Lista próximos eventos     |

---

## 🧠 Inteligencia Artificial (Gemini)

El bot utiliza **Gemini 1.5 Flash** para:

* Responder mensajes normales de forma conversacional
* Mantener contexto reciente por usuario
* Detectar automáticamente eventos dentro de mensajes como:

> “Reunión con el cliente mañana a las 3pm”

### Flujo automático

1. El usuario escribe un mensaje
2. Gemini analiza el texto
3. Se extrae título, fecha y hora
4. El evento se confirma
5. Se crea en Google Calendar

---

## 📅 Google Calendar

### Funcionalidades

* Sincronización de recordatorios
* Creación automática de eventos
* Consulta de próximos eventos

### Autorización

Cada usuario debe ejecutar `/auth` una vez para permitir el acceso a su calendario.
Los tokens OAuth se almacenan localmente por usuario en la carpeta `tokens/`.

---

## 🧩 Arquitectura general

* **Telegram Bot API** → Interfaz con usuarios
* **Gemini AI** → IA conversacional y NLP
* **Google Calendar API** → Eventos y recordatorios
* **AsyncIO** → Tareas en segundo plano
* **In-memory storage** → Notas, contexto y recordatorios

⚠️ Actualmente los datos se almacenan en memoria.
Para producción se recomienda Redis o base de datos persistente.

---

## ⚙️ Variables de entorno requeridas

Configura las siguientes variables en tu entorno (`.env`, Railway o VPS):

* `BOT_TOKEN` → Token del bot de Telegram
* `GEMINI_API_KEY` → API Key de Google Gemini
* `GOOGLE_CREDENTIALS_JSON` → Credenciales OAuth de Google (JSON completo)

El archivo `credentials.json` se genera automáticamente si no existe.

---

## 🔄 Recordatorios automáticos

* Revisión cada 60 segundos
* Envío automático de notificaciones
* Eliminación de recordatorios ejecutados
* Proceso asíncrono no bloqueante

---

## 🔐 Seguridad y consideraciones

* Tokens OAuth aislados por usuario
* No se comparten datos entre usuarios
* Credenciales sensibles gestionadas por variables de entorno
* Compatible con Railway, Docker y VPS

---

## ⚠️ Limitaciones actuales

* Almacenamiento en memoria (no persistente)
* Zona horaria fija por defecto
* No hay panel administrativo

---

## 🧭 Mejoras futuras sugeridas

* Persistencia con Redis / PostgreSQL
* Configuración de zona horaria por usuario
* Panel web administrativo
* Soporte multi-idioma
* Logs estructurados
* Deploy con Docker

---

## 📄 Aviso Legal

DragonSecretaryBot es un software desarrollado y propiedad de **Riandry Connor**.

El uso de este software está sujeto a una licencia.
Cualquier uso no autorizado, incluyendo copia, modificación, redistribución, ingeniería inversa o comercialización sin licencia válida, está estrictamente prohibido.

Este producto no está afiliado, patrocinado ni respaldado por Telegram, Google u OpenAI.

© 2025 **DragonSecretaryBot**. Todos los derechos reservados.

---

## 📜 Términos de Uso (Resumen)

* Uso gratuito limitado para fines personales, educativos o de prueba.
* Uso comercial o en producción requiere licencia válida.
* Prohibida la redistribución, modificación o reventa sin autorización.
* El software se proporciona “tal cual”, sin garantías.
* El uso continuado implica aceptación de posibles cambios en los términos.

Para ver los términos completos o adquirir una licencia comercial, contactar:
👉 **📧 riandrydevsoffers@gmail.com**

---

## 📩 Contacto y licencias

📧 riandrydevsoffers@gmail.com

---

**Dragon_Secretary**
*Un dragón que organiza tu vida.* 🐲✨
