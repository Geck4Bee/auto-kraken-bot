import sys
sys.path.append('lib')

import os
import json
import datetime
import boto3
from boto3.dynamodb.conditions import Key

from nanoid import generate
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
dynamoDB = boto3.resource('dynamodb', 'ap-northeast-1')
table = dynamoDB.Table(os.environ['TABLE'])

passURL = ['donate.html', 'https://www.stop2020fraud.com/', 'images/immaculate.pdf', 'terms.html']

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
            if link not in passURL:
                objs.append({
                    'URL': link,
                    'en': name,
                    'ja': '',
                })
    except Exception as ee:
        sys.stderr.write("*** error *** in BeautifulSoup ***\n")
        sys.stderr.write(str(ee) + "\n")
    else:
        return objs

def getFromDynamoDB(URL):
    try:
        result = table.query(
            IndexName='byURL',
            KeyConditionExpression = Key('URL').eq(URL),
            ScanIndexForward = False,
            Limit = 1
        )
    except Exception as eg:
        sys.stderr.write("*** error *** in GetFromDynamoDB ***\n")
        sys.stderr.write(str(eg) + "\n")
    else:
        return result

def putDynamoDB(obj):
    try:
        dateISO = datetime.datetime.utcnow().isoformat()
        table.put_item(
            Item = {
                'id': generate(),
                'URL': obj['URL'],
                'en': obj['en'],
                'ja': obj['ja'],
                'createdAt': dateISO,
                'updatedAt': dateISO
            }
        )
    except Exception as ep:
        sys.stderr.write("*** error *** in PutDynamoDB ***\n")
        sys.stderr.write(str(ep) + "\n")
    else:
        return True

def translation(obj):
    try:
        result = translate.translate_text(
            Text=obj['en'], 
            SourceLanguageCode="en",
            TargetLanguageCode="ja"
        )
        obj['ja'] = result.get('TranslatedText')
    except Exception as et:
        sys.stderr.write("*** error *** in Translation ***\n")
        sys.stderr.write(str(et) + "\n")
    else:
        return obj

def sendWebHook(objs):
    content = '●新着クラーケン\n\n'
    for obj in objs:
        content += obj['en'] + '\n' + obj['ja'] + '\n' + obj['URL'] + '\n\n'
    try:
        response = requests.post(
            os.environ['WEBHOOK'],
            {"content": content}
        )
    except Exception as ew:
        sys.stderr.write("*** error *** in SendWebHook ***\n")
        sys.stderr.write(str(ew) + "\n")
    else:
        return response

def handler(event, context):
    objs = webscrape()
    translated_objs = []
    try:
        for obj in objs:
            getFromDB = getFromDynamoDB(obj['URL'])
            if len(getFromDB['Items']) == 0:
                translated = translation(obj)
                translated_objs.append(translated)
                putting = putDynamoDB(obj)
                if (len(translated_objs) > 0):
                    webhook = sendWebHook(translated_objs)
    except Exception as eh:
        sys.stderr.write("*** error *** in PutDynamoDB ***\n")
        sys.stderr.write(str(eh) + "\n")

    data = {
        'output': 'Hello World',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'objs': json.dumps(translated_objs)
    }

    return {'statusCode': 200,
            'body': json.dumps(data),
            'headers': {'Content-Type': 'application/json'}}
