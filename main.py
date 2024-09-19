import discord
import asyncio
import os
from pokemon_functions import get_new_pokemons
from flask import Flask
import threading
import logging

# Habilitar logging para la librería discord
logging.basicConfig(level=logging.DEBUG)

# Configura el cliente de Discord
intents = discord.Intents.default()
intents.messages = True  # Permiso para leer mensajes

client = discord.Client(intents=intents)

# ID del canal en el que quieres escribir
MY_CHANNEL_ID = os.getenv('MY_CHANNEL_ID')
TOKEN = os.getenv('TOKEN')

# Verificar si las variables de entorno están cargadas correctamente
print(f"TOKEN: {TOKEN}")
print(f"MY_CHANNEL_ID: {MY_CHANNEL_ID}")

if not MY_CHANNEL_ID:
    print("Error: MY_CHANNEL_ID no está definido")
else:
    MY_CHANNEL_ID = int(MY_CHANNEL_ID)  # Asegúrate de que sea un entero

if not TOKEN:
    print("Error: TOKEN no está definido")

# Crea el servidor Flask para mantener activo el bot
app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def home():
    return "Bot is running!", 200

def run():
    print("Servidor Flask está ejecutándose...")
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8000)))

def keep_alive():
    print("Iniciando el servidor Flask en un hilo separado")
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
    if not channel:
        print(f"Error: No se pudo encontrar el canal con ID {MY_CHANNEL_ID}")
        return

    while not client.is_closed():
        try:
            print("Procesando Pokémon...")
            # Cargar la lista de Pokémon
            mensaje = get_new_pokemons()
            print(f"Mensaje generado: {mensaje}")

            if mensaje != "":
                mensaje = "GitHub Info:\n" + mensaje
    
                # Envía el mensaje al canal
                await channel.send(mensaje)
                print(f"Mensaje enviado al canal {channel.name}")
            else:
                print("No hay nuevos Pokémon para enviar.")
    
            # Espera 10 minutos antes de ejecutar de nuevo el procesamiento
            print("Esperando 10 minutos para procesar de nuevo.")
            await asyncio.sleep(60 * 10)  # 10 minutos

        except Exception as e:
            print(f"Error en la tarea de procesamiento: {e}")
            # Si ocurre un error, espera 1 minuto antes de intentar de nuevo
            await asyncio.sleep(60)


try:
    print("Comienzo del programa")
    # Mantén el bot vivo utilizando Flask
    keep_alive()
    
    # Ejecuta el bot
    print("Iniciando el bot de Discord...")
    client.run(TOKEN)
except OSError as e:
    if "Address already in use" in str(e):
        print("El puerto 8000 ya está en uso. Verifica si hay otro proceso corriendo.")
    else:
        print(f"Error inesperado: {e}")
        raise e
