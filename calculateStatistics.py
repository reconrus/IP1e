import argparse
from ast import literal_eval

import pandas as pd

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help = "path to tsv file", dest = "input")
    parser.add_argument("-o", help = "path to output file", dest = "output")
    parser.add_argument("-c", help = "encoding standard", dest = "encoding", default="utf-8")
    parser.add_argument("-d", help = "delimiter for tsv", dest = "delimiter", default="\t")
    args = parser.parse_args()

    input_file = open(args.input, 'r', encoding=args.encoding)
    df = pd.read_csv(input_file, sep=args.delimiter, usecols=['subclassof', 'defining words'], converters={'subclassof': literal_eval, 'defining words': literal_eval})
    df = df.explode('subclassof').explode('defining words')
    df = df.rename(columns={"subclassof": "class", "defining words": "defining word"})
    df = df.groupby(by=['class', 'defining word']).size().reset_index(name='counts')
    
    df.to_csv(args.output, sep=args.delimiter, header=True, index=False, encoding=args.encoding)