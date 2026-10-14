#!/usr/bin/env python3
"""Event cards for the Holy Roman Empire series (hand-entered, editorial; every card cites its source).

Writes data/history/hre-events-{origins,patchwork,westphalia,end}.json.
Dates are stored in the proleptic Gregorian calendar as yyyymmdd. Sources that use the Julian calendar (everything before
1582, and Protestant estates until 18 Feb 1700) are entered as Julian with J(...) and converted here; such cards carry
"cal": "julian" so the card also shows the date as the source gives it.
"""
import json, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data", "history")
TODAY = time.strftime("%Y-%m-%d")


def jdn(y, m, d, julian):
    a = (14 - m) // 12; yy = y + 4800 - a; mm = m + 12 * a - 3
    if julian:
        return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - 32083
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045


def from_jdn(J):  # to Gregorian
    a = J + 32044; b = (4 * a + 3) // 146097; c = a - 146097 * b // 4
    d = (4 * c + 3) // 1461; e = c - 1461 * d // 4; m = (5 * e + 2) // 153
    return 100 * b + d - 4800 + m // 10, m + 3 - 12 * (m // 10), e - (153 * m + 2) // 5 + 1


def J(y, m, d):
    gy, gm, gd = from_jdn(jdn(y, m, d, True))
    return gy * 10000 + gm * 100 + gd


def G(y, m, d):
    return y * 10000 + m * 100 + d


assert J(1700, 2, 18) == 17000228 and J(1648, 10, 14) == 16481024

WP = "https://en.wikipedia.org/wiki/"
KINDS = {"rule": {"label": "Crowns and rulers", "color": "c5", "icon": "crown"},
         "war": {"label": "Wars and battles", "color": "c2", "icon": "swords"},
         "law": {"label": "Treaties and laws", "color": "c1", "icon": "flag"},
         "faith": {"label": "Religion", "color": "c2", "icon": "cross"}}


def card(title, date, at, kind, text, src, page, **kw):
    c = {"title": title, "date": date, "at": at, "kind": kind, "text": text, "source": src, "url": WP + page}
    c.update(kw)
    return c


ORIGINS = [
    card("Charlemagne crowned emperor", J(800, 12, 25), [12.4534, 41.9022], "rule",
         "Pope Leo III crowned Charlemagne, king of the Franks and of the Lombards, emperor in St Peter's in Rome on Christmas Day 800. The West had not had an emperor since 476.",
         "Wikipedia, 'Charlemagne'", "Charlemagne", cal="julian"),
    card("Charlemagne dies at Aachen", J(814, 1, 28), [6.0839, 50.7747], "rule",
         "Charlemagne died at Aachen, his favourite residence, and was buried in his palace chapel, today's Aachen Cathedral. German kings were crowned there until 1531.",
         "Wikipedia, 'Charlemagne'; 'Aachen Cathedral'", "Aachen_Cathedral", cal="julian"),
    card("Treaty of Verdun", 843, [5.3833, 49.1598], "law",
         "Charlemagne's grandsons split the empire in three: West Francia went to Charles the Bald, East Francia to Louis the German, and a middle kingdom from the North Sea to Italy, with the imperial title, to Lothair.",
         "Wikipedia, 'Treaty of Verdun'", "Treaty_of_Verdun"),
    card("Battle of Lechfeld", J(955, 8, 10), [10.88, 48.25], "war",
         "Otto I, king of East Francia, defeated the Magyar (Hungarian) horsemen near Augsburg, ending decades of raids into Germany. The victory made his name.",
         "Wikipedia, 'Battle of Lechfeld'", "Battle_of_Lechfeld", cal="julian"),
    card("Otto I crowned emperor", J(962, 2, 2), [12.4534, 41.9022], "rule",
         "Pope John XII crowned Otto emperor in Rome. From here on, whoever was elected king in Germany could claim the imperial crown: historians usually date the Holy Roman Empire from 962.",
         "Wikipedia, 'Holy Roman Empire'; 'Otto I, Holy Roman Emperor'", "Otto_I,_Holy_Roman_Emperor", cal="julian"),
    card("Otto III crowned in Rome", J(996, 5, 21), [12.4534, 41.9022], "rule",
         "Otto III, aged 15, was crowned emperor. He settled in Rome and called his programme a 'renewal of the Empire of the Romans'.",
         "Wikipedia, 'Otto III, Holy Roman Emperor'", "Otto_III,_Holy_Roman_Emperor", cal="julian"),
    card("Burgundy joins the Empire", J(1033, 2, 2), [6.938, 46.82], "rule",
         "Conrad II was crowned king of Burgundy at Payerne, adding the Kingdom of Burgundy (Arles), from Basel to Provence, to Germany and Italy: the third kingdom of the Empire.",
         "Wikipedia, 'Holy Roman Empire' (infobox); 'Kingdom of Burgundy'", "Kingdom_of_Burgundy", cal="julian"),
]

