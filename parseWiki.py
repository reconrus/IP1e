import argparse
import codecs
import csv
import os
import re
import xml.etree.ElementTree as etree

import en
import WikiExtractor
from definingPhrasesNWords import get_definitions

parser = argparse.ArgumentParser()
parser.add_argument("-i", help = "path to WikiDump file", dest = "input")
parser.add_argument("-o", help = "path to output TSV file", dest = "output")
parser.add_argument("-c", help = "encoding standard", dest = "encoding", default="utf-8")
args = parser.parse_args()

input_file = codecs.open(args.input, 'r', args.encoding)
output_file = codecs.open(args.output,'w', args.encoding)

tsv_writer = csv.writer(output_file, delimiter='\t')
tsv_writer.writerow(['title', 'timestamp', 'first sentence', 'defining phrases', 'defining words'])

def strip_tag_name(t):
    idx = t.rfind("}")
    if idx != -1:
        t = t[idx + 1:]
    return t

def delete_comments(text):
    return re.sub(re.compile(r"<!--[\S\s]*?-->"), "", text)

def clean(text):
    text = text.strip().replace('&quot;', '')
    return text.replace('&quot', '')

total_processed = 0
clear = True # Whether to clear elem. If in page, False
skip_section = False # skip if disambiguation or redirect 

for event, elem in etree.iterparse(input_file, events=('start', 'end')):
    tname = strip_tag_name(elem.tag)
    if event == 'start' and not skip_section:
        if tname == 'page':
            clear = False
        elif tname == 'title':
            title_el = elem
        elif tname == 'timestamp':
            ts_el = elem
        elif tname == 'text':
            text_el = elem
        elif tname == 'redirect':
            skip_section = True
    elif tname == 'page':
        total_processed += 1
        if not skip_section:
            text = delete_comments(text_el.text)
            result =  en.getData(text, title_el.text)
            if not result[0]: # if type of article is empty (not disambiguation or redirect)  
                first_sentence = clean(result[1])
                phrases, words = get_definitions(title_el.text, first_sentence)
                tsv_writer.writerow([title_el.text, ts_el.text, first_sentence, phrases, words])
        if total_processed > 1 and (total_processed % 10) == 0:
            print("\r{:,}".format(total_processed), end='')  

        skip_section = False       
        clear = True

    if clear:
        elem.clear()

input_file.close()
output_file.close()