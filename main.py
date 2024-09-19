import discord
from discord.ext import tasks
import asyncio

# ID del canal en el que quieres escribir
MY_CHANNEL_ID = os.getenv('MY_CHANNEL_ID')
TOKEN = os.getenv('TOKEN')
print(f"TOKEN: {TOKEN}")
print(f"MY_CHANNEL_ID: {MY_CHANNEL_ID}")
if not MY_CHANNEL_ID:
    print("Error: MY_CHANNEL_ID no está definido")
else:
    MY_CHANNEL_ID = int(MY_CHANNEL_ID)  # Asegúrate de que sea un entero

intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    procesar_pokemons.start()  # Inicia la tarea asíncrona periódica

@tasks.loop(minutes=10)
async def procesar_pokemons():
    channel = client.get_channel(MY_CHANNEL_ID)
    if channel:
        print('Procesando Pokémon...')
        # Aquí puedes implementar la lógica de obtener y enviar mensajes
        mensajes = await obtener_mensajes_nuevos(channel)  # Función que obtiene nuevos mensajes de Pokémon
        if mensajes:
            for mensaje in mensajes:
                await channel.send(mensaje)
        else:
            print('No hay nuevos Pokémon para enviar.')
    else:
        print('No se encontró el canal.')

async def obtener_mensajes_nuevos(channel):
    # Implementa la lógica para obtener nuevos Pokémon o mensajes
    # Esto es solo un ejemplo
    messages = await channel.history(limit=10).flatten()
    nuevos_pokemons = []  # Aquí añades los nuevos Pokémon si los hay
    return nuevos_pokemons

client.run(TOKEN)

