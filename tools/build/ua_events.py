"""War in Ukraine series: event cards (hand-entered, each with its source) and the 2014 shapes.
Writes
  data/history/ua-2014.json         shapes: Crimea + Sevastopol (annexed March 2014) and the Donetsk and Luhansk
                                    regions (context only: the area held by Russian-backed forces 2014-2022 is NOT
                                    mapped, because no openly licensed polygon of the 2015 line of contact was found)
                                    from Natural Earth 1:10m admin-1 (public domain).
  data/history/ua-cards-2014.json, ua-cards-2022.json, ua-cards-front.json   event cards (source: editorial;
                                    each card names the Wikipedia article or UN record it was checked against).
Dates are Gregorian yyyymmdd. Run: python3 tools/build/ua_events.py (needs .cache/admin1 from tools/build/admin1.py)"""
import os, json, subprocess, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(ROOT, ".cache/ua_events")
os.makedirs(CACHE, exist_ok=True)
TODAY = datetime.date.today().isoformat()
MS = os.path.join(ROOT, "tools/node_modules/mapshaper/bin/mapshaper")
WP = "https://en.wikipedia.org/wiki/"


def card(date, at, kind, title, text, src, page=None, **kw):
    d = {"title": title, "date": date, "at": at, "kind": kind, "text": text, "source": src}
    if page:
        d["url"] = WP + page
    d.update(kw)
    return d


# ---------------- 2014-2022 ----------------
C2014 = [
    card(20140222, [30.524, 50.450], "politics", "Yanukovych removed",
         "After three months of protests on Kyiv's Maidan, President Viktor Yanukovych leaves Kyiv and parliament removes him from office.",
         "Wikipedia: Revolution of Dignity", "Revolution_of_Dignity"),
    card(20140227, [34.10, 44.95], "military", "Crimea's parliament seized",
         "Armed men without insignia, later acknowledged as Russian special forces, seize Crimea's parliament and government buildings in Simferopol. The European Court of Human Rights later agreed that Russia controlled Crimea from this day.",
         "Wikipedia: 2014 Russian annexation of Crimea (ECHR, Ukraine v. Russia re Crimea, 2021)", "2014_Russian_annexation_of_Crimea"),
    card(20140316, [34.10, 44.95], "politics", "Referendum under occupation",
         "A referendum on joining Russia is held in Crimea while Russian troops control the peninsula. Ukraine and most UN member states do not recognise it.",
         "Wikipedia: 2014 Russian annexation of Crimea", "2014_Russian_annexation_of_Crimea"),
    card(20140318, [33.52, 44.60], "politics", "Annexation treaty",
         "Vladimir Putin signs a treaty in Moscow with the Russian-installed Crimean leaders, annexing Crimea and Sevastopol to Russia.",
         "Wikipedia: 2014 Russian annexation of Crimea", "2014_Russian_annexation_of_Crimea"),
    card(20140327, [32.0, 45.9], "politics", "UN: the referendum is invalid",
         "The UN General Assembly affirms Ukraine's territorial integrity and calls the Crimean referendum invalid (resolution 68/262): 100 in favour, 11 against, 58 abstentions.",
         "UN General Assembly resolution 68/262, 27 March 2014", "United_Nations_General_Assembly_Resolution_68/262"),
    card(20140412, [37.61, 48.85], "military", "Sloviansk seized",
         "An armed unit led by the Russian citizen Igor Girkin crosses from Russia and seizes Sloviansk. Separatists declare 'people's republics' in Donetsk and Luhansk; Ukraine answers with an 'anti-terrorist operation' on 15 April.",
         "Wikipedia: War in Donbas", "War_in_Donbas"),
    card(20140717, [38.64, 48.14], "civilian", "MH17 shot down",
         "Malaysia Airlines Flight 17 is shot down over separatist-held territory; all 298 people on board are killed. A Dutch-led investigation found the Buk missile system came from Russia's 53rd Anti-Aircraft Missile Brigade.",
         "Wikipedia: Malaysia Airlines Flight 17 (Joint Investigation Team, 2016)", "Malaysia_Airlines_Flight_17"),
    card(20140829, [38.20, 47.92], "military", "Ilovaisk",
         "Ukrainian forces that had entered Ilovaisk are encircled after Russian regular troops cross the border (24-26 August); many are killed as they withdraw on 29 August.",
         "Wikipedia: Battle of Ilovaisk", "Battle_of_Ilovaisk"),
    card(20140905, [27.56, 53.90], "politics", "Minsk Protocol",
         "Ukraine, Russia and the OSCE, with the separatist leaders, sign a ceasefire in Minsk: OSCE monitoring, withdrawal of foreign fighters and heavy weapons, local elections under Ukrainian law. The ceasefire does not hold.",
         "Wikipedia: Minsk agreements", "Minsk_agreements"),
    card(20150212, [27.56, 53.90], "politics", "Minsk II",
         "A second package of measures, brokered by France and Germany, sets a new ceasefire from 15 February 2015.",
         "Wikipedia: Minsk agreements", "Minsk_agreements"),
    card(20150218, [38.41, 48.34], "military", "Debaltseve",
         "Despite the new ceasefire, Russian and Russian-backed forces take the rail hub of Debaltseve; Ukrainian troops withdraw on 18 February. It is the last major battle before the front freezes.",
         "Wikipedia: Battle of Debaltseve", "Battle_of_Debaltseve"),
    card(20211231, [37.80, 48.00], "civilian", "14,200-14,400 dead",
         "The UN human rights office estimates 14,200-14,400 people were killed from April 2014 to the end of 2021: about 6,500 on the separatist side, 4,400 Ukrainian forces and 3,404 civilians. Most died in the first year.",
         "OHCHR, Conflict-related civilian casualties in Ukraine, 27 January 2022 (via Wikipedia: Casualties of the Russo-Ukrainian war)", "Casualties_of_the_Russo-Ukrainian_war"),
    card(20220221, [39.31, 48.57], "politics", "Russia recognises the 'republics'",
         "Russia recognises the Donetsk and Luhansk 'people's republics' as independent states and announces it is sending troops. Three days later it invades Ukraine.",
         "Wikipedia: War in Donbas", "War_in_Donbas"),
]

