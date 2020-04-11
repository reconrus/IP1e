import argparse
import datetime
import glob
import json
import multiprocessing as mp
import os
import shutil
import time

from hurry.filesize import size
from tqdm import tqdm

from Chunker import Chunker

def key_error_handle(entity, exception, log_folder):
    with open(os.path.join(log_folder, 'key_errors.txt'), 'a+') as f:
        f.write(str(exception))
        f.write("\n{}\n\n".format(entity))


def process_line(json_line, log_folder):
    # Do not consider first '[' and last ']'
    if json_line[0]!='{':
        return '' 
    if json_line[-2:] == ',\n':
        json_line = json_line[:-2]
    elif json_line[-1:] == ',':
        json_line = json_line[:-1]

    entity = json.loads(json_line)
    shortened_entity = {
        'id': entity['id'],
        'instanceof': [],
        'subclassof': []
        }

    try:
        shortened_entity['title'] = entity['sitelinks']['enwiki']['title']
    except KeyError:
        shortened_entity['title'] = None

    if 'P31' in entity['claims']:
        for instance in entity['claims']['P31']:
            try: 
                shortened_entity['instanceof'].append(instance['mainsnak']['datavalue']['value']['id'])
            except KeyError as e:
                key_error_handle(entity, e, log_folder)
            
    if 'P279' in entity['claims']:
        for subclass in entity['claims']['P279']:
            try:
                shortened_entity['subclassof'].append(subclass['mainsnak']['datavalue']['value']['id'])
            except KeyError as e:
                key_error_handle(entity, e, log_folder)

    return '%s,\n' % json.dumps(shortened_entity)


def process_chunk(chunk, input_file, output_folder, jobID, encoding):
    processed_lines = []
    for line in Chunker.parse(Chunker.read(input_file, chunk)):
        processed_line = process_line(line, output_folder)
        processed_lines.append(processed_line)

    file_path = os.path.join(output_folder, 'processed_wikidata_%d' % mp.current_process().pid)
    
    with open(file_path, 'a+', encoding=encoding) as f:
        f.writelines(processed_lines)

    print("Processed chunk #%d" % (jobID+1))
    

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help = "path to WikiData json file", dest = "input")
    parser.add_argument("-o", help = "path to output folder", dest = "output")
    parser.add_argument("-c", help = "encoding standard", dest = "encoding", default="utf-8")
    parser.add_argument("-s", help= "chunk size", dest="chunk_size", default=1024*1024*1024)
    args = parser.parse_args()
    args.chunk_size = int(args.chunk_size)

    if not os.path.exists(args.output):
        os.mkdir(args.output)

    logs_file = open(os.path.join(args.output, "logs.txt"), 'a+')

    pool = mp.Pool(mp.cpu_count())
    jobs = []
    start_time = time.time()
    print("Chunks of size %s" % size(args.chunk_size), file=logs_file)
    for jobID,chunk in enumerate(Chunker.chunkify(args.input, size=args.chunk_size)):
        job = pool.apply_async(process_chunk,(chunk,args.input,args.output, jobID, args.encoding))
        jobs.append(job)

    output = []
    for job in jobs:
        job.get()

    pool.close()

    print("Total # of chunks: %d" % (jobID+1), file=logs_file)
    print("Total time: {}".format(datetime.timedelta(seconds=time.time() - start_time)), file=logs_file)
    logs_file.close()

    filenames_pattern = os.path.join(args.output, "processed_*")
    outfilename = os.path.join(args.output, "processed_wikidata_all.json")
    with open(outfilename, 'w+', encoding=args.encoding) as outfile:
        outfile.write('[\n')
        for filename in tqdm(glob.glob(filenames_pattern), desc="Merge files to one"):
            if filename == outfilename:
                continue
            with open(filename, 'r', encoding=args.encoding) as readfile:
                shutil.copyfileobj(readfile, outfile)
        outfile.write(']')