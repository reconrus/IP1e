import argparse
import json 

import networkx as nx

import matplotlib.pyplot as plt

def create_graph(wikidata):
    graph = nx.DiGraph()

    for row in wikidata:
        graph.add_node(row['id'], label=row['enlabel'])
        edges = [(row['id'], superclass_id) for superclass_id in row['subclassof']]
        graph.add_edges_from(edges) 

    return graph

def get_path(most_specific_id):
    label = graph.nodes[most_specific_id].get('label', 'UNK')
    yield (most_specific_id, label)
    
    cur_id = most_specific_id
    while len(graph.succ[cur_id]):
        superclass = list(graph.succ[cur_id].keys())[0]
        label = graph.nodes[superclass].get('label', 'UNK')
        yield (superclass, label)
        cur_id = superclass 

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-wd", help = "path to shorten wikidata json file", dest = "wd_input")
    parser.add_argument("-o", help = "path to output file", dest = "output")
    parser.add_argument("-g", help = "path to output file for graph", dest = "graph_output")
    parser.add_argument("-c", help = "encoding standard", dest = "encoding", default="utf-8")
    args = parser.parse_args()

    wikidata_file = open(args.wd_input, 'r', encoding=args.encoding)
    wikidata = json.load(wikidata_file)

    graph = create_graph(wikidata)

    # from the most specific classes to the top class (one path out of all possible)
    paths = [list(get_path(_id)) for _id, subclasses in graph.pred.items() if len(subclasses) == 0]

    with open(args.output, 'w', encoding=args.encoding) as f:
        f.writelines(['%s\n' % str(path) for path in paths])

    if args.graph_output:
        nx.write_graphml(graph, args.graph_output, encoding=args.encoding)
        
    wikidata_file.close()