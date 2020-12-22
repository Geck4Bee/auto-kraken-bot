import sys
sys.path.append('lib')

import json
import datetime

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib3
import os


def handler(event, context):
    data = {
        'output': 'Hello World',
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    return {'statusCode': 200,
            'body': json.dumps(data),
            'headers': {'Content-Type': 'application/json'}}
