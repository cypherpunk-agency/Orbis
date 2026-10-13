"""Conflict events in Syria, UCDP GED, aggregated by cell and month. See events_ucdp.py for sources and fetch steps.
Run: python3 tools/build/events_conflict_syria.py  ->  data/events/conflict-syria.json, conflict-syria-fatalities.json"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from events_ucdp import build

build("conflict-syria", "Syria", 201103, "Syria (civil war from March 2011)")
