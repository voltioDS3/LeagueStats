import json
import os
import time
from argparse import RawDescriptionHelpFormatter
from email.policy import HTTP
from msilib.schema import Error
from time import process_time_ns

from urllib import response
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import requests
from requests.exceptions import HTTPError
import threading
import queue


### CUSTOM ERRORS ###
class Error(Exception):
    """Base class for other exceptions"""

    pass


class BLANKError(Error):
    """Raised when the input value is too small"""

    pass


class IDError(Error):
    """Raised when the input value is too large"""

    pass


class MATCHESError(Error):
    """Raised when the input value is too large"""

    pass


class GETTINGMATCHError(Error):
    """Raised when the input value is too large"""

    pass

class Viego:

    """
    this class creates a viego object which can interact with the riot developer portal
    WEB API in order to get a lot of matches for knowing what meta items, champions or builds
    are currently in use. to archieve this, first you need to collect alot of players (plat+)
    with LEAGUE-EXP-V4 after that we need to extract every "summonerName" and make a request
    on SUMMONER-V4 with summonerName and extract "puuid" which then we will use it to get
    the last matches on a period of max 1 week that the player played in with MATCH-V5 by puiid
    that will give us "matchId" with that now we'll use MATCH-V5 to get items and champion played
    also we can use timeline to view what items were purchased first
    """

    x = 0
    TIER_MAPPING = {
        "GOLD": ["CHALLENGER", "GRANDMASTER", "MASTER","DIAMOND", "PLATINUM", "GOLD"],
        "PLATINUM": ["CHALLENGER", "GRANDMASTER", "MASTER", "DIAMOND", "PLATINUM"],
        "DIAMOND": ["CHALLENGER", "GRANDMASTER", "MASTER", "DIAMOND"],
        "MASTER": ["CHALLENGER", "GRANDMASTER", "MASTER"],
        "GRANDMASTER" : ["CHALLENGER", "GRANDMASTER"],
        "CHALLENGER": ["CHALLENGER"]
    }

    CONTINENTS_MAPPING = {
        "br1": "americas",
        "eun1": "europe",
        "euw1": "europe",
        "jp1": "asia",
        "kr": "asia",
        "la1": "americas",
        "la2": "americas",
        "na1": "americas",
        "oc1": "sea",
        "ru": "europe",
    }
    DATA_ESTRUCTURE = {
        "championId": [0],
        "championName": [0],
        "item0": [0],
        "item1": [0],
        "item2": [0],
        "item3": [0],
        "item4": [0],
        "item5": [0],
        "spell1": [0],
        "spell2": [0],
        "perk0": [0],
        "perk1": [0],
        "perk2": [0],
        "perk3": [0],
        "perk4": [0],
        "perk5": [0],
        "role": [0],
        "lane": [0],
        "win": [0],
        "tier": [0],
        "division": [0],
    }
    DIVISION_MAPPING = {
        "IV": ["IV", "III", "II", "I"],
        "III": ["III", "II", "I"],
        "II": ["II", "I"],
        "I": ["I"],
    }
    def __init__(self, region, division, tier, page):
        ### VARIABLES DECLARATION ###
        self.region = region  # BR1, EUN1, EUW1, JP1, KR, LA1, LA2, NA1, OC1, RU
        self.region_continent = Viego.CONTINENTS_MAPPING[region]
        self.tier_list = Viego.TIER_MAPPING[tier]
        self.page_list = [x for x in range(page, 10000)]
        self.division_list = Viego.DIVISION_MAPPING[division]
        self.requests = 0
        ### files initialization ###
        self.folder_name = self.region + "_data"
        self.csv_name = self.region + "_data.csv"
        self.recovery_name = self.region + "_recovery.txt"

        if not os.path.isdir(self.folder_name):
            os.mkdir(self.folder_name)

        if not os.path.isfile(self.folder_name + "/" + self.recovery_name):
            with open(self.folder_name + "/" + self.recovery_name, "w+") as f:
                f.write("first")
        else:
            self.recovery_name = self.folder_name + "/" + self.recovery_name

        if not os.path.isfile(self.folder_name + "/" + self.csv_name):
            self.csv_name = self.folder_name + "/" + self.csv_name
            self.lol_data = pd.DataFrame(Viego.DATA_ESTRUCTURE, index=["championId"])
            self.lol_data.to_csv(self.csv_name, index=False)
        else:
            self.csv_name = self.folder_name + "/" + self.csv_name
            self.lol_data = pd.read_csv(self.csv_name)
        ### API KEY RETRIVMENT ###
        with open("./api_key.txt") as f:  # api key needs to be secret!!!
            contents = f.readline()
            self.api_key = contents
        
        print(self.api_key)

    def get_data(self):
        for division in self.division_list:
            for tier in self.tier_list:
                print(division)
                if tier == 'CHALLENGER' and division != 'I':
                    print('proceding because higher ranks dont have tiers')
                    break
                for page in self.page_list:
                    
                    
                    # print(tier)
                    # print(division)
                    # print(page)
                    players_entries = self.league_exp_v4('RANKED_SOLO_5x5',tier, division, page)
                    if type(players_entries) is type(None):
                        print('retrying in 1s')
                        time.sleep(1)
                        players_entries = self.league_exp_v4('RANKED_SOLO_5x5', tier, division, page)
                        if type(players_entries) is not type(None):
                            pass
                        else:
                            print('breaking')
                            continue

                    
                    self.requests  +=1
                    for player in players_entries:
                        summoner_id = player["summonerId"]
                    
                        puuid = self.summoner_v4_by_summoner(summoner_id)
                        if type(puuid) is type(None):
                            print('retrying in 1s')
                            time.sleep(1)
                            puuid = self.summoner_v4_by_summoner(summoner_id)
                            if type(puuid) is not type(None):
                                pass
                            else:
                                print('breaking')
                                continue
                        time.sleep(1)
                        self.requests  +=1
                        matches = self.match_v5_matches_by_puuid(puuid)

                        if type(matches) is type(None):
                            print('retrying in 1s')
                            time.sleep(1)
                            matches = self.match_v5_matches_by_puuid(puuid)
                            if type(matches) is not type(None):
                                pass
                            else:
                                print('breaking')
                                continue
                        time.sleep(1)
                        self.requests  +=1
                        # print(matches)
                        # print(puuid)
                        # print(games)

                        try:

                            for match in matches:
                                time.sleep(0.25)
                                # print(match)
                                match_info = self.match_v5_match_info_by_id(match)
                                if type(match_info) is type(None):
                                    print('retrying in 1s')
                                    time.sleep(1)
                                    match_info = self.match_v5_match_info_by_id(match)
                                    if type(match_info) is not type(None):
                                        pass
                                    else:
                                        print('breaking')
                                        continue
                                   
                                
                                self.requests  +=1
                                print(f'this is request n{self.requests}')
                                for participant in match_info["participants"]:
                                    perks = participant["perks"]
                                    styles = perks["styles"]
                                    perks = []

                                    for style in styles:
                                        selections = style["selections"]
                                        for selection in selections:
                                            perks.append(selection["perk"])

                                    try:
                                        league_data = {
                                            "championId": [participant["championId"]],
                                            "championName": [
                                                participant["championName"]
                                            ],
                                            "item0": [participant["item0"]],
                                            "item1": [participant["item1"]],
                                            "item2": [participant["item2"]],
                                            "item3": [participant["item3"]],
                                            "item4": [participant["item4"]],
                                            "item5": [participant["item5"]],
                                            "spell1": [participant["summoner1Id"]],
                                            "spell2": [participant["summoner2Id"]],
                                            "perk0": [perks[0]],
                                            "perk1": [perks[1]],
                                            "perk2": [perks[2]],
                                            "perk3": [perks[3]],
                                            "perk4": [perks[4]],
                                            "perk5": [perks[5]],
                                            "role": [participant["individualPosition"]],
                                            "lane": [participant["lane"]],
                                            "win": [participant["win"]],
                                            "tier": tier,
                                            "division": division,
                                        }
                                        aux_df = pd.DataFrame(
                                            league_data, index=["championId"]
                                        )
                                        self.lol_data = self.lol_data.append(
                                            aux_df, ignore_index=True
                                        )

                                    except Exception:
                                        print("passing because list out of index")
                                        pass
                                Viego.x += 1
                                if Viego.x == 50:
                                    self.lol_data.to_csv(self.csv_name, index=False)
                                    Viego.x = 0
                                    print("writted after 50")
                                    print(f"{tier}, {division}, {page}")
                                    pass

                        except TypeError as non_iterable:
                            print("[error] matches list was empty")
                            continue
        pass
    def league_exp_v4(self,queue, tier, division, page=1):
        """
        queue = 'RANKED_SOLO_5X5', 'RANKED_TFT', 'RANKED_FLEX_SR', 'RANKED_FLEX_TT'
        tier = 'IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER'
        division = 'I', 'II', 'III', 'IV'
        page = starts at 1

        this request returns a list of dicts with lots for players from the specified parameters
        """
        HEADERS = {'X-Riot-Token': self.api_key}
        url = f"https://{self.region}.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}"

        try:
            response = requests.get(url, headers=HEADERS)

            if len(response.json()) == 0:  # Means there was an empty response
                raise BLANKError
            
            print(f"[success] entries gotten")
            
            return response.json()

        except BLANKError:  #  response was blank, which could mean that we have reached last page
            print("[error] response was empty, likely last page")
            pass

        except HTTPError as http_err:  #  Somthing serious error like no internet, server error, bad url ec
            print(f"[error] HTTP ERROR OCCURRED(SERIOUS): {http_err}")
            pass

        except requests.exceptions.ConnectionError as e:
            return 
            pass

        except Exception as e:
            return
            pass

    def summoner_v4_by_summoner(self, summoner_id):
        """
        this returns the puiid requered to access to the matches
        repitedly looking for unexisting matches will result in a backlist
        """
        HEADERS = {'X-Riot-Token': self.api_key} 
        # url = f"https://{self.region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}"
        print(summoner_id)
        url = f'https://{self.region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}'
        try:
            response = requests.get(url, headers=HEADERS)
            
            if response.status_code == 400:  # id not found
                raise IDError
            
            print(f"[success] puuid gotten")
            
            print(response.json())
            if response.status_code == 500:
                return
            return response.json()["puuid"]

        except HTTPError as http_err:  #  some serious error like no internet, server error, bad url ec
            print(f"[error] HTTP ERROR OCCURRED(SERIOUS): {http_err}")
            pass

        except IDError:
            print("[error] id not found or other error")
            pass
        except TypeError:
            print('error with the summonerv4 get summoner by id')

        except requests.exceptions.ConnectionError as e:
            return 
            pass
        except Exception as e:
            return
            pass

    def match_v5_matches_by_puuid(self,puuid, count=40):

        start_time = int(time.time()) - 604800 * 2  # two weeks from today

        # url = f'https://{self.region_continent}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&type=ranked&endTime={end_time}&count={count}&api_key={self.api_key}'
        url = f"https://{self.region_continent}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={start_time}&endTime={int(time.time())}&queue=420&type=ranked&start=0&count={count}&api_key={self.api_key}"
        try:
            response = requests.get(url)

            if len(response.json()) == 1:
                print("[warning] did not found recent games")
                return
            if response.status_code != 200:
                raise MATCHESError
            print(f"[success] match list retrived")
            return response.json()

        except HTTPError as http_err:  #  some serious error like no internet, server error, bad url ec
            print(f"[error] HTTP ERROR OCCURRED(SERIOUS): {http_err}")
            pass

        except MATCHESError:
            print("[error] matches id ")
            pass

        except requests.exceptions.ConnectionError as e:
            return 
            pass
        except Exception as e:
            return
            pass
    
    def match_v5_match_info_by_id(self, match_id):
        url = f"https://{self.region_continent}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={self.api_key}"
        try:
            response = requests.get(url)

            if response.status_code != 200:
                raise GETTINGMATCHError

            print(f"[success] match info gotten")
            return response.json()["info"]
        except GETTINGMATCHError:
            print("[error] could not get match info")

        except HTTPError as http_err:  #  some serious error like no internet, server error, bad url ec
            print(f"[error] HTTP ERROR OCCURRED(SERIOUS): {http_err}")
            pass

        except requests.exceptions.ConnectionError as e:
            return 
            pass
        except Exception as e:
            return
            pass

    def match_v5_timeline_by_id(self, match_id):
        url = f'https://{self.region_continent}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline?api_key={self.api_key}'
        try:
            response = requests.get(url)

            if response.status_code != 200:
                raise GETTINGMATCHError

            print(f"[success] match info gotten")
            return response.json()
        except GETTINGMATCHError:
            print("[error] could not get match info")

        except HTTPError as http_err:  #  some serious error like no internet, server error, bad url ec
            print(f"[error] HTTP ERROR OCCURRED(SERIOUS): {http_err}")
            pass

        except requests.exceptions.ConnectionError as e:
            return 
            pass
        except Exception as e:
            return
            pass



if __name__ == '__main__':
    na1 = Viego('na1', "IV", "CHALLENGER", 1)
    na1.get_data()

       

    

