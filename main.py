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
    client.bg_task = client.loop.create_task(procesar_y_enviar_mensaje())


# Funcion de procesamiento que quieres ejecutar periodicamente
async def procesar_y_enviar_mensaje():
    await client.wait_until_ready()
    print("El bot está listo y ejecutando la tarea de procesamiento")
    channel = client.get_channel(MY_CHANNEL_ID)

    while not client.is_closed():
        print("Procesando Pokémon...")
        # Cargar la lista de Pokémon
        mensaje = get_new_pokemons()
        #mensaje = "Hola Mundo"

        # Envía el mensaje al canal
        if channel:
            await channel.send(mensaje)
        else:
            print("No se pudo encontrar el canal.")

        # Espera 10 segundos antes de ejecutar de nuevo el procesamiento
        await asyncio.sleep(60*10)  # Ajusta el tiempo según tus necesidades

# Mantén el bot vivo utilizando Flask
keep_alive()

# Ejecuta el bot
client.run(TOKEN)
print("HELLO")
