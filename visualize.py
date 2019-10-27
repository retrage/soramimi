#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json

import nagisa
import matplotlib.pyplot as plt
from wordcloud import WordCloud

EVAL_WEIGHT=True
FONT_PATH = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
STOP_WORDS = ['ある', 'ない', '無い', 'する', 'いい', 'もう', 'どう', '中略', 'ちょっと', 'そう', 'し', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def normalize(words):
    words = words.replace('\n', ' ')
    words = words.replace('\t', ' ')
    words = words.replace('（☆）', ' ')

    return words.strip()

def weight(evaluation):
    if not EVAL_WEIGHT:
        return 1.0
    if 'ジャンパー' in evaluation:
        return 2.5
    elif 'シャツ' in evaluation:
        return 2.0
    elif 'ミミかき' in evaluation:
        return 1.5
    elif '手ぬぐい' in evaluation:
        return 1.0
    else:
        return 1.0

def main():
    if len(sys.argv) < 2:
        return -1

    with open(sys.argv[1], 'r') as fp:
        data = json.load(fp)

    frequencies = {}
    for work in data:
        text = normalize(work['soramimi'])
        words = nagisa.extract(text, \
                extract_postags=['名詞', '動詞', '形容詞' ,'副詞'])
        evaluation = normalize(work['evaluation'])
        word_weight = weight(evaluation)
        for word in words.words:
            if word in STOP_WORDS:
                continue
            if word in frequencies:
                frequencies[word] += word_weight
            else:
                frequencies[word] = word_weight

    wordcloud = WordCloud(font_path=FONT_PATH, \
            width=900, height=500).fit_words(frequencies)

    plt.figure(figsize=(15, 12))
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()

    return 0

if __name__ == '__main__':
    sys.exit(main())
