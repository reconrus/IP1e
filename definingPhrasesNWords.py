from typing import List, Tuple

import spacy 
from spacy.symbols import conj, nsubj, NOUN, AUX

nlp = spacy.load("en_core_web_sm")

def_words_file = open("def_words.txt", 'w', encoding='utf-8')
def_phrases_file = open("def_phrases.txt", 'w', encoding='utf-8')
def_file = open("def_file.txt", 'w', encoding='utf-8')


def head_aux(subject_chunk, chunk):
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


def root_noun_conj(current_chunk, def_chunks):
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


def subject_chunk_by_title(title, chunk):
    """
    Compares current chunk text and an article title
    # TODO Update method using some similarity criterion
    :return: chunk if subject_chunk, None otherwise
    """
    if title.lower() in chunk.text.lower() or \
            chunk.text.lower() in title.lower():
       
        return chunk

    return None


def get_definitions(title, text):
    """
    :param subject: Title of a Wikipedia article
    :param text: First sentence of a Wikipedia article
    :return: Tuple with lists of definition phrases and words respectively
    """
    doc = nlp(text)
    # subject_doc = nlp(subject) # to get nsubj
    
    subject_chunk = None
    def_chunks = []
    def_phrases = []
    def_words = []

    # Assumes that subject chunk is the first
    for chunk in doc.noun_chunks:
        processed_chunk = None

        if not subject_chunk:
            subject_chunk = subject_chunk_by_title(title, chunk)

        result = head_aux(subject_chunk, chunk)
        if result:
            subject_chunk, processed_chunk = result
        
        if not processed_chunk: 
            processed_chunk = root_noun_conj(chunk, def_chunks)

        if not processed_chunk:
            continue 

        def_phrases.append(processed_chunk.text)
        def_words.append(processed_chunk.root.text)
        def_chunks.append(processed_chunk)

    return def_phrases, def_words
