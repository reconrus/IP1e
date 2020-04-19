import argparse
import csv

import pandas as pd

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-wd", help = "path to shorten wikidata json file", dest = "wd_input")
    parser.add_argument("-tsv", help = "path to tsv file with defining phrases", dest = "tsv_input")
    parser.add_argument("-o", help = "path to output folder", dest = "output")
    parser.add_argument("-c", help = "encoding standard", dest = "encoding", default="utf-8")
    parser.add_argument("-d", help = "delimiter for tsv", dest = "delimiter", default="\t")
    args = parser.parse_args()

    wikidata_file = open(args.wd_input, 'r', encoding=args.encoding)
    tsv_input_file = open(args.tsv_input, 'r', encoding=args.encoding)

    wikidata = pd.read_json(wikidata_file, orient='records', encoding=args.encoding)
    inptsv = pd.read_csv(tsv_input_file, sep=args.delimiter)

    wikidata_new = wikidata.set_index('id')
    mapping = wikidata_new['enlabel']
    
    get_titles = lambda x: [(i, mapping[i]) if i in mapping.index else "UNKNOWN_ENTITY: %s" % i for i in x]

    wikidata['instanceoftitle'] = wikidata['instanceof'].apply(get_titles)
    wikidata['subclassoftitle'] = wikidata['subclassof'].apply(get_titles)

    wd2merge = wikidata[['title', 'instanceoftitle', 'subclassoftitle']]
    wd2merge = wd2merge.rename(columns={"instanceoftitle": "instanceof", "subclassoftitle": "subclassof"})

    outtsv = pd.merge(inptsv, wd2merge, on='title')
    outtsv.to_csv(args.output, sep=args.delimiter, header=True, index=False, encoding=args.encoding)

    wikidata_file.close()
    tsv_input_file.close()