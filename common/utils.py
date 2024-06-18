import os
from decouple import config
import requests

def generate_random_number():
    return os.urandom(8).hex().upper()