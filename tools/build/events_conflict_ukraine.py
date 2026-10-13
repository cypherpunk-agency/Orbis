"""Conflict events in Ukraine, UCDP GED, aggregated by cell and month. See events_ucdp.py for sources and fetch steps.
Run: python3 tools/build/events_conflict_ukraine.py  ->  data/events/conflict-ukraine.json, conflict-ukraine-fatalities.json"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from events_ucdp import build

build("conflict-ukraine", "Ukraine", 202202, "Ukraine from February 2022 (Russian full-scale invasion on 24 February 2022)")
