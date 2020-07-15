# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 15:55:16 2020

@author: marko
"""

#!/usr/bin/python3
import os, json, urllib, requests, csv

def html2csv(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, features="html.parser")
    table = soup.find("table")
    headers = [th.text.strip() for th in table.select("tr th")]
    headers.insert(1,"first_name")
    headers[0] = "last_name"
    
    with open("out.csv", "w") as f:
        output_rows = []
        for table_row in table.findAll('tr'):
            columns = table_row.findAll('td')
            output_row = []
            for column in columns:
                output_row.append(column.text.strip())
            output_rows.append(",".join(output_row))
    return ",".join(headers) + "\n".join(output_rows)

headers = {
    'authority': 'fantasyoverlord.com',
    'content-length': '0',
    'accept': '*/*',
    'cache-control': 'no-cache',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'origin': 'https://fantasyoverlord.com',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'referer': 'https://fantasyoverlord.com/FPL/PlayerPointForecasts',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'en-US;q=1.0',
}


def fetch_from_overlod():

    for position in ["GLK", "DEF", "MID", "FWD"]:
        print("[INFO] Fetching data for {}".format(position))
        params = (('', ''), ('pos', position))
        response = requests.post('https://fantasyoverlord.com/FPL/FullForecast', headers=headers, params=params)
        data = json.loads(response.text)["Result"]
        print("[INFO] Parsing data for {}".format(position))
        
        location = os.path.join( position+".csv")
        with open(location, "w", encoding = 'utf-8') as f:
            f.write(html2csv(data))
        print("[INFO] Saved to \"{}\"".format(location))