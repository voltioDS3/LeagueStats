import json
import os
import time
from argparse import RawDescriptionHelpFormatter
from email.policy import HTTP
from msilib.schema import Error
from time import process_time_ns
from types import NoneType
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
    def __init__(self, region):
        ### VARIABLES DECLARATION ###
        self.region = region
        ### API KEY RETRIVMENT ###
        with open("./api_key.txt") as f:  # api key needs to be secret!!!
            contents = f.readline()
            self.api_key = contents
        pass

    def league_exp_v4(self,queue, tier, division, page=1):
        """
        queue = 'RANKED_SOLO_5X5', 'RANKED_TFT', 'RANKED_FLEX_SR', 'RANKED_FLEX_TT'
        tier = 'IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER'
        division = 'I', 'II', 'III', 'IV'
        page = starts at 1

        this request returns a list of dicts with lots for players from the specified parameters
        """
        url = f"https://la2.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}&api_key={self.api_key}"

        try:
            response = requests.get(url)

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

    def summoner_v4_by_name(self, summoner_id):
        """
        this returns the puiid requered to access to the matches
        repitedly looking for unexisting matches will result in a backlist
        """
        url = f"https://{self.region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={self.api_key}"

        try:
            response = requests.get(url)
            
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

    def match_v5_match_by_puuid(self,puuid, count=40)
    
       

    

