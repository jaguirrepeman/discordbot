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

# Variable global para la tarea
bg_task = None

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    
    global bg_task
    # Verifica si la tarea ya se está ejecutando
    if bg_task is None or bg_task.done():  # Si la tarea no existe o ha terminado
        print("Iniciando la tarea de procesamiento.")
        bg_task = client.loop.create_task(procesar_y_enviar_mensaje())
    else:
        print("La tarea ya está corriendo, no se iniciará de nuevo.")

# Funcion de procesamiento que quieres ejecutar periodicamente
async def procesar_y_enviar_mensaje():
    await client.wait_until_ready()
    print("El bot está listo y ejecutando la tarea de procesamiento")
    channel = client.get_channel(MY_CHANNEL_ID)

    while not client.is_closed():
        try:
            print("Procesando Pokémon...")
            # Cargar la lista de Pokémon
            mensaje = get_new_pokemons()
            if mensaje != "":
                mensaje = "GitHub Info:\n" + mensaje
    
                # Envía el mensaje al canal
                if channel:
                    await channel.send(mensaje)
                else:
                    print("No se pudo encontrar el canal.")
    
            # Espera 10 minutos antes de ejecutar de nuevo el procesamiento
            await asyncio.sleep(60 * 10)  # 10 minutos

        except Exception as e:
            print(f"Error en la tarea de procesamiento: {e}")
            # Si ocurre un error, espera 1 minuto antes de intentar de nuevo
            await asyncio.sleep(60)

# Mantén el bot vivo utilizando Flask
keep_alive()

# Ejecuta el bot
client.run(TOKEN)
