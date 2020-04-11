import re
from typing import List, Tuple

import spacy 
from spacy.symbols import appos, conj, ccomp, \
                          nsubj, \
                          AUX, NOUN 

from tools import compare_texts, get_similar_substring_slice, \
                  peek

nlp = spacy.load("en_core_web_sm")

class DefiningPhrases:

    @classmethod
    def head_aux(cls, subject_chunk, chunk):
        """
        Simplest case. E.g. 
        Argon is a chemical element with the symbol Ar and atomic number 18. 
        And spaCy determines "is" as head of both subject_chunk and current chunk
        :param chunk: current noun_chunk to process
        :param subject_chunk: chunk with an article subject (title) E.g. Argon
        :return: new subject_chunk, current chunk if definining 
        """
        if chunk.root.head.pos != AUX:
            return None

        if not subject_chunk and chunk.root.dep == nsubj:
            return chunk, None # new subject_chunk
        
        if subject_chunk and chunk.root.head == subject_chunk.root.head:
            return subject_chunk, chunk

    @classmethod
    def root_noun_conj(cls, current_chunk, def_chunks):
        """
        Check if root of a noun chunk is conjunct with some other root from defining phrases 
        E.g. "TARDIS (Time And Relative Dimension In Space) is a fictional time machine and spacecraft that appears
        in the British science fiction television series Doctor Who and its various spin-offs."
        "spacecraft" here is conjunct with "machine" 
        """
        if current_chunk.root.dep == conj and \
        any([current_chunk.root.head == chunk.root for chunk in def_chunks]):
            return current_chunk

        return None

    @classmethod
    def subject_chunk_by_title(cls, title, chunk, previous_chunks):
        """
        Compares current chunk text and an article title
        :return: chunk if subject_chunk, None otherwise
        """
        if chunk.root.dep == nsubj and compare_texts(title, chunk.text):
            return chunk

        # e.g. "Actresses (Catalan: Actrius)", "Actrius" - title, "Actresses" - nsubj. 
        # Actrius appos Catalan
        # Catalan appos Actresses
        subject_chunk = chunk if compare_texts(title, chunk.text) else None 
        while subject_chunk and subject_chunk.root.dep == appos:
            subject_chunk = peek(_chunk for _chunk in previous_chunks if subject_chunk.root.head == _chunk.root)

        return subject_chunk

    @classmethod   
    def subject_chunk_verb_ccomp(cls, subject_chunk, chunk):
        """
        Finds cases when subject chunk is connected to verb and 
        this verb is ccomp to AUX with defining phrase
        E.g. "Alain Connes (born 1 April 1947) is a French mathematician"
        spaCy connect Connes to born and born to is. 
        Find dependency visualization in explanations\images\Alain Connes.svg
        """
        # from the example above: 
        # if chunk in process is "is a French mathematician" then
        #    subject_chunk.root.head == "born"
        #    chunk.root.head == "is"
        #    subject_chunk.root.head.head == "is"
        if  subject_chunk.root.head.dep == ccomp and \
            chunk.root.head.pos == AUX and \
            subject_chunk.root.head.head == chunk.root.head:
            return chunk
        
        return None


def get_phrases_next_to_title(title, doc):
    """
    For such cases when title is not part of noun chunks and after the title goes AUX
    E.g. "!!! is an American dance-punk band that formed in Sacramento..." 
    Where "an American dance-punk band" can be easily detected as defining phrase,
    but "!!!" is not part of any noun chunk 
    """
    AUX_tokens = [token for token in doc if token.pos == AUX]
    if not AUX_tokens:
        return None
    
    first_AUX = AUX_tokens[0]
    text_before_first_AUX = [token.text for token in doc if token.i < first_AUX.i]
    text_before_first_AUX = ' '.join(text_before_first_AUX)
    if not compare_texts(title, text_before_first_AUX):
        return None

    def_chunks = []
    def_phrases = []
    def_words = []
    
    for chunk in doc.noun_chunks:
        processed_chunk = None
        if chunk.root.head == first_AUX:
            processed_chunk = chunk

        if not processed_chunk: 
            processed_chunk = DefiningPhrases.root_noun_conj(chunk, def_chunks)

        if not processed_chunk:
            continue

        def_chunks.append(processed_chunk)        
        def_phrases.append(processed_chunk.text)
        def_words.append(processed_chunk.root.text)
    
    return def_phrases, def_words


# TODO come up with name
def get_phrases_(title, doc):
    """
    For such cases when title is not part of noun chunks and 
    somewhere in the text AUX is connected to one of the title words
    E.g. "!PAUS3, or THEE PAUSE, (born in Philadelphia, Pennsylvania),
          now located in the New York City area, is an international platinum selling musician..." 

    Where "an international platinum selling musician" can be easily detected as defining phrase,
    but "!PAUS3" is not part of any noun chunk 

    This method is looks like more general version of get_phrases_next_to_title.
    But I left both of them since tests showed results, where this method does not work while 
    get_phrases_next_to_title does 
    """

    subject_slice = get_similar_substring_slice(title, doc)
    if not subject_slice:
        return None

    def_chunks = []
    def_phrases = []
    def_words = []

    AUX_token = None

    for token in subject_slice:
        if token.head.pos == AUX:
            AUX_token = token.head
            break


    for chunk in doc.noun_chunks:
        processed_chunk = None
        if chunk.root.head == AUX_token:
            processed_chunk = chunk

        if not processed_chunk: 
            processed_chunk = DefiningPhrases.root_noun_conj(chunk, def_chunks)

        if not processed_chunk:
            continue

        def_chunks.append(processed_chunk)        
        def_phrases.append(processed_chunk.text)
        def_words.append(processed_chunk.root.text)

    return def_phrases, def_words


def clean(text):
    """
    Deletes brackets and their content
    """
    text = re.sub(re.compile(r"\([\S\s]*?\)"), "", text)
    text = re.sub(re.compile(r'\s{2,}'), ' ', text)
    return text

def get_definitions(title, text):
    """
    :param subject: Title of a Wikipedia article
    :param text: First sentence of a Wikipedia article
    :return: Tuple with lists of definition phrases and words respectively
    """
    text = clean(text)
    doc = nlp(text)
    # subject_doc = nlp(subject) # to get nsubj
    
    subject_chunk = None # chunk that contain nsubj
    previous_chunks = [] # chunks that will be processed until subject_chunk is not found
    def_chunks = []
    def_phrases = []
    def_words = []

    # Assumes that subject chunk is the first
    for chunk in doc.noun_chunks:
        processed_chunk = None

        if not subject_chunk:
            subject_chunk = DefiningPhrases.subject_chunk_by_title(title, chunk, previous_chunks)
            previous_chunks.append(chunk)
            continue

        result = DefiningPhrases.head_aux(subject_chunk, chunk)
        if result:
            subject_chunk, processed_chunk = result
        
        if not processed_chunk: 
            processed_chunk = DefiningPhrases.root_noun_conj(chunk, def_chunks)

        if not processed_chunk: 
            processed_chunk = DefiningPhrases.subject_chunk_verb_ccomp(subject_chunk, chunk)

        if not processed_chunk:
            continue

        def_phrases.append(processed_chunk.text)
        def_words.append(processed_chunk.root.text)
        def_chunks.append(processed_chunk)

    if not subject_chunk:
        result = get_phrases_next_to_title(title, doc)
        if result:
            def_phrases, def_words = result

    if not def_phrases:
        result = get_phrases_(title, doc)
        if result:
            def_phrases, def_words = result

    return def_phrases, def_words
