#!/usr/bin/env python
import simplejson as json
from lxml import etree
from copy import deepcopy

border_ways = {}
border_nodes = {}
relations_ways = {}
relations = {}
country_data_default = {
    'type': "Feature",
    'geometry': {
        'type': 'Polygon',
        "coordinates": []
    },
    'properties': {
        'name': '',
        'id': '',
        'count': 0
    }
}
countries_data = []

def generate_nodes(filename):
    for action, elem in etree.iterparse(open(filename, 'rb'), tag="node"):
        border_nodes[elem.get('id')] = (float(elem.get('lon')),
                                        float(elem.get('lat')))
def generate_relations(filename):
    for action, elem in etree.iterparse(open(filename, 'rb'), tag="relation"):
        ways = []
        relation_id = elem.get('id')
        country_name = ''
        for child in elem.getchildren():
            if child.tag == 'tag' and child.get('k') == 'NAME':
                country_name = child.get('v')
            if child.tag == 'member' and child.get('type') == 'way':
                ways.append(child.get('ref'))
        if country_name == '':
            country_name = relation_id

        if country_name not in relations:
            relations[country_name] = []
            country_data = deepcopy(country_data_default)
            country_data['properties']['name'] = country_name
            country_data['properties']['id'] = relation_id

        if relation_id not in relations_ways:
            relations_ways[relation_id] = []

        countries_data.append(country_data)
        relations_ways[relation_id].extend(ways)

def generate_ways(filename):
    for action, elem in etree.iterparse(open(filename, 'rb'), tag="way"):
        way_id = elem.get('id')
        nodes = []
        for child in elem.iterchildren():
            if child.tag == 'nd' and child.get('ref') in border_nodes:
                nodes.append(border_nodes[child.get('ref')])

        for relation_id, way_ids in relations_ways.items():
            if way_id in way_ids:
                for country in countries_data:
                    if country['properties']['id'] == relation_id:
                        country['geometry']['coordinates'].append(nodes)
                        country['properties']['count'] += len(nodes)

def write(filename):
    json.dump({"type": "FeatureCollection", "features": countries_data},
                open(filename, 'wb'))

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
    generate_nodes(args.src)
    generate_relations(args.src)
    generate_ways(args.src)

    write(args.dst)

if __name__ == '__main__': main()
