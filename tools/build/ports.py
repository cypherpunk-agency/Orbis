"""World's busiest container ports, hand-typed from official and port-authority figures (editorial facts),
plus schematic container shipping lanes drawn by Orbis (own work).
No download: the figures are typed in below with their sources. Optional check file for the 2009/2023 ranking:
  mkdir -p .cache/ports && curl -sSfL -o .cache/ports/hk.pdf https://www.mardep.gov.hk/filemanager/en/share/fact/pdf/portstat_2_y_b5.pdf
Run:    python3 tools/build/ports.py
Output: data/economics/ports.json  (points list: field "teu", periods 2009, 2023, 2024; million TEU)
        data/economics/shipping-lanes.json  (lines set "lanes", schematic)"""
import os, json, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
today = datetime.date.today().isoformat()
# million TEU. 2009 and 2023: Hong Kong Marine Department, "Ranking of Container Ports of the World" (as at
# 16 May 2024) - top ten ports of each year only, so other ports have no value for those years.
# 2024: port authorities / governments as reported (see SOURCES); rounded.
PORTS = [
    # id, name, [lon, lat], 2009, 2023, 2024
    ("shanghai", "Shanghai", [122.05, 30.63], 25.002, 49.158, 51.51),
    ("singapore", "Singapore", [103.78, 1.26], 25.867, 39.013, 41.12),
    ("ningbo", "Ningbo-Zhoushan", [121.88, 29.93], 10.503, 35.301, 39.30),
    ("shenzhen", "Shenzhen", [113.88, 22.50], 18.250, 29.880, 33.40),
    ("qingdao", "Qingdao", [120.20, 36.00], 10.276, 28.769, 30.87),
    ("guangzhou", "Guangzhou", [113.62, 22.75], 11.200, 25.414, 26.1),
    ("busan", "Busan", [129.05, 35.08], 11.980, 23.151, 24.4),
    ("tianjin", "Tianjin", [117.78, 38.97], None, 22.187, 23.3),
    ("jebelali", "Jebel Ali (Dubai)", [55.03, 25.01], 11.124, 14.472, 15.5),
    ("klang", "Port Klang", [101.36, 3.00], None, None, 14.64),
    ("rotterdam", "Rotterdam", [4.05, 51.95], 9.743, None, 13.8),
    ("hongkong", "Hong Kong", [114.12, 22.33], 21.040, 14.401, 13.69),
    ("antwerp", "Antwerp-Bruges", [4.30, 51.28], None, None, 13.5),
    ("pelepas", "Tanjung Pelepas", [103.55, 1.36], None, None, 12.25),
    ("losangeles", "Los Angeles", [-118.26, 33.73], None, None, 10.3),
    ("longbeach", "Long Beach", [-118.20, 33.75], None, None, 9.6),
    ("hamburg", "Hamburg", [9.93, 53.53], None, None, 7.8),
]
SOURCES = ("2009, 2023: Hong Kong Marine Department, Ranking of Container Ports of the World (as at 16.05.2024), top ten "
    "of each year only. 2024: Shanghai 51.5, Singapore 41.12, Ningbo-Zhoushan 39.3, Shenzhen 33.4, Qingdao 30.87, Tianjin 23.3 "
    "as compiled in the JOC Top 50 Global Container Ports (Aug 2025) from port data; Guangzhou 26.1 (port-reported, "
    "Container News; JOC lists 26.45 for Guangzhou-Nansha); Busan 24.4 (Busan Port Authority, via its 2025 release: "
    "24.88 in 2025, up 2.0% on 24.4); Jebel Ali 15.5 (DP World, Feb 2025); Port Klang 14.64 and Tanjung Pelepas 12.25 "
    "(Malaysia Ministry of Transport, via Bernama); Rotterdam 13.8 (Port of Rotterdam annual figures); Hong Kong 13.69 "
    "(Census and Statistics Department / Marine Department, 2024, down 5.0%); Antwerp-Bruges 13.5 and Hamburg 7.8 "
    "(HHLA Annual Report 2024, sector section); Los Angeles 10.3 (Port of Los Angeles, Jan 2025); Long Beach 9.6 "
    "(Port of Long Beach, record year). Positions: container terminals, rounded.")
pts = [{"id": i, "name": n, "at": at, "teu": [a, b, c]} for i, n, at, a, b, c in PORTS]
ports = {"source": "editorial", "asOf": "2025-08-04", "retrieved": today, "note": SOURCES,
         "periods": ["2009", "2023", "2024"], "units": {"teu": "million TEU (twenty-foot equivalent units)"}, "points": pts}

# schematic container lanes [lon, lat]; waypoints follow the usual sea routes, not exact tracks
LANES = [
    {"name": "Asia–Europe via Suez", "labelAt": 12, "path": [[122.05, 30.63], [121.0, 25.0], [114.5, 21.5], [110.0, 12.0],
        [105.0, 3.0], [104.3, 1.35], [103.78, 1.2], [103.4, 1.15], [102.4, 1.8], [101.0, 2.7], [98.5, 4.6], [95.5, 6.1], [80.5, 5.5], [65.0, 12.5], [52.0, 13.0], [43.4, 12.6],
        [40.0, 16.0], [36.5, 22.5], [34.0, 27.5], [32.55, 29.95], [32.3, 31.3], [25.0, 34.0], [15.0, 37.0], [5.0, 38.0],
        [-5.6, 35.95], [-10.0, 40.0], [-6.0, 48.5], [2.0, 51.0], [4.05, 51.95]]},
    {"name": "Asia–Europe via the Cape", "status": "diverted", "labelAt": 5, "path": [[95.5, 6.1], [80.5, 5.5], [70.0, -5.0],
        [55.0, -20.0], [38.0, -32.0], [25.0, -36.0], [18.5, -35.2], [12.0, -25.0], [3.0, -5.0], [-8.0, 3.0], [-18.0, 15.0],
        [-17.0, 28.0], [-11.0, 38.0], [-9.0, 44.0], [-6.0, 48.5]]},
    {"name": "Transpacific", "labelAt": 4, "path": [[122.05, 30.63], [129.05, 33.5], [140.0, 35.0], [160.0, 42.0], [180.0, 46.0],
        [-160.0, 46.0], [-140.0, 42.0], [-125.0, 36.0], [-118.26, 33.73]]},
    {"name": "Asia–US East Coast via Panama", "labelAt": 3, "path": [[122.05, 30.63], [140.0, 30.0], [180.0, 22.0],
        [-140.0, 15.0], [-100.0, 10.0], [-79.7, 9.1], [-75.0, 20.0], [-74.0, 40.5]]},
    {"name": "Transatlantic", "labelAt": 3, "path": [[4.05, 51.95], [2.0, 51.0], [-6.0, 49.5], [-30.0, 46.0],
        [-55.0, 42.0], [-74.0, 40.5]]},
]
lanes = {"source": "orbis-schematic", "asOf": today, "retrieved": today,
         "note": "Main container shipping lanes, drawn by Orbis for orientation (schematic). The Cape route is dashed: "
                 "most Asia–Europe services have used it since attacks on Red Sea shipping began in late 2023.",
         "lines": {"lanes": LANES}}
for name, obj in (("ports", ports), ("shipping-lanes", lanes)):
    out = os.path.join(root, "data/economics", name + ".json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(obj, open(out, "w"), separators=(",", ":"), ensure_ascii=False)
    print(out, os.path.getsize(out), "bytes")
top10 = sorted(PORTS, key=lambda p: -p[5])[:10]
print("2024 top 10:", ", ".join(p[1] for p in top10), "| total of listed:", round(sum(p[5] for p in PORTS), 1))