PATCHWORK = [
    card("The Golden Bull", 1356, [11.0767, 49.4521], "law",
         "Charles IV's Golden Bull, issued at Nuremberg and Metz, fixed who elected the king: seven prince-electors, three archbishops (Mainz, Cologne, Trier) and four secular princes (Bohemia, the Palatinate, Saxony, Brandenburg).",
         "Wikipedia, 'Golden Bull of 1356'", "Golden_Bull_of_1356"),
    card("Luther's theses", J(1517, 10, 31), [12.6484, 51.8664], "faith",
         "Martin Luther, a monk and professor at Wittenberg in Electoral Saxony, published 95 theses against the sale of indulgences. Within a few decades many princes and most imperial cities had turned Protestant.",
         "Wikipedia, 'Ninety-five Theses'; 'Reformation'", "Ninety-five_Theses", cal="julian"),
    card("Diet of Worms", J(1521, 4, 18), [8.3653, 49.6341], "faith",
         "Before Emperor Charles V and the princes, Luther refused to recant. The Edict of Worms outlawed him, but his prince, Frederick the Wise of Saxony, hid him at the Wartburg.",
         "Wikipedia, 'Diet of Worms'", "Diet_of_Worms", cal="julian"),
    card("Peace of Augsburg", J(1555, 9, 25), [10.8978, 48.3705], "law",
         "Emperor and estates agreed that each prince chooses the faith of his land, Catholic or Lutheran: later summed up as 'cuius regio, eius religio'. Calvinists were not included.",
         "Wikipedia, 'Peace of Augsburg'", "Peace_of_Augsburg", cal="julian"),
    card("Silesia goes to Prussia", J(1742, 7, 28), [17.0385, 51.1079], "war",
         "In 1740 Frederick II of Prussia invaded Habsburg Silesia. The Treaty of Berlin (28 July 1742) ceded almost all of it to Prussia, which kept it after two more wars.",
         "Wikipedia, 'First Silesian War'; 'Treaty of Berlin (1742)'", "Treaty_of_Berlin_(1742)", cal=None),
]
for c in PATCHWORK:  # 1742 is Gregorian already in Prussia and Austria
    if c.get("cal", "x") is None:
        c.pop("cal"); c["date"] = G(1742, 7, 28)

WESTPHALIA = [
    card("Defenestration of Prague", G(1618, 5, 23), [14.4003, 50.0905], "war",
         "Protestant Bohemian nobles threw two imperial governors and a secretary out of a window of Prague Castle. All three survived; the revolt that followed grew into the Thirty Years' War.",
         "Wikipedia, 'Defenestrations of Prague'", "Defenestrations_of_Prague"),
    card("Battle of White Mountain", G(1620, 11, 8), [14.3200, 50.0780], "war",
         "Imperial and Catholic League troops crushed the Bohemian rebels outside Prague. Bohemia was forcibly re-Catholicised.",
         "Wikipedia, 'Battle of White Mountain'", "Battle_of_White_Mountain"),
    card("Sack of Magdeburg", G(1631, 5, 20), [11.6276, 52.1205], "war",
         "Imperial and League troops stormed the Protestant city of Magdeburg. About 20,000 defenders and civilians died; of some 25,000 inhabitants about 5,000 survived.",
         "Wikipedia, 'Sack of Magdeburg'", "Sack_of_Magdeburg"),
    card("Battle of Lützen", G(1632, 11, 16), [12.1427, 51.2617], "war",
         "The Swedish army beat Wallenstein's imperial army near Leipzig, but King Gustavus Adolphus of Sweden was killed in the battle.",
         "Wikipedia, 'Battle of Lützen (1632)'", "Battle_of_L%C3%BCtzen_(1632)", cal="julian"),
    card("Peace of Westphalia", G(1648, 10, 24), [7.6261, 51.9625], "law",
         "Treaties negotiated at Münster and Osnabrück ended the war. Calvinists won the same rights as Lutherans; the princes could make alliances abroad; Sweden gained Western Pomerania, Bremen-Verden and Wismar; France kept Metz, Toul, Verdun and Habsburg rights in Alsace; the Swiss and Dutch were recognised as outside the Empire. Protestant delegates dated it 14 October.",
         "Wikipedia, 'Peace of Westphalia'", "Peace_of_Westphalia", cal="julian"),
    card("Protestants switch calendars", G(1700, 3, 1), [13.4050, 52.5200], "law",
         "The Protestant estates of the Empire adopted an 'improved calendar': Sunday 18 February 1700 was followed by Monday 1 March. For 117 years, Catholic and Protestant neighbours had dated letters ten days apart.",
         "Wikipedia, 'Adoption of the Gregorian calendar'", "Adoption_of_the_Gregorian_calendar"),
    card("Gregorian calendar", G(1582, 10, 15), [12.4534, 41.9022], "law",
         "Pope Gregory XIII's reform dropped ten days: Thursday 4 October 1582 was followed by Friday 15 October. Catholic states adopted it within a few years; the Empire's Protestant estates refused a calendar issued by the pope.",
         "Wikipedia, 'Gregorian calendar'; 'Adoption of the Gregorian calendar'", "Gregorian_calendar"),
]

