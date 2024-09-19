import discord
from discord.ext import tasks
import requests
import asyncio
from flask import Flask
from threading import Thread
import os
from pokemon_functions import get_new_pokemons

# Configuración
MY_CHANNEL_ID = int(os.getenv('MY_CHANNEL_ID'))
TOKEN = os.getenv('TOKEN')

# Verificar si las variables de entorno están cargadas correctamente
print(f"TOKEN: {TOKEN}")
print(f"MY_CHANNEL_ID: {MY_CHANNEL_ID}")

intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)

# Flask app para la salud del servidor
app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def home():
    return "Bot is running", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))  # Usar un puerto diferente si 8000 está ocupado
    print(f"Servidor Flask está ejecutándose en el puerto {port}...")
    app.run(port=port)

# Función que se ejecuta cuando el bot está listo
@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    procesar_pokemons.start()  # Inicia la tarea periódica de procesamiento
    print('Iniciando la tarea de procesamiento.')
    # Inicia el servidor Flask en un hilo separado
    Thread(target=run_flask).start()

# Tarea asíncrona que se ejecuta cada 10 minutos
@tasks.loop(minutes=10)
async def procesar_pokemons():
    channel = client.get_channel(MY_CHANNEL_ID)
    if channel:
        print('Procesando Pokémon...')
        mensaje = get_new_pokemons()
        if mensaje != "":
            mensaje = "GitHub Info:\n" + mensaje

            # Envía el mensaje al canal
            await channel.send(mensaje)
            print(f"Mensaje enviado al canal {channel.name}")
        else:
            print("No hay nuevos Pokémon para enviar.")

    else:
        print('No se encontró el canal.')

# Arranca el bot de Discord
client.run(TOKEN)