# ---------------- 2022 ----------------
C2022 = [
    card(20220224, [30.20, 50.58], "military", "The invasion begins",
         "Russian forces cross into Ukraine from Russia, Belarus and Crimea. Helicopter-borne troops attack Hostomel airport near Kyiv.",
         "Wikipedia: Northern front of the Russian invasion of Ukraine", "Northern_front_of_the_Russian_invasion_of_Ukraine"),
    card(20220302, [32.62, 46.64], "military", "Kherson occupied",
         "Russian forces begin the occupation of Kherson region; Kherson becomes the only regional capital they take in 2022.",
         "Wikipedia: 2022 Kherson counteroffensive", "2022_Kherson_counteroffensive"),
    card(20220304, [34.63, 47.51], "military", "Zaporizhzhia nuclear plant",
         "Russian troops take Enerhodar and the Zaporizhzhia nuclear power plant, the largest in Europe.",
         "Wikipedia: Battle of Enerhodar", "Battle_of_Enerhodar"),
    card(20220401, [30.21, 50.54], "civilian", "Bucha",
         "After Russian troops leave Bucha, evidence of the killing of civilians emerges. Local authorities recovered 458 bodies; the UN human rights office documented unlawful killings of at least 73 civilians there.",
         "Wikipedia: Bucha massacre (OHCHR)", "Bucha_massacre"),
    card(20220405, [31.29, 51.49], "military", "Retreat from the north",
         "Unable to take Kyiv, Russia withdraws from Kyiv, Zhytomyr, Chernihiv and Sumy regions in late March and early April.",
         "Wikipedia: Northern front of the Russian invasion of Ukraine", "Northern_front_of_the_Russian_invasion_of_Ukraine"),
    card(20220520, [37.55, 47.10], "military", "Mariupol falls",
         "The last Ukrainian defenders at the Azovstal steelworks surrender after a siege of almost three months. The UN confirmed 1,348 civilian deaths in the city and said the real toll was likely thousands higher.",
         "Wikipedia: Siege of Mariupol", "Siege_of_Mariupol"),
    card(20220906, [36.84, 49.46], "military", "Kharkiv counteroffensive",
         "Ukraine breaks through in Kharkiv region. It retakes Balakliia on 8 September and Izium and Kupiansk on 10 September.",
         "Wikipedia: 2022 Kharkiv counteroffensive", "2022_Kharkiv_counteroffensive"),
    card(20220930, [35.4, 47.0], "politics", "Annexation claim",
         "After referendums in occupied areas, Vladimir Putin announces the annexation of Donetsk, Luhansk, Kherson and Zaporizhzhia regions, including parts Russia does not hold. The UN General Assembly calls it invalid (143 in favour, 5 against).",
         "Wikipedia: Russo-Ukrainian war (2022-present); UN General Assembly resolution ES-11/4", "Russo-Ukrainian_war_(2022%E2%80%93present)"),
    card(20221001, [37.80, 48.99], "military", "Lyman",
         "Ukraine retakes Lyman, ending the Kharkiv counteroffensive. In about a month it regained over 500 settlements and some 12,000 km².",
         "Wikipedia: 2022 Kharkiv counteroffensive", "2022_Kharkiv_counteroffensive"),
    card(20221111, [32.62, 46.64], "military", "Kherson retaken",
         "Two days after Russia ordered its troops to withdraw across the Dnipro, Ukrainian forces enter Kherson city.",
         "Wikipedia: 2022 Kherson counteroffensive", "2022_Kherson_counteroffensive"),
]

