"""
Compare OSM stops to NVBW provided stops.
"""
import geojson

import sys
import spatialite
import sqlite3
import traceback

from osm_stop_matcher.StatisticsUpdater import StatisticsUpdater
from osm_stop_matcher.MatchPicker import MatchPicker
from osm_stop_matcher.NvbwStopsImporter import NvbwStopsImporter
from osm_stop_matcher.StopMatcher import StopMatcher
from osm_stop_matcher.MatchResultValidator import MatchResultValidator
from osm_stop_matcher.OsmStopsImporter import OsmStopsImporter
		
import logging

# TODO
# instead of using coded booleans for imports, derive that from params
# introduce some more deterministics choosing ambigous candidates as winning match
# label matches for which an equally rated candidate exists as ambigous
# label current ambigous match as matched_parent_stop_only
# pre/succ currently only works for (bus) platforms...
def main(osmfile, stops_file):
	logging.basicConfig(filename='matching.log', filemode='w', level=logging.INFO)
	db = spatialite.connect('stops.db')
	db.execute("PRAGMA case_sensitive_like=ON")
	db.row_factory = sqlite3.Row

	import_haltestellen = True	
	import_osm = True

	if import_haltestellen:
		NvbwStopsImporter(db).import_stops(stops_file)
		print("Imported NVBW stops")
	
	if import_osm:
		OsmStopsImporter(db, osm_file = osmfile)
		print("Imported osm file")

	StopMatcher(db).match_stops()
	print("Matched and exported candidates")
	MatchPicker(db).pick_matches()
	MatchResultValidator(db).check_assertions()
	StatisticsUpdater(db).update_match_statistics()
	
	db.close()

	return 0

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Usage: python %s <osmfile> <stopsfile>" % sys.argv[0])
		sys.exit(-1)

	exit(main(sys.argv[1], sys.argv[2]))