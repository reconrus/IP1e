from nltk.tokenize import word_tokenize


def compare_texts(text1, text2):
    # TODO Update method using some similarity criterion
    tl1 = text1.lower()
    tl2 = text2.lower()

    if tl1 in tl2 or tl2 in tl1:
        return True

    ts1 = word_tokenize(tl1)
    ts2 = word_tokenize(tl2)

    return all([True if token in ts2 else False for token in ts1 ]) or \
           all([True if token in ts1 else False for token in ts2 ])  
           

def peek(iterable):
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return first