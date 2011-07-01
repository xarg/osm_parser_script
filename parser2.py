#!/usr/bin/env python
import os
from lxml import etree
from multiprocessing import Process, Queue
import simplejson as json
import cPickle
import math

###############
#             #
#   Workers   #
#             #
###############

def parse_nodes(src, q):
    nodes = {}
    with open(src, 'rb') as sourcefile:
        for action, elem in etree.iterparse(sourcefile, tag="node"):
            nodes[int(elem.get('id'))] = (float(elem.get('lon')),
                                     float(elem.get('lat')))
    q.put(nodes)

def parse_ways(src, q):
    ways = {}
    with open(src, 'rb') as sourcefile:
        for action, elem in etree.iterparse(sourcefile, tag="way"):
            way_id = int(elem.get('id'))
            nodes = []
            for child in elem.iterchildren():
                if child.tag == 'nd':
                    nodes.append(int(child.get('ref')))
            ways[way_id] = nodes
    q.put(ways)

def parse_relations(src, q):
    relations = {}
    with open(src, 'rb') as sourcefile:
        for action, elem in etree.iterparse(sourcefile, tag="relation"):
            relation_id = int(elem.get('id'))
            relations[relation_id] = {}
            ways = []
            for child in elem.iterchildren():
                if child.tag == 'tag' and child.get('k') == 'NAME':
                    relations[relation_id]['name'] = child.get('v')
                if child.tag == 'member' and child.get('type') == 'way':
                    ways.append(int(child.get('ref')))
            relations[relation_id]['ways'] = ways
    q.put(relations)

def reducer(nodes1, nodes2):
    combined = list(set(nodes1) & set(nodes2))
    if combined:
        #if nodes1[-1] == combined[0] and nodes2[0] == combined[0]:
        #    nodes2.remove(combined[0])
        #    return nodes1 + nodes2
        #if nodes1[-1] == combined[0] and nodes2[-1] == combined[0]:
        #    nodes2.remove(combined[0])
        #    nodes2.reverse()
        #    return nodes1 + nodes2
        #if nodes1[0] == combined[0] and nodes2[-1] == combined[0]:
        #    nodes1.remove(combined[0])
        #    return nodes2 + nodes1
        #if nodes1[0] == combined[0] and nodes2[0] == combined[0]:
        #    nodes1.remove(combined[0])
        #    nodes1.reverse()
        #    return nodes2 + nodes1
        import pdb; pdb.set_trace()
    return None

def reduce_ways(lists):
    if len(lists) <= 1:
        return lists
    for i, l1 in enumerate(lists):
        if len(lists) == 1: break
        for l2 in lists[i+1:]:
            if len(lists) == 1: break
            reduced = reducer(l1, l2)
            if reduced is not None:
                if l1 in lists:
                    lists.remove(l1)
                if l2 in lists:
                    lists.remove(l2)
                lists = reduce_ways(lists + [reduced])
    return lists

def reduce_ways_dist(lists, nodes, epsilon=.5):
    if len(lists) <= 1:
        return lists
    new_lists = []
    for i, l1 in enumerate(lists):
        for l2 in lists[i+1:]:
            if dist(nodes[l1[0]], nodes[l2[0]]) <= epsilon:
                import pdb; pdb.set_trace()
            if dist(nodes[l1[-1]], nodes[l2[-1]]) <= epsilon:
                import pdb; pdb.set_trace()
            if dist(nodes[l1[0]], nodes[l2[-1]]) <= epsilon:
                import pdb; pdb.set_trace()
            if dist(nodes[l1[-1]], nodes[l2[0]]) <= epsilon:
                import pdb; pdb.set_trace()

    return lists

def dist(a, b):
    """Euclidian distance between 2 coordinates"""
    return math.sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2))

def generate_geojson(nodes, ways, relations):
    data = {
        "type": "FeatureCollection",
        "features": []
    }
    for rel_id, relation in relations.iteritems():
        coords = []
        counter = 0
        for way in reduce_ways([ways[way] for way in relation['ways']]):
            coords.append([nodes[node] for node in way])
            counter += len(way)

            #if len(coords) > 1: # See if we can reduce by coordinates as well

        #if relation['name'] == 'Portugal':
        #    import pdb; pdb.set_trace()
        data['features'].append({
            'type': "Feature",
            'geometry': {
                'type': 'Polygon',
                "coordinates": coords
            },
            'properties': {
                'name': relation['name'],
                'count': counter
            }
        })
    return data

def main():
    import argparse
    arg_parser = argparse.ArgumentParser(description="""Simplify a osm file by
    reducibinng the number of ways in the map.""")
    arg_parser.add_argument('--src', dest='src', action='store', required=True,
                   help='Source file. Supports .osm')
    arg_parser.add_argument('--dst', dest='dst', action='store', required=True,
                       help='Output .osm file.')
    args = arg_parser.parse_args()

    temp_pickle = '/tmp/parser2.pickle'
    if os.path.exists(temp_pickle):
        nodes, ways, relations = cPickle.load(open(temp_pickle, 'rb'))
    else: #Process
        nodes_q = Queue()
        ways_q = Queue()
        relations_q = Queue()

        node_proc = Process(target=parse_nodes, args=(args.src, nodes_q, ))
        node_proc.start()

        ways_proc = Process(target=parse_ways, args=(args.src, ways_q, ))
        ways_proc.start()

        relations_proc = Process(target=parse_relations,
                            args=(args.src, relations_q, ))
        relations_proc.start()

        nodes = nodes_q.get()
        node_proc.join()

        ways = ways_q.get()
        ways_proc.join()

        relations = relations_q.get()
        relations_proc.join()

        cPickle.dump((nodes, ways, relations, ), open(temp_pickle, 'wb'))
    json.dump(generate_geojson(nodes, ways, relations), open(args.dst, 'wb'),
                indent=4)

if __name__ == '__main__':
    main()


