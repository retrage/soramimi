#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import json
import datetime

import requests
from urllib import parse
from bs4 import BeautifulSoup

BASE_URL = 'http://www7a.biglobe.ne.jp/~soramimiupdate/'

def fetch_data(link):
    url = parse.urljoin(BASE_URL, link)
    response = requests.get(url)
    assert response.ok, 'could not fetch from {}'.format(url)

    return response

def parse_response(response, encoding='shift-jis'):
    response.encoding = encoding
    return BeautifulSoup(response.text, 'html.parser')

def fetch_past_links():
    response = fetch_data('past.htm')

    soup = parse_response(response)

    links = []
    for anchor in soup.find_all('a'):
        href = anchor['href']
        if 'past' in href:
            links.append(href)

    return links

def fetch_past_data(link, encoding='shift-jis'):
    response = fetch_data(link)

    soup = parse_response(response)

    for frame in soup.find_all('frame'):
        src = frame['src']
        if 'main' in src:
            main_link = src
            break
    assert main_link, 'could not find URL to main data'

    time.sleep(1)

    response = fetch_data(main_link)

    return parse_response(response, encoding)

def parse_table(table, date):
    data = []
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) < 4:
            print('[!] {}: Skipping...'.format(date.isoformat()))
            continue
        artist = cells[0].text
        song_name = cells[1].text
        soramimi = cells[2].text
        original_words = cells[3].text
        if len(cells) < 5:
            evaluation = '賞品なし'
        else:
            evaluation = cells[4].text
        if 'アーティスト名' in artist:
            continue
        data.append({ 'date': date.isoformat(), \
                      'artist': artist, \
                      'song_name': song_name, \
                      'soramimi': soramimi, \
                      'original_words': original_words, \
                      'evaluation': evaluation })

    return data

def parse_past_data(soup):
    year = int(soup.find('h1').text[:4])
    data = []
    for title in soup.find_all('h3'):
        if not '月' in title.text or not '日' in title.text:
            continue
        t = title.text
        try:
            month = int(t[:t.index('月')])
            day = int(t[t.index('月')+1:t.index('日')])
        except:
            print('[!] Date encoding error: {}'.format(t))
        date = datetime.date(year, month, day)
        sibling = title.find_next_sibling('p')
        if sibling is not None and '放送' in sibling.text:
            print('[-] {}: No on air p'.format(date.isoformat()))
            continue
        sibling = title.find_next_sibling('div')
        if sibling is not None and '放送' in sibling.text:
            print('[-] {}: No on air div'.format(date.isoformat()))
            continue
        anchor = title.find_next('a')
        if anchor is not None and '空耳アワード' in anchor.text:
            url = anchor['href']
            print('[!] {}: Award found: {}'.format(date.isoformat(), url))
            continue
        sibling = title.find_next_sibling('h3')
        if sibling is not None and '空耳アワード' in sibling.text:
            url = sibling.find_next('a')['href']
            print('[!] {}: Award found: {}'.format(date.isoformat(), url))
            continue
        if sibling is not None and '名作' in sibling.text:
            url = sibling.find_next('a')['href']
            print('[!] {}: Epic found: {}'.format(date.isoformat(), url))
            continue
        if '雑談アワー' in title.text:
            print('[-] {}: Skipping talks...'.format(date.isoformat()))
            continue
        table = title.find_next('table')
        data += parse_table(table, date)

    return data

def main():
    if len(sys.argv) < 2:
        return -1

    print('[+] Fetching past links...')
    links = fetch_past_links()
    print('[+] Fetched and parsed past links')

    data = []
    for link in links:
        print('[+] Fetching {} ...'.format(link))
        encoding = 'shift-jis' if not '2015' in link else 'UTF-8'
        soup = fetch_past_data(link, encoding)
        data += parse_past_data(soup)
        time.sleep(1)

    with open(sys.argv[1], 'w') as fp:
        json.dump(data, fp, indent='\t')

    return 0

if __name__ == '__main__':
    sys.exit(main())
