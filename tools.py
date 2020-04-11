from nltk.tokenize import word_tokenize
from fuzzywuzzy import fuzz

THRESHOLD = 0.6


def compare_texts(text1, text2):
    """
    :return: True if text1 is similar to text2, False otherwise
    """
    tl1 = text1.lower()
    tl2 = text2.lower()

    if tl1 in tl2 or tl2 in tl1:
        return True

    ts1 = word_tokenize(tl1)
    ts2 = word_tokenize(tl2)

    if all([True if token in ts2 else False for token in ts1 ]) or \
           all([True if token in ts1 else False for token in ts2 ]):
        return True

    if fuzz.token_sort_ratio(tl1, tl2) > THRESHOLD:
        return True
    
    return False
           

def peek(iterable):
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return first