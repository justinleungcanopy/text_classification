import pandas as pd
import numpy as np
import re


def ubs_solver(file_path):
    pass

def ubs_text_classifier(narration,amount,ac_number):

with open("./Data Files/EN_US.txt") as word_file:
    english_words = set(word.strip().lower() for word in word_file)
def is_word(word):
    return word.lower() in english_words