# ---------------- the long front, 2023-2026 ----------------
CFRONT = [
    card(20221010, [30.52, 50.45], "energy", "The grid becomes a target",
         "Russia strikes power infrastructure across Ukraine with 84 cruise missiles and 24 drones. By 19 November about 10 million people were without electricity, according to President Zelenskyy.",
         "Wikipedia: Russian strikes against Ukrainian infrastructure", "Russian_strikes_against_Ukrainian_infrastructure"),
    card(20230520, [38.00, 48.60], "military", "Bakhmut",
         "After months of assaults led by the Wagner Group, Russian forces take most of Bakhmut. Some military analysts call it the bloodiest battle since World War II.",
         "Wikipedia: Battle of Bakhmut", "Battle_of_Bakhmut"),
    card(20230606, [33.37, 46.78], "energy", "Kakhovka dam destroyed",
         "The Russian-held Kakhovka dam is breached, flooding the lower Dnipro. Many experts concluded Russian forces likely blew it up; Russia denies this.",
         "Wikipedia: Destruction of the Kakhovka Dam", "Destruction_of_the_Kakhovka_Dam"),
    card(20230610, [35.83, 47.45], "military", "Counteroffensive stalls",
         "Ukraine's summer offensive in Zaporizhzhia and Donetsk meets dense minefields and trenches. It retakes 14 villages, about 370 km².",
         "Wikipedia: 2023 Ukrainian counteroffensive", "2023_Ukrainian_counteroffensive", circa=True),
    card(20240217, [37.75, 48.14], "military", "Avdiivka",
         "Ukraine withdraws from Avdiivka, near Donetsk, after a four-month Russian offensive: Russia's largest gain since Bakhmut.",
         "Wikipedia: Battle of Avdiivka (2023-2024)", "Battle_of_Avdiivka_(2023%E2%80%932024)"),
    card(20240322, [35.08, 47.87], "energy", "Dams and power plants hit",
         "A massive strike leaves more than a million people without power; missiles hit the Dnipro dam in Zaporizhzhia and Kharkiv's largest power plants. On 11 April the Trypilska plant near Kyiv is destroyed.",
         "Wikipedia: Russian strikes against Ukrainian infrastructure", "Russian_strikes_against_Ukrainian_infrastructure"),
    card(20240719, [37.43, 48.20], "military", "Towards Pokrovsk",
         "Russian forces capture Prohres, north-west of Avdiivka, and push towards Pokrovsk, a road and rail hub of western Donetsk.",
         "Wikipedia: Pokrovsk offensive", "Pokrovsk_offensive"),
    card(20240806, [35.27, 51.19], "military", "Ukraine enters Kursk",
         "Ukraine launches an incursion into Russia's Kursk region. By March 2025 most Ukrainian forces had been pushed out. (Fighting in Russia is not on the control map.)",
         "Wikipedia: Kursk campaign", "Kursk_campaign"),
    card([20251101, 20260228], [37.18, 48.28], "military", "Pokrovsk and Myrnohrad",
         "Russian forces enter Pokrovsk in November 2025 and are reported to have taken Pokrovsk and Myrnohrad in early 2026.",
         "Wikipedia: Pokrovsk offensive", "Pokrovsk_offensive"),
]

KINDS = {"military": {"label": "Fighting", "color": "c2", "icon": "swords"},
         "politics": {"label": "Politics and diplomacy", "color": "c5"},
         "civilian": {"label": "Civilian deaths", "color": "muted"},
         "energy": {"label": "Energy and dams", "color": "c3"}}


