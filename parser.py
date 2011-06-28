#!/usr/bin/env python
from imposm.parser import OSMParser
from pyosm import OSMXMLFile, Node, Way

border_ways = {}
border_nodes = {}

node_ids = set()

def parse_ways(ways):
    for way in ways:
        if 'border_type' in way[1] and way[1]['border_type'] == 'nation':
            border_ways[way[0]] = Way({
                'id': way[0],
                'version': 1,
                'visible': 'true',
                'changeset': 1,
            }, nodes=map(str, way[2]))
            node_ids.update(way[2])

def parse_coords(nodes):
    for node in nodes:
        if node[0] in node_ids:
            border_nodes[node[0]] = Node({
                'id': node[0],
                'version': 1,
                'changeset': 1,
                'visible': 'true',
                'user': 'sasha',
                'lat': '%.15f' % node[1],
                'lon': '%.15f' % node[2]
            })


def write(filename):
    osm_file = OSMXMLFile()
    osm_file.ways = border_ways
    osm_file.nodes = border_nodes
    osm_file.write(filename)

def main():
    import argparse
    arg_parser = argparse.ArgumentParser(description="""Simplify a pbf file by
    reducing the number of ways in the map.""")
    arg_parser.add_argument('--src', dest='src', action='store', required=True,
                   help='Source file. Supports .pbf, .osm and .osm.bz2.')
    arg_parser.add_argument('--dst', dest='dst', action='store', required=True,
                       help='Output .osm file.')
    args = arg_parser.parse_args()
    #Parse ways to extract border_nodes. Then get meta_data from border_nodes
    OSMParser(concurrency=8, ways_callback=parse_ways).parse(args.src)
    OSMParser(concurrency=8, coords_callback=parse_coords).parse(args.src)
    write(args.dst)

if __name__ == '__main__': main()
