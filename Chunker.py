# source: https://www.blopig.com/blog/2016/08/processing-large-files-using-python-part-duex/
"""
This class optimizes reads of large files. 
"""
import os.path

class Chunker(object):

    #Iterator that yields start and end locations of a file chunk of default size 100MB.
    #Always yields chunk locations where the end corresponds to the end of line
    @classmethod
    def chunkify(cls,fname,encoding='utf-8',size=100*1024*1024):
        fileEnd = os.path.getsize(fname)
        with open(fname,'r', encoding='utf-8') as f:
            chunkEnd = f.tell()
            while True:
                chunkStart = chunkEnd
                f.seek(f.tell() + size, os.SEEK_SET)
                cls._EOC(f)
                chunkEnd = f.tell()
                yield chunkStart, chunkEnd - chunkStart
                if chunkEnd >= fileEnd:
                    break

    #Move file pointer to end of chunk
    @staticmethod
    def _EOC(f):
        f.readline()

    #read chunk
    @staticmethod
    def read(fname,chunk,encoding='utf-8'):
        with open(fname,'r',encoding='utf-8') as f:
            f.seek(f.tell() + chunk[0])
            return f.read(chunk[1])

    #iterator that splits a chunk into units
    @staticmethod
    def parse(chunk):
        for line in chunk.splitlines():
            yield line