def cards(fn, items, what):
    kinds = {k: v for k, v in KINDS.items() if any(i["kind"] == k for i in items)}
    out = {"source": "editorial", "asOf": TODAY, "retrieved": TODAY, "kinds": kinds, "items": items,
           "note": what + " Hand-entered by Orbis; each card names the article or record it was checked against "
                  "(Wikipedia articles as retrieved on " + TODAY + ", text paraphrased). Dates are Gregorian. "
                  "Built by tools/build/ua_events.py."}
    json.dump(out, open(os.path.join(ROOT, fn), "w"), ensure_ascii=False, indent=0)
    print(fn, os.path.getsize(os.path.join(ROOT, fn)))


def shapes_2014():
    src = os.path.join(ROOT, ".cache/admin1/ne_10m_admin_1_states_provinces.shp")
    gj = os.path.join(CACHE, "ua2014.geojson")
    subprocess.run(["node", MS, "-i", src, "encoding=utf8",
                    "-filter", '["UA-43","UA-40","UA-14","UA-09"].indexOf(iso_3166_2)>=0',
                    "-each", 'grp=(iso_3166_2=="UA-43"||iso_3166_2=="UA-40")?"crimea":iso_3166_2',
                    "-dissolve", "grp", "-o", gj, "format=geojson"], check=True, capture_output=True)
    fc = json.load(open(gj))
    P = {"crimea": {"name": "Crimea and Sevastopol", "group": "annexed", "from": 20140318, "to": None, "at": [34.2, 45.3],
                    "note": "Annexed by Russia on 18 March 2014; not recognised by Ukraine or by UN General Assembly resolution 68/262."},
         "UA-14": {"name": "Donetsk region", "group": "donbas", "from": 20140412, "to": None, "opacity": 0.18, "at": [37.7, 48.2],
                   "note": "Russian-backed forces held part of this region (including Donetsk city) from 2014; the line of contact is not mapped here."},
         "UA-09": {"name": "Luhansk region", "group": "donbas", "from": 20140412, "to": None, "opacity": 0.18, "at": [39.2, 48.9],
                   "note": "Russian-backed forces held part of this region (including Luhansk city) from 2014; the line of contact is not mapped here."}}
    for f in fc["features"]:
        f["properties"] = P[f["properties"]["grp"]]
    json.dump(fc, open(gj, "w"))
    tj = os.path.join(CACHE, "ua2014.topo.json")
    subprocess.run(["node", MS, gj, "-simplify", "dp", "interval=500", "keep-shapes", "-rename-layers", "shapes",
                    "-o", tj, "format=topojson", "quantization=20000"], check=True, capture_output=True)
    out = {"source": "naturalearth", "asOf": "Natural Earth 1:10m admin-1 v5.1", "retrieved": TODAY,
           "note": "Outlines of the Autonomous Republic of Crimea, Sevastopol, and Donetsk and Luhansk regions from Natural "
                   "Earth (public domain), simplified. Crimea and Sevastopol are shown from the annexation treaty of 18 March "
                   "2014 (Russian forces controlled the peninsula from late February). Donetsk and Luhansk regions are shown "
                   "only as context from April 2014: Russian-backed forces held roughly the eastern parts, including both "
                   "regional capitals, but this file does not map the line of contact. Built by tools/build/ua_events.py.",
           "groups": {"annexed": {"label": "Crimea: annexed by Russia, March 2014", "color": "c2"},
                      "donbas": {"label": "Donetsk and Luhansk regions (war from April 2014)", "color": "c3"}},
           "topology": json.load(open(tj))}
    fn = os.path.join(ROOT, "data/history/ua-2014.json")
    json.dump(out, open(fn, "w"), separators=(",", ":"), ensure_ascii=False)
    print(fn, os.path.getsize(fn))


if __name__ == "__main__":
    shapes_2014()
    cards("data/history/ua-cards-2014.json", C2014, "Crimea and the war in Donbas, February 2014 to February 2022.")
    cards("data/history/ua-cards-2022.json", C2022, "The full-scale invasion and the 2022 counteroffensives.")
    cards("data/history/ua-cards-front.json", [c for c in CFRONT if c["kind"] != "energy" or "Kakhovka" in c["title"]],
          "The long front, 2023 to 2026.")
    cards("data/history/ua-cards-energy.json", [c for c in CFRONT if c["kind"] == "energy"],
          "Strikes on Ukraine's energy system and dams, October 2022 to 2024.")
