from selectorlib import Extractor
import requests 
import json 
from time import sleep
import csv
from dateutil.parser import parse
import sys
import re
from analysis import getrate, recordlinks
import pandas as pd


# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('selectors.yml')
def scrape(url):    
    headers = {
        'authority': 'www.amazon.in',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US,en-IN;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    #print("Downloading %s"%url)
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 400:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create
    #print(e.extract(r.text))
    return e.extract(r.text)

def finding_data(data, writer, url):
    if data:
        #print(data)
        for r in data['reviews']:
            #print(r)
            r["product"] = data["product_title"]
            r['url'] = url
            if 'verified' in r:
                if r['verified'] == None or 'Verified Purchase' in r['verified']:
                    r['verified'] = 'Yes'
                else:
                    r['verified'] = 'Yes'
            try:
                r['rating'] = r['rating'].split(' out of')[0]
            except:
                r['rating'] = "None"
            date_posted = r['date'].split('on ')[-1]
            if r['images']:
                r['images'] = "\n".join(r['images'])
            r['date'] = parse(date_posted).strftime('%d/%m/%Y')
            try:
                writer.writerow(r)
            except:
                pass
    

# product_data = []
with open("urls.txt",'r') as urllist, open('data.csv','w', encoding="utf-8", errors="ignore", newline="") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=["title","content","date","variant","images","verified","author","rating","product","url"])
    writer.writeheader()
    data_list = pd.read_csv('datalist.csv')
    
    #print(data_list["product"])
    for url in urllist.readlines():
        urlorg = url
        data = scrape(url)
        name = data["product_title"]
        #print(data_list['product'])
        #print(name)
        if name in data_list.values:
            print("Data Already saved!")
        else:
            
            while data["product_title"] == None:
                data = scrape(url)
                
            while data["next_page"] != None:
                finding_data(data, writer, url)
                url = "https://www.amazon.in" + data["next_page"]
                data = scrape(url)
                while data["product_title"] == None:
                    data = scrape(url)  
            else:
                finding_data(data, writer, url)
            df_len, deltaT, rate = getrate()
            #recordlinks(name, df_len, deltaT, rate, urlorg)
        
        

