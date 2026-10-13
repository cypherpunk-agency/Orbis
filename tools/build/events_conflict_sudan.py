"""Conflict events in Sudan, UCDP GED, aggregated by cell and month. See events_ucdp.py for sources and fetch steps.
Run: python3 tools/build/events_conflict_sudan.py  ->  data/events/conflict-sudan.json, conflict-sudan-fatalities.json"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from events_ucdp import build

build("conflict-sudan", "Sudan", 202304, "Sudan (war between SAF and RSF from 15 April 2023)")
