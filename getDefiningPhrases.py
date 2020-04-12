import argparse
import codecs
import csv
import os
import re
from tqdm import tqdm

from definingPhrasesNWords import get_definitions


def get_title_from_link(link, lang):
    link_pattern = re.compile("https?://%s.wikipedia.org/wiki/" % lang)
    title = re.sub(link_pattern, "", link)
    title = title.replace("_", " ")
    return title

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help = "path to file with FirstSentences generated by wikipedia2tsv scripts", dest = "input")
    parser.add_argument("-o", help = "path to output TSV file", dest = "output")
    parser.add_argument("-c", help = "encoding standard", dest = "encoding", default="utf-8")
    parser.add_argument("-l", help = "language of the dump", dest = "lang", default="en")
    parser.add_argument("-d", help = "delimiter for tsv", dest = "delimiter", default="\t")
    
    args = parser.parse_args()

    input_file = codecs.open(args.input, 'r', args.encoding)
    output_file = codecs.open(args.output,'w', args.encoding)

    reader = csv.reader(input_file, delimiter=args.delimiter)
    writer = csv.writer(output_file, delimiter=args.delimiter)
    writer.writerow(['title', 'first sentence', 'defining phrases', 'defining words'])

    total_processed = 0

    for line in reader:
        title = get_title_from_link(line[0], args.lang)
        phrases, words = get_definitions(title, line[1])
        writer.writerow([title, line[1], phrases, words])

    input_file.close()
    output_file.close()

if __name__=='__main__':
    main()