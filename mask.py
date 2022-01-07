from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS


def create_masked(text, name, *, mask_path=r"./masks/heart.png",
                  background_color=None,
                  mode="RGBA",
                  width=800,
                  height=400,
                  max_words=400,
                  stopwords=STOPWORDS,
                  include_numbers=False,
                  contour_width=0,
                  contour_color='red',
                  colormap='Reds',
                  max_font_size=60,
                  min_font_size=8,
                  relative_scaling=0.5,
                  min_word_length=3,
                  random_state=23):

    mask = np.array(Image.open(mask_path))

    stopwords = STOPWORDS.update(['media', 'omitted', 'missed',
                                  'voice', 'call', 'http', 'https'])
    stopwords = STOPWORDS.update(['jed', 'ker', 'hab'])

    wc = WordCloud(mask=mask,
                   stopwords=stopwords,
                   include_numbers=include_numbers,
                   background_color=background_color,
                   mode="RGBA",
                   width=width,
                   height=height,
                   max_words=max_words,
                   contour_width=contour_width,
                   contour_color=contour_color,
                   colormap=colormap,
                   max_font_size=max_font_size,
                   min_font_size=min_font_size,
                   relative_scaling=relative_scaling,
                   min_word_length=min_word_length,
                   random_state=random_state)

    wc.generate(text)

    wc.to_file(f"./img/{name}.png")

    # show
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.figure()
    plt.imshow(mask, cmap=plt.cm.gray, interpolation='bilinear')
    plt.axis("off")
    plt.show()
