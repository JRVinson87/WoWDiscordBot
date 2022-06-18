import requests
from application import api_client

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

  threevthree = api_client.wow.profile.get_character_pvp_bracket_statistics("us", "en_US", realm, name, pvp_bracket="3v3")

  media = api_client.wow.profile.get_character_media_summary("us", "en_US", realm, name)

  return twovtwo, threevthree, media
  
def get_affix():
  aff = requests.get("https://raider.io/api/v1/mythic-plus/affixes?region=us&locale=en")
  aff = aff.json()
  return aff