#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json

import nagisa
import matplotlib.pyplot as plt
from wordcloud import WordCloud

FONT_PATH = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

def normalize(words):
    words = words.replace('\n', ' ')
    words = words.replace('\t', ' ')
    words = words.replace('（☆）', ' ')
    return words.strip()

def main():
    if len(sys.argv) < 2:
        return -1

    with open(sys.argv[1], 'r') as fp:
        data = json.load(fp)

    words_list = []
    for work in data:
        text = normalize(work['soramimi'])
        words = nagisa.extract(text, \
                extract_postags=['名詞', '動詞', '形容詞' ,'副詞'])
        words_list += words.words

    stop_words = ['ある', 'ない', '無い', 'する', 'いい', 'もう', 'どう', '中略']
    texts = ' '.join(words_list)
    wordcloud = WordCloud(font_path=FONT_PATH, stopwords=set(stop_words), width=900, height=500).generate(texts)

    plt.figure(figsize=(15, 12))
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
