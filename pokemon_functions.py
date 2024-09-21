import requests
import json
from datetime import datetime
import pandas as pd
import re
import os
# import time

import discord
from discord.ext import commands

def read_captured_pokemon():
    sheet_name = 'pokemon' # replace with your own sheet name
    SHEET_ID = os.getenv('SHEET_ID')
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    pokemon_captured = pd.read_csv(url)\
        .loc[lambda x: ~x.name.str.contains(r"\(Mega\)")]\
        .rename(columns = {"level": "level_captured", "name": "complete_name"})\
        .drop("number", axis = 1)
    return pokemon_captured


def check_spawns(channel_id):

    AUTH = os.getenv('AUTH')

    headers = {
        'authorization': AUTH
    }
        
    r = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers)
    
    jsonn = json.loads(r.text)
    
    # for value in jsonn:
    #     print(value, '\n')
    return jsonn

def parse_spawn(msj):
    try:
        name_html = msj['embeds'][0]['fields'][0]['name']

        # Expresión regular para encontrar el nombre y el genero del Pokémon
        patron = r"\*\*(\w+)\*\*(?: \*\*\((.+?)\)\*\*)?.*?(<:(female|male|genderless):\d+>)?"
        patron = r"\*\*(\w+)\*\*(?: \*\*\((.+?)\)\*\*)?.*?<:(female|male|genderless):\d+>"

        # Buscar el nombre en la línea
        pokemon = re.search(patron, name_html)

        nombre_pokemon = pokemon.group(1)
        forma_pokemon = pokemon.group(2) if pokemon.group(2) else ""
        genero_emoji = pokemon.group(3) if pokemon.group(3) else "Desconocido"
        genero = {
            "female": "Femenino",
            "male": "Masculino",
            "genderless": "Sin Genero"
        }.get(genero_emoji, "Desconocido")
        nombre_completo = f"{nombre_pokemon} ({forma_pokemon})" if forma_pokemon != "" else nombre_pokemon

        level = msj['embeds'][0]['fields'][0]['value'].split('|')[1].split()[1]
        # try:
        #     ms = msj['embeds'][0]['fields'][0]['value'].split('|')[2].split('\n')[2].split('*')[1].split(':')[1]#.replace(r'\s', '')
        #     despawn_time = datetime.datetime.fromtimestamp(int(ms)).isoformat()
        # except:
        #     print(f"No date on {msj}")
        #     ms = None
        #     despawn_time = None

        patron_fecha = r"<t:(\d+):[RT]>"
        fecha_html = msj['embeds'][0]['fields'][0]['value'].split('|')[2]
        # Buscar el timestamp en el mensaje
        timestamps = re.findall(patron_fecha, fecha_html)

        # Convertir los timestamps Unix a una fecha legible
        if timestamps:
            timestamp = int(timestamps[0])
            fecha_despawn = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            print("No se encontró un timestamp.")
        
        df = pd.DataFrame({
            'name': nombre_pokemon,
            'form': forma_pokemon,
            'complete_name': nombre_completo,
            'gender': genero,
            'level': level,
            'despawn_time': fecha_despawn
        }, index = [0])

        return df
    except:
        print(msj)

def filter_spawns(spawns_df, min_level = 20):
  
  pokemon_captured = read_captured_pokemon()
  future_spawns_df = spawns_df\
    .loc[lambda x: pd.to_datetime(x.despawn_time) >= datetime.now()]\
    .merge(pokemon_captured, how = "left", on = "complete_name")\
    .assign(level = lambda x: x.level.astype(float))\
    .loc[lambda x: ~((x.iv_max == 100)&(x.level_captured >= x.level))]\
    .sort_values("despawn_time")
  
  if min_level is not None:
    future_spawns_df = future_spawns_df\
      .loc[lambda x: x.level >= min_level]
  
  return future_spawns_df

def imprimir_despawn_info(df):
    
    now = datetime.now()
    mensaje = ""
    
    for index, row in df.iterrows():
        complete_name = row['complete_name']
        level = row['level']
        despawn_time_str = row['despawn_time']
        despawn_time = datetime.strptime(despawn_time_str, '%Y-%m-%d %H:%M:%S')

        # Calcular el tiempo restante hasta el despawn
        time_remaining = despawn_time - now
        total_seconds = int(time_remaining.total_seconds())

        # Convertir el tiempo restante a minutos y segundos
        minutes, seconds = divmod(total_seconds, 60)
        
        # Formatear en MM:SS
        formatted_time = f"{minutes:02}:{seconds:02}"
        
        # print(f"Pokémon: {complete_name} | Nivel: {level} | Tiempo restante hasta el despawn: {formatted_time}")
        mensaje += f"Pokémon: {complete_name}\nNivel: {level}\nTiempo restante hasta el despawn: {formatted_time}\n\n"
    return mensaje

def get_new_pokemons():
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    print(CHANNEL_ID)
    spawns_json = check_spawns(CHANNEL_ID)
    spawns_df = pd.concat([parse_spawn(spawns_json[i]) for i in range(len(spawns_json))])
    future_spawns_df = filter_spawns(spawns_df)
    mensaje = imprimir_despawn_info(future_spawns_df)
    return mensaje
