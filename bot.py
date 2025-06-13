import json
import os
import random
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# Google API imports
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import google.generativeai as genai

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# SCOPES = ['https://www.googleapis.com/auth/calendar']
# Scopes para acceder al calendario
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

user_notes = {}
user_reminders = {}
# Configura la API key de Gemini
genai.configure(api_key=GEMINI_API_KEY)
# Modelo Gemini Pro
gemini_model = genai.GenerativeModel(model_name='gemini-1.5-flash')

def get_calendar_service():
    creds = None
    token_path = 'token.pickle'
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def add_event_to_calendar(event: dict):
    service = get_calendar_service()

    # Construimos el evento en formato Google Calendar
    event_body = {
        'summary': event['title'],
        'start': {
            'dateTime': f"{event['date']}T{event['time']}:00",
            'timeZone': 'America/Santo_Domingo',  # cambia tu zona horaria
        },
        'end': {
            'dateTime': f"{event['date']}T{event['time']}:00",
            'timeZone': 'America/Santo_Domingo',
        },
    }

    event = service.events().insert(calendarId='primary', body=event_body).execute()
    return event.get('htmlLink')


# --- Funciones Bot ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_ayuda = """
🤖 *Dragon_Secretary* - Comandos disponibles:

/start - Saludo inicial y presentación del bot
/saludo - Mensaje de saludo casual
/hora - Muestra la hora actual
/chiste - Cuenta un chiste para alegrarte el día
/nota <texto> - Guarda una nota rápida
/vernotas - Muestra todas tus notas guardadas
/recordar <YYYY-MM-DD> <HH:MM> <texto> - Crea un recordatorio en Telegram y Google Calendar
/verrecordatorios - Lista tus recordatorios pendientes
/auth - Autoriza el acceso a tu Google Calendar (¡obligatorio para sincronizar recordatorios!)
/eventos - Muestra tus próximos eventos de Google Calendar
/help - Muestra esta ayuda

*Consejos para usar el bot:*
• Para crear recordatorios, usa el formato correcto de fecha y hora, por ejemplo:  
  `/recordar 2025-06-12 15:00 Comprar leche`
• Autoriza tu cuenta Google con /auth para que tus recordatorios se sincronicen.
• Si tienes dudas, usa /help en cualquier momento para recordar los comandos.
• Puedes chatear conmigo con mensajes normales para obtener respuestas inteligentes usando GEMINI AI.

¡Estoy aquí para ayudarte a ser más productivo! 🚀
"""
    await update.message.reply_text(texto_ayuda, parse_mode="Markdown")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy Dragon_Secretary, tu asistente productivo con estilo 🐲✨\n"
                                    "Para usar Google Calendar, primero autorízame con /auth")

async def saludo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Un saludo desde tu bot! 👋")

async def hora(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ahora = datetime.now().strftime("%H:%M:%S")
    await update.message.reply_text(f"La hora actual es: {ahora}")

async def chiste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chistes = [
        "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
        "¿Por qué los pájaros no usan Facebook? ¡Porque ya tienen Twitter!",
        "¿Qué le dice una impresora a otra? ¿Esa hoja es tuya o es una impresión mía?",
        "¿Sabes por qué los esqueletos no pelean entre ellos? Porque no tienen agallas.",
    ]
    await update.message.reply_text(random.choice(chistes))

async def nota(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    note_text = " ".join(context.args)
    if not note_text:
        await update.message.reply_text("📝 Usa el comando así: /nota comprar leche")
        return

    user_notes.setdefault(user_id, []).append(note_text)
    await update.message.reply_text("✅ Nota guardada.")

async def vernotas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    notas = user_notes.get(user_id, [])

    if not notas:
        await update.message.reply_text("🔍 No tienes notas guardadas.")
    else:
        respuesta = "\n".join(f"📌 {n}" for n in notas)
        await update.message.reply_text(respuesta)

# Recordatorios en Telegram y Google Calendar

async def recordar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if len(context.args) < 3:
        await update.message.reply_text("⏰ Uso: /recordar YYYY-MM-DD HH:MM Texto del recordatorio")
        return

    fecha_str = context.args[0]
    hora_str = context.args[1]
    try:
        dt = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        await update.message.reply_text("❌ Formato de fecha/hora incorrecto. Usa YYYY-MM-DD HH:MM")
        return

    if dt < datetime.now():
        await update.message.reply_text("❌ No puedes poner un recordatorio en el pasado.")
        return

    recordatorio_texto = " ".join(context.args[2:])
    user_reminders.setdefault(user_id, []).append((dt, recordatorio_texto))

    # Intentar crear evento en Google Calendar si autorizado
    try:
        service = get_calendar_service()
        event = {
            'summary': recordatorio_texto,
            'start': {'dateTime': dt.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': (dt + timedelta(minutes=30)).isoformat(), 'timeZone': 'UTC'},
        }
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        await update.message.reply_text(f"✅ Recordatorio guardado para {dt.strftime('%Y-%m-%d %H:%M')} y creado en Google Calendar.")
    except Exception as e:
        # Si falla Google Calendar, solo guarda el recordatorio Telegram
        await update.message.reply_text(f"✅ Recordatorio guardado para {dt.strftime('%Y-%m-%d %H:%M')}. "
                                        "Para sincronizar con Google Calendar usa /auth para autorizar.")
        print(f"Error Google Calendar: {e}")

async def verrecordatorios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    reminders = user_reminders.get(user_id, [])

    if not reminders:
        await update.message.reply_text("⏳ No tienes recordatorios pendientes.")
        return

    texto = ""
    for dt, text in reminders:
        texto += f"⏰ {dt.strftime('%Y-%m-%d %H:%M')}: {text}\n"

    await update.message.reply_text(texto)

async def check_reminders(app):
    while True:
        now = datetime.now()
        for user_id, reminders in list(user_reminders.items()):
            pendientes = []
            for dt, text in reminders:
                if dt <= now:
                    try:
                        await app.bot.send_message(chat_id=user_id, text=f"🔥 Recordatorio: {text}")
                    except Exception as e:
                        print(f"Error enviando recordatorio: {e}")
                else:
                    pendientes.append((dt, text))
            user_reminders[user_id] = pendientes


        await asyncio.sleep(60)  # chequea cada minuto

# Gemini AI Chatbot

async def extract_event_from_text_gemini(text: str) -> dict:
    prompt = f"""
