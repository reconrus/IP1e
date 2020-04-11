from nltk.tokenize import word_tokenize
from fuzzywuzzy import fuzz, process

THRESHOLD = 0.6

def compare_texts(text1, text2, levenstein_threshold=THRESHOLD):
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

    if fuzz.token_sort_ratio(tl1, tl2) > levenstein_threshold:
        return True
    
    return False
           

def peek(iterable):
    return next(iterable, None)


def get_similar_substring_slice(string2match, doc):
    """
    :param string2match: string for which the most similar substring is sought
    :param doc: spaCy Doc object where the search is going on
    """ 
    n = len(word_tokenize(string2match)) + 3 # how many tokens may be in the substring 
    substring_slices = [doc[start:start + i] for i in range(1, n) for start in range(1, len(doc)-i)]
    substrings = [substring_doc.text for substring_doc in substring_slices]
    most_similar = process.extractOne(string2match, substrings, score_cutoff=THRESHOLD)
    if not most_similar:
        return None
        
    return peek((slice_ for slice_ in substring_slices if slice_.text == most_similar[0]))
