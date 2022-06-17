import os
import discord
import requests
from blizzardapi import BlizzardApi
# from keep_alive import keep_alive
from wow_realms import wowRealms
from utils import *

client = discord.Client()
  

@client.event
async def on_ready():
  print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return


  #List bot commands and how to use them
  if message.content.startswith('$commands'):
    await message.channel.send("$cmd charName serverName - cmd for affix is $affix, M+ is $mp, Arena is $arena")


  #Check current week Affixes in US
  if message.content.startswith('$affix'):
    aff = get_affix()
    
    await message.channel.send(aff['title'])
    

  #Checking Mythic Plus Score and Dungeon Key Completion Level
  if message.content.startswith('$mp'):
    split = message.content.split()
    if len(split) > 3:
      split[2] = f"{split[2]}-{split[3]}"
      
    realmName = split[2].lower().replace("'", "")
    if realmName in wowRealms:
      realmName = wowRealms[realmName]
      
    try:
      rio = get_cur_mythic_stats(realmName, split[1].lower())
    except:
      await message.channel.send("Error Fetching Data")
    
    embed = discord.Embed(
      title = f"{rio['name']} - {rio['race']} {rio['class']} ({rio['realm']})",
      url = f'https://raider.io/characters/us/{realmName}/{split[1].capitalize()}',
      description = f"Current M+ Score: {rio['mythic_plus_scores_by_season'][0]['scores']['all']}\nTop Ten High Scoring M+ Runs",
    )
    
    embed.set_thumbnail(url=rio['thumbnail_url'])
    for i in range(len(rio["mythic_plus_best_runs"])):
      embed.add_field(name=f"{rio['mythic_plus_best_runs'][i]['dungeon']}", value=f"{rio['mythic_plus_best_runs'][i]['mythic_level']}", inline=True)
    embed.set_footer(text=f"Last checked at {rio['last_crawled_at']}")
    await message.channel.send(embed = embed)
    

  #Checking Area Ratings
  if message.content.startswith('$arena'):
    split = message.content.split()
    if len(split) > 3:
      split[2] = f"{split[2]}-{split[3]}"
      
    realmName = split[2].lower().replace("'", "")
    if realmName in wowRealms:
      realmName = wowRealms[realmName]
      
    try:
      two, three, media = get_cur_arena_stats(realmName, split[1].lower())
    except:
      await message.channel.send("Error Fetching Data")

    embed = discord.Embed(
    title = f"{two['character']['name']} - {two['faction']['name']} ({two['character']['realm']['name']})",
    description = f"Current Arena Ratings:",
    )

    embed.set_thumbnail(url=media['assets'][0]['value'])
    embed.add_field(name="2v2", value=f"{two['rating']}", inline=True)
    embed.add_field(name="3v3", value=f"{three['rating']}", inline=True)
    await message.channel.send(embed = embed)


# keep_alive() #runs web server
# try:
#   client.run(os.environ['TOKEN'])
# except:
#   os.system("kill 1")