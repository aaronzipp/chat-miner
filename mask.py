#!/usr/bin/env python
# from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
# import os

from wordcloud import WordCloud, STOPWORDS

def create_masked(text, name):
    mask = np.array(Image.open(r"./masks/heart.png"))

    stopwords = set(STOPWORDS)
    stopwords = STOPWORDS.update(['media', 'omitted', 'missed', 'voice', 'call', 'http', 'https'])

    wc = WordCloud(background_color = "white",
                   max_words = 400, mask = mask,
                   stopwords = stopwords,
                   contour_width = 3,
                   contour_color = 'red',
                   colormap = 'Reds',
                   max_font_size = 60,
                   min_font_size = 8,
                   min_word_length = 3,
                   random_state = 23)

    wc.generate(text)

    wc.to_file(f"./img/{name}.png")

    # show
    plt.imshow(wc, interpolation = 'bilinear')
    plt.axis("off")
    plt.figure()
    plt.imshow(mask, cmap=plt.cm.gray, interpolation='bilinear')
    plt.axis("off")
    plt.show()
