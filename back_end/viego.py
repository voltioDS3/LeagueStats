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

