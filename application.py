import os
import discord
import requests
from dotenv import load_dotenv
# from stay_alive import keep_alive
from blizzardapi import BlizzardApi
from wow_realms import wowRealms
from flask import Flask

application = Flask(__name__)

@application.route('/')
def home():
  return "Hello. I am alive!"

load_dotenv()
client = discord.Client()
api_client = BlizzardApi(os.environ['WOW_CLIENT'], os.environ['WOW_SECRET'])

def get_cur_mythic_stats(realm, name):
  data = requests.get(f"https://raider.io/api/v1/characters/profile?region=us&realm={realm}&name={name}&fields=mythic_plus_scores_by_season%3Acurrent%2Cmythic_plus_best_runs")
  data = data.json()
  return data

def get_cur_raid_stats(realm, name):
  data = requests.get(f"https://raider.io/api/v1/characters/profile?region=us&realm={realm}&name={name}&fields=raid_progression")
  data = data.json()
  return data

def get_cur_arena_stats(realm, name):
  twovtwo = api_client.wow.profile.get_character_pvp_bracket_statistics("us", "en_US", realm, name, pvp_bracket="2v2")
  if 'code' in twovtwo:
    twovtwo = {'code': 404, 'rating': 0}

  threevthree = api_client.wow.profile.get_character_pvp_bracket_statistics("us", "en_US", realm, name, pvp_bracket="3v3")
  if 'code' in threevthree:
    threevthree = {'code': 404, 'rating': 0}

  media = api_client.wow.profile.get_character_media_summary("us", "en_US", realm, name)

  return twovtwo, threevthree, media
  
def get_affix():
  aff = requests.get("https://raider.io/api/v1/mythic-plus/affixes?region=us&locale=en")
  aff = aff.json()
  return aff


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
      
      
    two, three, media = get_cur_arena_stats(realmName, split[1].lower())

    if 'code' in two:
      if 'code' in three:
        title2 = "No Arena Ratings Found"
      else:
        title2 = f"{split[1].capitalize()} - {three['faction']['name']} ({three['character']['realm']['name']})"
    else:
      title2 = f"{split[1].capitalize()} - {two['faction']['name']} ({two['character']['realm']['name']})"

    embed = discord.Embed(
    title = title2,
    url = f'https://worldofwarcraft.com/en-us/character/us/{realmName}/{split[1]}',
    description = f"Current Arena Ratings:",
    )

    embed.set_thumbnail(url=media['assets'][0]['value'])
    embed.add_field(name="2v2", value=f"{two['rating']}", inline=True)
    embed.add_field(name="3v3", value=f"{three['rating']}", inline=True)
    await message.channel.send(embed = embed)


# keep_alive() #runs web server

client.run(os.environ['TOKEN'])