END = [
    card("France annexes the left bank", G(1801, 2, 9), [6.4966, 48.5917], "law",
         "In the Treaty of Lunéville the Emperor accepted France's border on the Rhine. The princes who lost land on the left bank were to be compensated inside the Empire.",
         "Wikipedia, 'Treaty of Lunéville'", "Treaty_of_Lun%C3%A9ville"),
    card("The Imperial Recess", G(1803, 2, 25), [12.0974, 49.0134], "law",
         "A deputation of the Imperial Diet at Regensburg dissolved almost all church states and all but six of the 51 free imperial cities. In all, 112 imperial estates disappeared; their land went to 72 rulers, mostly Prussia, Bavaria, Württemberg and Baden.",
         "Wikipedia, 'German mediatisation'", "German_mediatisation"),
    card("Battle of Austerlitz", G(1805, 12, 2), [16.7625, 49.1278], "war",
         "Napoleon defeated the Austrian and Russian armies in Moravia. In the Peace of Pressburg Austria gave up Tyrol and its lands in Swabia.",
         "Wikipedia, 'Battle of Austerlitz'; 'Peace of Pressburg (1805)'", "Battle_of_Austerlitz"),
    card("Confederation of the Rhine", G(1806, 7, 12), [2.3522, 48.8566], "law",
         "Sixteen German states signed a treaty in Paris placing themselves under Napoleon's protection; on 1 August they declared that they had left the Empire.",
         "Wikipedia, 'Confederation of the Rhine'", "Confederation_of_the_Rhine"),
    card("The Empire ends", G(1806, 8, 6), [16.3655, 48.2083], "rule",
         "In Vienna, Francis II laid down the imperial crown and declared the Empire dissolved. He kept the title Emperor of Austria, which he had taken in 1804.",
         "Wikipedia, 'Dissolution of the Holy Roman Empire'", "Dissolution_of_the_Holy_Roman_Empire"),
    card("Kingdom of Westphalia", G(1807, 8, 18), [9.4797, 51.3127], "rule",
         "After defeating Prussia, Napoleon created a Kingdom of Westphalia for his brother Jérôme, with Kassel as its capital, from Hesse-Kassel, Brunswick and Prussian lands west of the Elbe.",
         "Wikipedia, 'Kingdom of Westphalia'", "Kingdom_of_Westphalia"),
]

for name, items in (("origins", ORIGINS), ("patchwork", PATCHWORK), ("westphalia", WESTPHALIA), ("end", END)):
    json.dump({"source": "editorial", "asOf": TODAY, "retrieved": TODAY,
               "note": "Event cards typed by Orbis from the cited Wikipedia articles. Dates are stored in the Gregorian calendar; cards marked Julian also show the date as their sources give it.",
               "kinds": {k: v for k, v in KINDS.items() if any(c["kind"] == k for c in items)}, "items": items},
              open(os.path.join(OUT, "hre-events-%s.json" % name), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("wrote hre-events-%s.json" % name, len(items))
