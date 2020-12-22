import sys
sys.path.append('lib')

import json
import datetime

import requests
from bs4 import BeautifulSoup


def handler(event, context):
    try:
        # スクレイピング対象の URL にリクエストを送り HTML を取得する
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0",}
        res = requests.get('https://kraken-wood.com/', headers=headers)
        
        objs = []
        try:
            soup = BeautifulSoup(res.content, "html.parser")
            for aa in soup.find_all("a"):
                link = aa.get("href")
                name = aa.get_text()
                objs.append({
                    'link': link,
                    'name': name
                })
        except Exception as ee:
            sys.stderr.write("*** error *** in BeautifulSoup ***\n")
            sys.stderr.write(str(ee) + "\n")
    except Exception as ee:
        sys.stderr.write("*** error *** in requests.get ***\n")
        sys.stderr.write(str(ee) + "\n")
    
    data = {
        'output': 'Hello World',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'objs': json.dumps(objs)
    }

    return {'statusCode': 200,
            'body': json.dumps(data),
            'headers': {'Content-Type': 'application/json'}}
