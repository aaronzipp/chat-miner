#!/usr/bin/env python
# from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
# import os

from wordcloud import WordCloud, STOPWORDS

def create_masked(text, name, *,  background_color = "white",
                   max_words = 400,
                   contour_width = 3,
                   contour_color = 'red',
                   colormap = 'Reds',
                   max_font_size = 60,
                   min_font_size = 8,
                   min_word_length = 3,
                   random_state = 23):

    mask = np.array(Image.open(r"./masks/heart.png"))

    stopwords = set(STOPWORDS)
    stopwords = STOPWORDS.update(['media', 'omitted', 'missed', 'voice', 'call', 'http', 'https'])

    wc = WordCloud(mask = mask,
                   stopwords = stopwords,
                   background_color = background_color,
                   max_words = max_words,
                   contour_width = contour_width,
                   contour_color = contour_color,
                   colormap = colormap,
                   max_font_size = max_font_size,
                   min_font_size = min_font_size,
                   min_word_length = min_word_length,
                   random_state = random_state)

    wc.generate(text)

    wc.to_file(f"./img/{name}.png")

    # show
    plt.imshow(wc, interpolation = 'bilinear')
    plt.axis("off")
    plt.figure()
    plt.imshow(mask, cmap=plt.cm.gray, interpolation='bilinear')
    plt.axis("off")
    plt.show()