Extrae un evento del siguiente mensaje y devuélvelo como JSON con el formato:
{{
    "title": "...",
    "date": "YYYY-MM-DD",
    "time": "HH:MM"
}}

Mensaje: "{text}"

Si no se encuentra información suficiente, devuelve un JSON vacío.
"""
    try:
        response = gemini_model.generate_content(prompt)
        raw = response.text.strip()

        # Busca el bloque de JSON en el texto
        start = raw.find("{")
        end = raw.rfind("}") + 1
        json_data = raw[start:end]

        event = json.loads(json_data)

        # Validación mínima
        if "title" in event and "date" in event and "time" in event:
            return event
        return {}
    except Exception as e:
        print(f"❌ Error extrayendo evento con Gemini: {e}")
        return {}


async def gemini_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        # Pregunta a Gemini
        response = gemini_model.generate_content(user_message)
        reply_text = response.text.strip()
        await update.message.reply_text(reply_text)

        # Intentamos extraer un evento del mensaje
        event = await extract_event_from_text_gemini(user_message)
        if event:
            await update.message.reply_text(
                f"📅 Evento detectado:\n📝 {event['title']}\n📆 {event['date']}\n⏰ {event['time']}"
            )

            # Aquí podrías agregarlo automáticamente a tu calendario con otra función, ej:
            # await add_event_to_calendar(event)
            link = add_event_to_calendar(event)
            await update.message.reply_text(f"✅ Evento añadido a tu calendario:\n🔗 {link}")
    except Exception as e:
        await update.message.reply_text("❌ Error al comunicarse con Gemini AI.")
        print(f"Gemini Error: {e}")


# Google Calendar Auth command

async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Explica al usuario cómo autorizar su cuenta Google.
    """
    # user_id = update.message.from_user.id
    await update.message.reply_text(
        "Para autorizar tu Google Calendar, se abrirá una ventana de autorización en tu navegador.\n"
        "Si estás usando un servidor sin navegador, tendrás que copiar y pegar el link en otro dispositivo.\n"
        "Sigue las instrucciones para autorizar el acceso.\n\n"
        "Esto permite sincronizar recordatorios con Google Calendar."
    )
    # Iniciar flujo OAuth y guardar token para este user
    # En esta implementación, get_google_calendar_service abre la ventana y guarda token en disco,
    # por eso sólo llamamos a esa función una vez para que el usuario autorice.
    try:
        service = get_calendar_service()
        await update.message.reply_text("✅ Google Calendar autorizado con éxito.")
    except Exception as e:
        await update.message.reply_text("❌ Falló la autorización. Intenta de nuevo más tarde.")
        print(f"Error en autorización Google Calendar: {e}")

# Comando para listar próximos eventos Google Calendar

async def eventos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # user_id = update.message.from_user.id
    try:
        service = get_calendar_service()
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indica UTC
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            await update.message.reply_text('No tienes próximos eventos en Google Calendar.')
            return

        texto = "📅 Próximos eventos:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            texto += f"- {start}: {event['summary']}\n"

        await update.message.reply_text(texto)
    except Exception as e:
        await update.message.reply_text("❌ No se pudieron obtener los eventos. ¿Has autorizado con /auth?")
        print(f"Error al obtener eventos Google Calendar: {e}")

# --- MAIN ---

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers comandos básicos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("saludo", saludo))
    app.add_handler(CommandHandler("hora", hora))
    app.add_handler(CommandHandler("chiste", chiste))
    app.add_handler(CommandHandler("nota", nota))
    app.add_handler(CommandHandler("vernotas", vernotas))
    app.add_handler(CommandHandler("help", help_command))


    # Recordatorios Telegram + Google Calendar
    app.add_handler(CommandHandler("recordar", recordar))
    app.add_handler(CommandHandler("verrecordatorios", verrecordatorios))

    # Google Calendar
    app.add_handler(CommandHandler("auth", auth))
    app.add_handler(CommandHandler("eventos", eventos))

    # GEMINI AI para mensajes normales
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gemini_chat))

    print("🤖 Bot iniciado... Esperando comandos")

    # Tarea background para recordatorios Telegram
    asyncio.get_event_loop().create_task(check_reminders(app))

    app.run_polling()
