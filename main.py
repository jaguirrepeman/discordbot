import discord
import asyncio
import sys
import os
from pokemon_functions import get_new_pokemons
from flask import Flask
import threading

# Configura el cliente de Discord
intents = discord.Intents.default()
intents.messages = True  # Permiso para leer mensajes

client = discord.Client(intents=intents)

# ID del canal en el que quieres escribir
MY_CHANNEL_ID = int(os.getenv('MY_CHANNEL_ID'))
TOKEN = os.getenv('TOKEN')

# Crea el servidor Flask para mantener activo el bot
app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def home():
    return "Bot is running!", 200

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    thread = threading.Thread(target=run)
    thread.start()

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    if not hasattr(client, 'bg_task'):
        # Solo inicia la tarea si no se ha iniciado previamente
        client.bg_task = client.loop.create_task(procesar_y_enviar_mensaje())
        print("Tarea de procesamiento iniciada")

# Función de procesamiento que quieres ejecutar periódicamente
async def procesar_y_enviar_mensaje():
    await client.wait_until_ready()
    print("El bot está listo y ejecutando la tarea de procesamiento")
    channel = client.get_channel(MY_CHANNEL_ID)

    while not client.is_closed():
        try:
            print("Procesando Pokémon...")
            # Cargar la lista de Pokémon
            mensaje = get_new_pokemons()
            mensaje = "GitHub Info:\n" + mensaje

            # Envía el mensaje al canal
            if channel:
                await channel.send(mensaje)
            else:
                print("No se pudo encontrar el canal.")

            # Espera 10 minutos antes de ejecutar de nuevo el procesamiento
            await asyncio.sleep(60*10)
        
        except Exception as e:
            print(f"Ocurrió un error: {e}")
            await asyncio.sleep(60)  # Espera un minuto antes de reintentar

# Mantén el bot vivo utilizando Flask
keep_alive()

# Ejecuta el bot
client.run(TOKEN)
