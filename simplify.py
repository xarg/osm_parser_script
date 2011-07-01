import sys
import simplejson as json
from dp import simplify_points

def main(filename, output):
    data = json.load(open(filename, 'rb'))
    for polygon in data['features']:
        counter = 0
        coords = []
        for coordinates in polygon['geometry']['coordinates']:
            points = simplify_points(coordinates, .15)
            counter += len(points)
            coords.append(points)
        polygon['geometry']['coordinates'] = coords
        polygon['properties']['count'] = counter
    json.dump(data, open(output, 'wb'), indent=4)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
