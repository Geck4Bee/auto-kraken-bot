import sys
sys.path.append('lib')

import json
import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

def webscrape():
    # webdriver settings
    try:
        options = webdriver.ChromeOptions()
        options.binary_location = "./bin/headless-chromium"
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--single-process")
    
        driver = webdriver.Chrome(
            executable_path="./bin/chromedriver",
            chrome_options=options
        )
    
        # web scraping
        driver.get("https://kraken-wood.com/")
        #ここの時間が長いとlambdaの料金が無駄にかかります。driverがページの表示にかかる時間分だけを設定するのが良いです。
        time.sleep(1)
        html = driver.page_source.encode('utf-8')
    except Exception as ee:
        sys.stderr.write("*** error *** in webdriver ***\n")
        sys.stderr.write(str(ee) + "\n")
    else:
        return shaping_data(html)
    
def shaping_data(html):
    objs = []
    try:
        soup = BeautifulSoup(html, "html.parser")
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
    else:
        return objs

def handler(event, context):
    objs = webscrape()
    data = {
        'output': 'Hello World',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'objs': json.dumps(objs)
    }

    return {'statusCode': 200,
            'body': json.dumps(data),
            'headers': {'Content-Type': 'application/json'}}
