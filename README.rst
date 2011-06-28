PBF/OSM to osm filter
==========================

This is a script that filters the boundaries of world countries using the planet.pbf.

Dependencies
---------------

    https://github.com/werner2101/python-osm - Generates osm files
    https://bitbucket.org/sasha/imposm.parser - Reads PBF/OSM files

Installation and usage
---------------------------

    pip install -r requirements.txt
    python parser.py --src file.pbf --dst out.osm

The above will generate an .osm file containing the ways and nodes of countries 
boundaries.
