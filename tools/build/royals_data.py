"""Hand-typed tables for tools/build/royals.py (series "Ruling houses of Europe").

Every row is a fact from the English Wikipedia article named next to it (facts only, no text copied):
house tables from the "List of monarchs of ..." articles of each crown; cards from the article in their "source".
Dates are Gregorian (yyyymmdd); where the source gives a Julian date (England before 14 Sep 1752, Russia before 1918)
the card carries "cal": "julian" and the date is converted with jul() below.
"""


def _jdn(y, m, d, julian):
    a = (14 - m) // 12
    yy = y + 4800 - a
    mm = m + 12 * a - 3
    if julian:
        return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - 32083
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045


def _from_jdn(j):  # Gregorian
    a = j + 32044
    b = (4 * a + 3) // 146097
    c = a - 146097 * b // 4
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    return 100 * b + d - 4800 + m // 10, m + 3 - 12 * (m // 10), e - (153 * m + 2) // 5 + 1


def jul(y, m, d):
    """Julian calendar date -> Gregorian yyyymmdd."""
    gy, gm, gd = _from_jdn(_jdn(y, m, d, True))
    return gy * 10000 + gm * 100 + gd


WP = "https://en.wikipedia.org/wiki/"

# ------------------------------------------------------------------ chapter 1: monarchs of England / GB / UK
# (name, from, to, house, Wikipedia title). Years after Wikipedia, "List of English monarchs" and "List of British monarchs".
_M = [
    ("Alfred the Great", 871, 899, "Wessex", "Alfred_the_Great"),
    ("Edward the Elder", 899, 924, "Wessex", "Edward_the_Elder"),
    ("Æthelstan", 924, 939, "Wessex", "Æthelstan"),
    ("Edmund I", 939, 946, "Wessex", "Edmund_I"),
    ("Eadred", 946, 955, "Wessex", "Eadred"),
    ("Eadwig", 955, 959, "Wessex", "Eadwig"),
    ("Edgar", 959, 975, "Wessex", "Edgar,_King_of_England"),
    ("Edward the Martyr", 975, 978, "Wessex", "Edward_the_Martyr"),
    ("Æthelred the Unready", 978, 1013, "Wessex", "Æthelred_the_Unready"),
    ("Sweyn Forkbeard", 1013, 1014, "Denmark", "Swein_Forkbeard"),
    ("Æthelred the Unready (again)", 1014, 1016, "Wessex", "Æthelred_the_Unready"),
    ("Edmund Ironside", 1016, 1016, "Wessex", "Edmund_Ironside"),
    ("Cnut", 1016, 1035, "Denmark", "Cnut"),
    ("Harold Harefoot", 1035, 1040, "Denmark", "Harold_Harefoot"),
    ("Harthacnut", 1040, 1042, "Denmark", "Harthacnut"),
    ("Edward the Confessor", 1042, 1066, "Wessex", "Edward_the_Confessor"),
    ("Harold II", 1066, 1066, "Godwin", "Harold_Godwinson"),
    ("William I", 1066, 1087, "Normandy", "William_the_Conqueror"),
    ("William II", 1087, 1100, "Normandy", "William_II_of_England"),
    ("Henry I", 1100, 1135, "Normandy", "Henry_I_of_England"),
    ("Stephen", 1135, 1154, "Blois", "Stephen,_King_of_England"),
    ("Henry II", 1154, 1189, "Plantagenet", "Henry_II_of_England"),
    ("Richard I", 1189, 1199, "Plantagenet", "Richard_I_of_England"),
    ("John", 1199, 1216, "Plantagenet", "John,_King_of_England"),
    ("Henry III", 1216, 1272, "Plantagenet", "Henry_III_of_England"),
    ("Edward I", 1272, 1307, "Plantagenet", "Edward_I"),
    ("Edward II", 1307, 1327, "Plantagenet", "Edward_II"),
    ("Edward III", 1327, 1377, "Plantagenet", "Edward_III"),
    ("Richard II", 1377, 1399, "Plantagenet", "Richard_II_of_England"),
    ("Henry IV", 1399, 1413, "Lancaster", "Henry_IV_of_England"),
    ("Henry V", 1413, 1422, "Lancaster", "Henry_V_of_England"),
    ("Henry VI", 1422, 1461, "Lancaster", "Henry_VI_of_England"),
    ("Edward IV", 1461, 1470, "York", "Edward_IV"),
    ("Henry VI (again)", 1470, 1471, "Lancaster", "Henry_VI_of_England"),
    ("Edward IV (again)", 1471, 1483, "York", "Edward_IV"),
    ("Edward V", 1483, 1483, "York", "Edward_V"),
    ("Richard III", 1483, 1485, "York", "Richard_III_of_England"),
    ("Henry VII", 1485, 1509, "Tudor", "Henry_VII_of_England"),
    ("Henry VIII", 1509, 1547, "Tudor", "Henry_VIII"),
    ("Edward VI", 1547, 1553, "Tudor", "Edward_VI"),
    ("Lady Jane Grey (disputed)", 1553, 1553, "Tudor", "Lady_Jane_Grey"),
    ("Mary I", 1553, 1558, "Tudor", "Mary_I"),
    ("Elizabeth I", 1558, 1603, "Tudor", "Elizabeth_I"),
    ("James I (James VI of Scotland)", 1603, 1625, "Stuart", "James_VI_and_I"),
    ("Charles I", 1625, 1649, "Stuart", "Charles_I_of_England"),
    ("Charles II", 1660, 1685, "Stuart", "Charles_II_of_England"),
    ("James II", 1685, 1688, "Stuart", "James_II_of_England"),
    ("Mary II", 1689, 1694, "Stuart", "Mary_II"),
    ("William III", 1689, 1702, "Orange", "William_III_of_England"),
    ("Anne", 1702, 1714, "Stuart", "Anne,_Queen_of_Great_Britain"),
    ("George I", 1714, 1727, "Hanover", "George_I_of_Great_Britain"),
    ("George II", 1727, 1760, "Hanover", "George_II_of_Great_Britain"),
    ("George III", 1760, 1820, "Hanover", "George_III"),
    ("George IV", 1820, 1830, "Hanover", "George_IV"),
    ("William IV", 1830, 1837, "Hanover", "William_IV"),
    ("Victoria", 1837, 1901, "Hanover", "Queen_Victoria"),
    ("Edward VII", 1901, 1910, "Saxe-Coburg and Gotha", "Edward_VII"),
    ("George V", 1910, 1936, "Saxe-Coburg and Gotha, from 1917 Windsor", "George_V"),
    ("Edward VIII", 1936, 1936, "Windsor", "Edward_VIII"),
    ("George VI", 1936, 1952, "Windsor", "George_VI"),
    ("Elizabeth II", 1952, 2022, "Windsor", "Elizabeth_II"),
    ("Charles III", 2022, None, "Windsor", "Charles_III"),
]
MONARCHS = [{"name": n, "from": a, "to": b, "house": h, "url": WP + t} for n, a, b, h, t in _M]
# what the Wikidata P53 label must contain to count as the same house
HOUSE_MATCH = {"Wessex": "Wessex", "Denmark": "Knýtlinga", "Godwin": "Godwin", "Normandy": "Normandy", "Blois": "Blois",
               "Plantagenet": "Plantagenet", "Lancaster": "Lancaster", "York": "York", "Tudor": "Tudor",
               "Stuart": "Stuart", "Orange": "Orange", "Hanover": "Hanover",
               "Saxe-Coburg and Gotha": "Saxe-Coburg", "Saxe-Coburg and Gotha, from 1917 Windsor": "Windsor",
               "Windsor": "Windsor"}
# Wikidata spells the Stuarts "House of Stewart di Darnley" for most of them
HOUSE_ALT = {"Stuart": ["Stewart"]}

# gantt rows for the story: (row label, house names in MONARCHS, colour)
GANTT_ROWS = [
    ("Wessex", ["Wessex"], "c6"), ("Denmark", ["Denmark"], "c7"), ("Godwin", ["Godwin"], "muted"),
    ("Normandy", ["Normandy"], "c5"), ("Blois", ["Blois"], "muted"), ("Plantagenet", ["Plantagenet"], "c2"),
    ("Lancaster", ["Lancaster"], "c7"), ("York", ["York"], "c1"), ("Tudor", ["Tudor"], "c4"),
    ("Stuart", ["Stuart"], "c3"), ("Orange", ["Orange"], "c8"), ("Hanover", ["Hanover"], "c5"),
    ("Saxe-Coburg", ["Saxe-Coburg and Gotha", "Saxe-Coburg and Gotha, from 1917 Windsor"], "c6"),
    ("Windsor", ["Windsor"], "c2"),
]

# ------------------------------------------------------------------ chapter 1: realms (historical-basemaps snapshots)
REALM_GROUPS = {
    "england": {"label": "English crown (with lands in France and Ireland)", "color": "c1"},
    "scotland": {"label": "Scottish crown", "color": "c4"},
    "britain": {"label": "British crown (from 1707)", "color": "c5"},
    "ireland": {"label": "Kingdom of Ireland (same king)", "color": "c3"},
}
REALMS = [
    (1000, {"England": ("england", "Kingdom of England"), "Scotland": ("scotland", "Kingdom of Scotland")}),
    (1200, {"Angevin Empire": ("england", "Lands of the Plantagenet kings"), "Scotland": ("scotland", "Kingdom of Scotland")}),
    (1300, {"English territory": ("england", "Lands of the English crown"), "Scotland": ("scotland", "Kingdom of Scotland")}),
    (1500, {"England": ("england", "England and the Lordship of Ireland"), "Scotland": ("scotland", "Kingdom of Scotland")}),
    (1600, {"England and Ireland": ("england", "England and Ireland"), "Scotland": ("scotland", "Kingdom of Scotland")}),
    (1700, {"England and Ireland": ("england", "England and Ireland (same king as Scotland since 1603)"),
            "Scotland": ("scotland", "Kingdom of Scotland (same king as England since 1603)")}),
    (1715, {"United Kingdom": ("britain", "Kingdom of Great Britain"), "Kingdom of Ireland": ("ireland", "Kingdom of Ireland")}),
    (1815, {"United Kingdom of Great Britain and Ireland": ("britain", "United Kingdom of Great Britain and Ireland")}),
]

# ------------------------------------------------------------------ chapter 2: houses by crown, 1500-2026
CATS = {  # key: (legend label, colour)
    "capet": ("Capetians: Valois, Bourbon, Orléans", "c1"),
    "habsburg": ("Habsburg (and Habsburg-Lorraine)", "c3"),
    "britain": ("Tudor and Stuart", "c7"),
    "hanover": ("Hanover (Welf)", "c8"),
    "wettin": ("Wettin, incl. Saxe-Coburg and Windsor", "#3E9B4F"),
    "romanov": ("Romanov", "c2"),
    "hohenzollern": ("Hohenzollern", "ink"),
    "wittelsbach": ("Wittelsbach", "c4"),
    "oldenburg": ("Oldenburg, incl. Glücksburg and Holstein-Gottorp", "c5"),
    "vasa": ("Vasa and Bernadotte", "s1"),
    "braganza": ("Aviz and Braganza", "s2"),
    "savoy": ("Savoy", "s3"),
    "orange": ("Orange-Nassau and Nassau", "#EE8A2A"),
    "bonaparte": ("Bonaparte (Napoleon's family)", "#D8B630"),
    "osman": ("Osman (Ottoman sultans)", "c6"),
    "other": ("Other houses and rulers", "muted"),
    "none": ("Republic, or no monarch", "s0"),
}
CROWNS_NOTE = ("Which house held the crown that ruled each area, 1500-2026, typed by Orbis from Wikipedia's lists of monarchs "
               "for each crown (e.g. 'List of French monarchs', 'List of Spanish monarchs', 'List of monarchs of Portugal', "
               "'List of Polish monarchs', 'List of Russian monarchs', 'List of Swedish monarchs', 'List of Danish monarchs', "
               "'List of Norwegian monarchs', 'List of Hungarian monarchs', 'List of Bohemian monarchs', 'Kings of Naples', "
               "'List of monarchs of Sicily', 'List of monarchs of Sardinia', 'List of Dutch monarchs', 'List of rulers of "
               "Bavaria', 'List of rulers of Saxony', 'List of rulers of Brandenburg', 'List of sultans of the Ottoman "
               "Empire') and the articles on each state. Areas are today's countries, or groups of today's regions in the UK, "
               "Germany, Italy and Russia, standing for the crown seated there: an approximation, since historical borders "
               "differed. A change is placed in the year it took effect; short occupations and rival claimants are mostly "
               "left out. 'Rest of Germany' (many small states) and the Papal States are grey until unification. Houses "
               "are grouped by family: Valois, Bourbon and Orléans as Capetians; Windsor with Saxe-Coburg as a Wettin "
               "branch; Glücksburg and Holstein-Gottorp with Oldenburg; Romanov counts its Holstein-Gottorp-Romanov line.")

# rows: (first year, label shown on tap, category)
CROWNS = {
    "GB-ENG": [(1500, "Kingdom of England · Tudor", "britain"), (1603, "England, under the Scottish king James I · Stuart", "britain"),
               (1649, "Commonwealth: no king", "none"), (1660, "England · Stuart, restored", "britain"),
               (1689, "England · William III of Orange-Nassau, with Mary II (Stuart)", "orange"),
               (1702, "England · Anne (Stuart)", "britain"), (1707, "Great Britain · Anne (Stuart)", "britain"),
               (1714, "Great Britain · Hanover", "hanover"), (1801, "United Kingdom · Hanover", "hanover"),
               (1901, "United Kingdom · Saxe-Coburg and Gotha", "wettin"),
               (1917, "United Kingdom · Windsor (renamed from Saxe-Coburg and Gotha)", "wettin")],
    "GB-SCT": [(1500, "Kingdom of Scotland · Stewart", "britain"), (1603, "Scotland · Stuart (same king as England)", "britain"),
               (1651, "Commonwealth: no king", "none"), (1660, "Scotland · Stuart, restored", "britain"),
               (1689, "Scotland · William III of Orange-Nassau, with Mary II (Stuart)", "orange"),
               (1702, "Scotland · Anne (Stuart)", "britain"), (1707, "Great Britain · Anne (Stuart)", "britain"),
               (1714, "Great Britain · Hanover", "hanover"), (1801, "United Kingdom · Hanover", "hanover"),
               (1901, "United Kingdom · Saxe-Coburg and Gotha", "wettin"), (1917, "United Kingdom · Windsor", "wettin")],
    "GB-NIR": [(1500, "Lordship of Ireland, English crown · Tudor", "britain"), (1542, "Kingdom of Ireland · Tudor", "britain"),
               (1603, "Kingdom of Ireland · Stuart", "britain"), (1649, "Commonwealth: no king", "none"),
               (1660, "Kingdom of Ireland · Stuart", "britain"), (1689, "Kingdom of Ireland · William III of Orange-Nassau", "orange"),
               (1702, "Kingdom of Ireland · Anne (Stuart)", "britain"), (1714, "Kingdom of Ireland · Hanover", "hanover"),
               (1801, "United Kingdom · Hanover", "hanover"), (1901, "United Kingdom · Saxe-Coburg and Gotha", "wettin"),
               (1917, "United Kingdom · Windsor", "wettin")],
    "IRL": [(1500, "Lordship of Ireland, English crown · Tudor", "britain"), (1542, "Kingdom of Ireland · Tudor", "britain"),
            (1603, "Kingdom of Ireland · Stuart", "britain"), (1649, "Commonwealth: no king", "none"),
            (1660, "Kingdom of Ireland · Stuart", "britain"), (1689, "Kingdom of Ireland · William III of Orange-Nassau", "orange"),
            (1702, "Kingdom of Ireland · Anne (Stuart)", "britain"), (1714, "Kingdom of Ireland · Hanover", "hanover"),
            (1801, "United Kingdom · Hanover", "hanover"), (1901, "United Kingdom · Saxe-Coburg and Gotha", "wettin"),
            (1917, "United Kingdom · Windsor", "wettin"), (1922, "Irish Free State, the British king as head of state · Windsor", "wettin"),
            (1949, "Republic of Ireland", "none")],
    "FRA": [(1500, "Kingdom of France · Valois", "capet"), (1589, "Kingdom of France · Bourbon", "capet"),
            (1792, "French Republic", "none"), (1804, "French Empire · Napoleon I (Bonaparte)", "bonaparte"),
            (1814, "Kingdom of France · Bourbon, restored", "capet"), (1830, "Kingdom of the French · Louis-Philippe (Orléans)", "capet"),
            (1848, "French Republic", "none"), (1852, "French Empire · Napoleon III (Bonaparte)", "bonaparte"),
            (1870, "French Republic", "none")],
    "ESP": [(1500, "Castile and Aragon · Trastámara (the Catholic Monarchs)", "other"), (1516, "Spain · Habsburg", "habsburg"),
            (1700, "Spain · Bourbon (Philip V)", "capet"), (1808, "Spain · Joseph Bonaparte", "bonaparte"),
            (1813, "Spain · Bourbon, restored", "capet"), (1868, "Spain: revolution, no king", "none"),
            (1870, "Spain · Amadeo I (Savoy)", "savoy"), (1873, "First Spanish Republic", "none"),
            (1874, "Spain · Bourbon, restored", "capet"), (1931, "Second Spanish Republic", "none"),
            (1939, "Spain under Franco: no king", "none"), (1975, "Spain · Bourbon (Juan Carlos I, then Felipe VI)", "capet")],
    "PRT": [(1500, "Portugal · Aviz", "braganza"), (1580, "Portugal · Habsburg (kings of Spain)", "habsburg"),
            (1640, "Portugal · Braganza", "braganza"), (1910, "Portuguese Republic", "none")],
    "NLD": [(1500, "Burgundian Netherlands · Habsburg", "habsburg"), (1581, "Dutch Republic (stadtholders of Orange-Nassau)", "none"),
            (1795, "Batavian Republic", "none"), (1806, "Kingdom of Holland · Louis Bonaparte", "bonaparte"),
            (1810, "Annexed to Napoleon's France", "bonaparte"), (1813, "Netherlands · Orange-Nassau", "orange")],
    "BEL": [(1500, "Burgundian Netherlands · Habsburg", "habsburg"), (1556, "Spanish Netherlands · Habsburg", "habsburg"),
            (1714, "Austrian Netherlands · Habsburg", "habsburg"), (1795, "Annexed to the French Republic", "none"),
            (1804, "French Empire · Napoleon I (Bonaparte)", "bonaparte"),
            (1815, "United Kingdom of the Netherlands · Orange-Nassau", "orange"),
            (1831, "Belgium · Saxe-Coburg (now House of Belgium)", "wettin")],
    "LUX": [(1500, "Duchy of Luxembourg · Habsburg", "habsburg"), (1684, "Occupied by Louis XIV's France · Bourbon", "capet"),
            (1697, "Duchy of Luxembourg · Habsburg", "habsburg"), (1795, "Annexed to the French Republic", "none"),
            (1804, "French Empire · Napoleon I (Bonaparte)", "bonaparte"),
            (1815, "Grand Duchy of Luxembourg · Orange-Nassau (the Dutch king)", "orange"),
            (1890, "Grand Duchy of Luxembourg · Nassau-Weilburg", "orange")],
    "CHE": [(1500, "Swiss Confederation: no monarch", "none")],
    "AUT": [(1500, "Archduchy of Austria · Habsburg", "habsburg"), (1804, "Austrian Empire · Habsburg-Lorraine", "habsburg"),
            (1867, "Austria-Hungary · Habsburg-Lorraine", "habsburg"), (1918, "Republic of Austria", "none")],
    "CZE": [(1500, "Kingdom of Bohemia · Jagiellon", "other"), (1526, "Kingdom of Bohemia · Habsburg", "habsburg"),
            (1619, "Kingdom of Bohemia · Frederick V, the 'Winter King' (Wittelsbach)", "wittelsbach"),
            (1620, "Kingdom of Bohemia · Habsburg", "habsburg"),
            (1741, "Kingdom of Bohemia · Charles Albert of Bavaria (Wittelsbach)", "wittelsbach"),
            (1743, "Kingdom of Bohemia · Habsburg-Lorraine", "habsburg"), (1918, "Czechoslovakia: republic", "none")],
    "SVK": [(1500, "Kingdom of Hungary · Jagiellon", "other"),
            (1526, "Kingdom of Hungary · Habsburg (Pressburg, today's Bratislava, was its capital 1536-1783)", "habsburg"),
            (1918, "Czechoslovakia: republic", "none")],
    "HUN": [(1500, "Kingdom of Hungary · Jagiellon", "other"), (1526, "Hungary, contested · John Zápolya", "other"),
            (1541, "Buda under the Ottoman sultan", "osman"), (1686, "Kingdom of Hungary · Habsburg", "habsburg"),
            (1918, "Hungary: republic, from 1920 a kingdom with no king (regent Horthy)", "none")],
    "POL": [(1500, "Kingdom of Poland · Jagiellon", "other"), (1573, "Poland-Lithuania · Henry of Valois (elected)", "capet"),
            (1575, "Poland-Lithuania · Stephen Báthory (elected)", "other"), (1587, "Poland-Lithuania · Vasa (elected)", "vasa"),
            (1669, "Poland-Lithuania · elected Polish nobles (Wiśniowiecki, Sobieski)", "other"),
            (1697, "Poland-Lithuania · Augustus II of Saxony (Wettin)", "wettin"),
            (1704, "Poland-Lithuania · Stanisław Leszczyński", "other"), (1709, "Poland-Lithuania · Augustus II (Wettin)", "wettin"),
            (1764, "Poland-Lithuania · Stanisław August Poniatowski", "other"),
            (1795, "Warsaw under Prussia (partitions) · Hohenzollern", "hohenzollern"),
            (1807, "Duchy of Warsaw · Frederick Augustus I of Saxony (Wettin)", "wettin"),
            (1815, "Kingdom of Poland, the Russian emperor as king · Romanov", "romanov"),
            (1915, "Occupied by the German Empire · Hohenzollern", "hohenzollern"), (1918, "Republic of Poland", "none")],
    "LTU": [(1500, "Grand Duchy of Lithuania · Jagiellon", "other"), (1573, "Poland-Lithuania · Henry of Valois (elected)", "capet"),
            (1575, "Poland-Lithuania · Stephen Báthory", "other"), (1587, "Poland-Lithuania · Vasa", "vasa"),
            (1669, "Poland-Lithuania · elected Polish nobles", "other"), (1697, "Poland-Lithuania · Augustus II (Wettin)", "wettin"),
            (1704, "Poland-Lithuania · Stanisław Leszczyński", "other"), (1709, "Poland-Lithuania · Augustus II (Wettin)", "wettin"),
            (1764, "Poland-Lithuania · Stanisław August Poniatowski", "other"), (1795, "Russian Empire · Romanov", "romanov"),
            (1915, "Occupied by the German Empire · Hohenzollern", "hohenzollern"), (1918, "Lithuania: republic (Soviet 1940-1990)", "none")],
    "BLR": [(1500, "Grand Duchy of Lithuania · Jagiellon", "other"), (1573, "Poland-Lithuania · Henry of Valois (elected)", "capet"),
            (1575, "Poland-Lithuania · Stephen Báthory", "other"), (1587, "Poland-Lithuania · Vasa", "vasa"),
            (1669, "Poland-Lithuania · elected Polish nobles", "other"), (1697, "Poland-Lithuania · Augustus II (Wettin)", "wettin"),
            (1704, "Poland-Lithuania · Stanisław Leszczyński", "other"), (1709, "Poland-Lithuania · Augustus II (Wettin)", "wettin"),
            (1764, "Poland-Lithuania · Stanisław August Poniatowski", "other"), (1793, "Russian Empire · Romanov", "romanov"),
            (1917, "Soviet republic, independent Belarus from 1991", "none")],
    "UKR": [(1500, "Grand Duchy of Lithuania · Jagiellon", "other"), (1569, "Kingdom of Poland · Jagiellon", "other"),
            (1573, "Poland-Lithuania · Henry of Valois (elected)", "capet"), (1575, "Poland-Lithuania · Stephen Báthory", "other"),
            (1587, "Poland-Lithuania · Vasa", "vasa"), (1648, "Cossack Hetmanate", "other"),
            (1667, "Kyiv under the Russian tsar · Romanov", "romanov"), (1917, "Ukrainian and Soviet republics; independent from 1991", "none")],
    "LVA": [(1500, "Livonia: the Livonian Order and the Archbishop of Riga", "other"),
            (1581, "Riga under Poland-Lithuania · Stephen Báthory", "other"), (1587, "Poland-Lithuania · Vasa", "vasa"),
            (1621, "Riga under Sweden · Vasa", "vasa"), (1654, "Swedish Riga · Wittelsbach (Palatinate-Zweibrücken)", "wittelsbach"),
            (1710, "Russian Empire · Romanov", "romanov"), (1918, "Latvia: republic (Soviet 1940-1991)", "none")],
    "EST": [(1500, "Livonia: the Livonian Order", "other"), (1561, "Swedish Estonia · Vasa", "vasa"),
            (1654, "Swedish Estonia · Wittelsbach (Palatinate-Zweibrücken)", "wittelsbach"), (1710, "Russian Empire · Romanov", "romanov"),
            (1918, "Estonia: republic (Soviet 1940-1991)", "none")],
    "SWE": [(1500, "Kalmar Union · Hans of Denmark (Oldenburg)", "oldenburg"), (1501, "Sweden under regents (Sture)", "other"),
            (1520, "Kalmar Union · Christian II (Oldenburg)", "oldenburg"), (1523, "Kingdom of Sweden · Vasa", "vasa"),
            (1654, "Sweden · Wittelsbach (Palatinate-Zweibrücken)", "wittelsbach"), (1720, "Sweden · Frederick I of Hesse", "other"),
            (1751, "Sweden · Holstein-Gottorp", "oldenburg"), (1818, "Sweden · Bernadotte", "vasa")],
    "FIN": [(1500, "Kalmar Union · Hans of Denmark (Oldenburg)", "oldenburg"), (1501, "Swedish crown under regents (Sture)", "other"),
            (1520, "Kalmar Union · Christian II (Oldenburg)", "oldenburg"), (1523, "Swedish crown · Vasa", "vasa"),
            (1654, "Swedish crown · Wittelsbach (Palatinate-Zweibrücken)", "wittelsbach"), (1720, "Swedish crown · Frederick I of Hesse", "other"),
            (1751, "Swedish crown · Holstein-Gottorp", "oldenburg"), (1809, "Grand Duchy of Finland, the Russian emperor · Romanov", "romanov"),
            (1917, "Republic of Finland", "none")],
    "NOR": [(1500, "Denmark-Norway · Oldenburg", "oldenburg"), (1814, "Union with Sweden · Charles XIII (Holstein-Gottorp)", "oldenburg"),
            (1818, "Union with Sweden · Bernadotte", "vasa"), (1905, "Kingdom of Norway · Glücksburg", "oldenburg")],
    "DNK": [(1500, "Kingdom of Denmark · Oldenburg", "oldenburg"), (1863, "Kingdom of Denmark · Glücksburg", "oldenburg")],
    "ISL": [(1500, "Danish crown · Oldenburg", "oldenburg"), (1863, "Danish crown · Glücksburg", "oldenburg"),
            (1918, "Kingdom of Iceland, the Danish king · Glücksburg", "oldenburg"), (1944, "Republic of Iceland", "none")],
    "RUS": [(1500, "Grand Principality of Moscow · Rurikid", "other"), (1598, "Tsardom of Russia · Boris Godunov", "other"),
            (1605, "Time of Troubles", "other"), (1610, "Moscow held for the Polish prince Władysław (Vasa), elected tsar", "vasa"),
            (1612, "Time of Troubles", "other"), (1613, "Tsardom of Russia · Romanov", "romanov"),
            (1762, "Russian Empire · Holstein-Gottorp-Romanov", "romanov"), (1917, "Soviet Russia; Russian Federation from 1991", "none")],
    "RU-KGD": [(1500, "State of the Teutonic Order", "other"), (1525, "Duchy of Prussia · Hohenzollern", "hohenzollern"),
               (1701, "Kingdom of Prussia · Hohenzollern", "hohenzollern"), (1871, "German Empire · Hohenzollern", "hohenzollern"),
               (1918, "German republic; Soviet Kaliningrad from 1945", "none")],
    "DE-PRU": [(1500, "Electorate of Brandenburg · Hohenzollern", "hohenzollern"), (1701, "Kingdom of Prussia · Hohenzollern", "hohenzollern"),
               (1871, "German Empire · Hohenzollern", "hohenzollern"), (1918, "German republic", "none")],
    "DE-BAV": [(1500, "Duchy of Bavaria · Wittelsbach", "wittelsbach"), (1623, "Electorate of Bavaria · Wittelsbach", "wittelsbach"),
               (1806, "Kingdom of Bavaria · Wittelsbach", "wittelsbach"), (1918, "Free State of Bavaria: republic", "none")],
    "DE-SAX": [(1500, "Saxony · Wettin", "wettin"), (1806, "Kingdom of Saxony · Wettin", "wettin"), (1918, "Free State of Saxony: republic", "none")],
    "DE-HAN": [(1500, "Duchies of Brunswick-Lüneburg · Welf", "hanover"), (1692, "Electorate of Hanover · Welf", "hanover"),
               (1714, "Electorate of Hanover, same king as Britain · Hanover", "hanover"),
               (1803, "Occupied by Napoleon's France", "bonaparte"), (1813, "Hanover, same king as Britain · Hanover", "hanover"),
               (1837, "Kingdom of Hanover, own king · Hanover", "hanover"), (1866, "Prussia · Hohenzollern", "hohenzollern"),
               (1918, "German republic", "none")],
    "DE-OTH": [(1500, "Many princes, bishops and free cities of the Holy Roman Empire", "other"),
               (1806, "Confederation of the Rhine and other German states", "other"),
               (1871, "German Empire · Hohenzollern", "hohenzollern"), (1918, "German republic", "none")],
    "IT-SAV": [(1500, "Duchy of Savoy, Piedmont · Savoy", "savoy"), (1536, "Piedmont occupied by France · Valois", "capet"),
               (1563, "Duchy of Savoy, capital Turin · Savoy", "savoy"), (1720, "Kingdom of Sardinia, capital Turin · Savoy", "savoy"),
               (1798, "Piedmont under the French Republic", "none"), (1804, "French Empire · Napoleon I (Bonaparte)", "bonaparte"),
               (1814, "Kingdom of Sardinia · Savoy", "savoy"), (1861, "Kingdom of Italy · Savoy", "savoy"),
               (1946, "Italian Republic", "none")],
    "IT-SAR": [(1500, "Kingdom of Sardinia, Crown of Aragon · Trastámara", "other"), (1516, "Kingdom of Sardinia · Habsburg (Spain)", "habsburg"),
               (1700, "Kingdom of Sardinia · Bourbon (Philip V)", "capet"), (1708, "Kingdom of Sardinia · Habsburg (Austria)", "habsburg"),
               (1717, "Kingdom of Sardinia · Bourbon (Spain)", "capet"), (1720, "Kingdom of Sardinia · Savoy", "savoy"),
               (1861, "Kingdom of Italy · Savoy", "savoy"), (1946, "Italian Republic", "none")],
    "IT-LIG": [(1500, "Republic of Genoa", "none"), (1805, "French Empire · Napoleon I (Bonaparte)", "bonaparte"),
               (1815, "Kingdom of Sardinia · Savoy", "savoy"), (1861, "Kingdom of Italy · Savoy", "savoy"), (1946, "Italian Republic", "none")],
    "IT-LOM": [(1500, "Duchy of Milan · Louis XII of France (Valois)", "capet"), (1512, "Duchy of Milan · Sforza", "other"),
               (1515, "Duchy of Milan · Francis I of France (Valois)", "capet"), (1521, "Duchy of Milan · Sforza", "other"),
               (1535, "Duchy of Milan · Habsburg (Spain)", "habsburg"), (1706, "Duchy of Milan · Habsburg (Austria)", "habsburg"),
               (1796, "Republics under French control", "none"), (1805, "Kingdom of Italy · Napoleon I (Bonaparte)", "bonaparte"),
               (1814, "Kingdom of Lombardy-Venetia · Habsburg-Lorraine", "habsburg"), (1859, "Kingdom of Sardinia · Savoy", "savoy"),
               (1861, "Kingdom of Italy · Savoy", "savoy"), (1946, "Italian Republic", "none")],
    "IT-VEN": [(1500, "Republic of Venice", "none"), (1797, "Austrian Venetia · Habsburg-Lorraine", "habsburg"),
               (1805, "Kingdom of Italy · Napoleon I (Bonaparte)", "bonaparte"),
               (1814, "Kingdom of Lombardy-Venetia · Habsburg-Lorraine", "habsburg"), (1866, "Kingdom of Italy · Savoy", "savoy"),
               (1946, "Italian Republic", "none")],
    "IT-TRE": [(1500, "County of Tyrol and Bishopric of Trent · Habsburg", "habsburg"),
               (1805, "Kingdom of Bavaria · Wittelsbach", "wittelsbach"), (1814, "Austrian Tyrol · Habsburg-Lorraine", "habsburg"),
               (1918, "Kingdom of Italy · Savoy", "savoy"), (1946, "Italian Republic", "none")],
    "IT-TUS": [(1500, "Republic of Florence", "none"), (1532, "Duchy of Florence, from 1569 Tuscany · Medici", "other"),
               (1737, "Grand Duchy of Tuscany · Habsburg-Lorraine", "habsburg"),
               (1801, "Kingdom of Etruria · Bourbon-Parma", "capet"), (1807, "French Empire · Napoleon I (Bonaparte)", "bonaparte"),
               (1814, "Grand Duchy of Tuscany · Habsburg-Lorraine", "habsburg"), (1860, "Kingdom of Sardinia · Savoy", "savoy"),
               (1861, "Kingdom of Italy · Savoy", "savoy"), (1946, "Italian Republic", "none")],
    "IT-PAP": [(1500, "Papal States (elected popes)", "other"), (1798, "Roman Republic, under France", "none"),
               (1800, "Papal States", "other"), (1809, "French Empire · Napoleon I (Bonaparte)", "bonaparte"),
               (1814, "Papal States", "other"), (1870, "Kingdom of Italy · Savoy", "savoy"), (1946, "Italian Republic", "none")],
    "IT-NAP": [(1500, "Kingdom of Naples · Trastámara", "other"), (1501, "Kingdom of Naples · Louis XII of France (Valois)", "capet"),
               (1504, "Kingdom of Naples · Ferdinand of Aragon (Trastámara)", "other"), (1516, "Kingdom of Naples · Habsburg (Spain)", "habsburg"),
               (1700, "Kingdom of Naples · Bourbon (Philip V)", "capet"), (1707, "Kingdom of Naples · Habsburg (Austria)", "habsburg"),
               (1734, "Kingdom of Naples · Bourbon", "capet"),
               (1806, "Kingdom of Naples · Joseph Bonaparte, then Joachim Murat", "bonaparte"),
               (1815, "Kingdom of the Two Sicilies · Bourbon", "capet"), (1860, "Kingdom of Sardinia, then Italy · Savoy", "savoy"),
               (1946, "Italian Republic", "none")],
    "IT-SIC": [(1500, "Kingdom of Sicily · Ferdinand of Aragon (Trastámara)", "other"), (1516, "Kingdom of Sicily · Habsburg (Spain)", "habsburg"),
               (1700, "Kingdom of Sicily · Bourbon (Philip V)", "capet"), (1713, "Kingdom of Sicily · Savoy", "savoy"),
               (1720, "Kingdom of Sicily · Habsburg (Austria)", "habsburg"), (1735, "Kingdom of Sicily · Bourbon", "capet"),
               (1860, "Kingdom of Sardinia, then Italy · Savoy", "savoy"), (1946, "Italian Republic", "none")],
    "TUR": [(1500, "Ottoman Empire · Osman", "osman"), (1922, "Sultanate abolished; Republic of Turkey from 1923", "none")],
    "GRC": [(1500, "Ottoman Empire · Osman", "osman"), (1828, "First Hellenic Republic (Kapodistrias)", "none"),
            (1832, "Kingdom of Greece · Otto (Wittelsbach)", "wittelsbach"), (1862, "Greece: Otto deposed", "none"),
            (1863, "Kingdom of Greece · Glücksburg", "oldenburg"), (1924, "Second Hellenic Republic", "none"),
            (1935, "Kingdom of Greece · Glücksburg, restored", "oldenburg"), (1973, "Hellenic Republic", "none")],
    "BGR": [(1500, "Ottoman Empire · Osman", "osman"), (1879, "Principality of Bulgaria · Alexander of Battenberg", "other"),
            (1887, "Bulgaria · Ferdinand of Saxe-Coburg (Wettin)", "wettin"), (1946, "People's Republic of Bulgaria", "none")],
    "ROU": [(1500, "Wallachia: own princes under Ottoman suzerainty", "osman"),
            (1859, "United Principalities · Alexandru Ioan Cuza", "other"),
            (1866, "Romania · Hohenzollern-Sigmaringen", "hohenzollern"), (1947, "People's Republic of Romania", "none")],
    "MDA": [(1500, "Principality of Moldavia · Stephen the Great", "other"),
            (1538, "Moldavia: own princes under Ottoman suzerainty", "osman"), (1812, "Bessarabia, Russian Empire · Romanov", "romanov"),
            (1918, "Kingdom of Romania · Hohenzollern-Sigmaringen", "hohenzollern"), (1940, "Soviet Moldavia; Moldova from 1991", "none")],
    "SRB": [(1500, "Belgrade, Kingdom of Hungary · Jagiellon", "other"), (1521, "Ottoman Empire · Osman", "osman"),
            (1718, "Habsburg Serbia", "habsburg"), (1739, "Ottoman Empire · Osman", "osman"),
            (1817, "Principality of Serbia · Obrenović and Karađorđević", "other"),
            (1918, "Kingdom of Serbs, Croats and Slovenes (Yugoslavia) · Karađorđević", "other"),
            (1945, "Yugoslavia, then Serbia: republic", "none")],
    "HRV": [(1500, "Kingdom of Croatia, with Hungary · Jagiellon", "other"), (1527, "Kingdom of Croatia · Habsburg", "habsburg"),
            (1918, "Kingdom of Serbs, Croats and Slovenes (Yugoslavia) · Karađorđević", "other"),
            (1941, "Axis occupation and puppet state", "none"), (1945, "Yugoslavia, then Croatia: republic", "none")],
    "SVN": [(1500, "Duchy of Carniola · Habsburg", "habsburg"), (1809, "Illyrian Provinces of Napoleon's France", "bonaparte"),
            (1813, "Austrian Empire · Habsburg-Lorraine", "habsburg"),
            (1918, "Kingdom of Serbs, Croats and Slovenes (Yugoslavia) · Karađorđević", "other"),
            (1941, "Axis occupation", "none"), (1945, "Yugoslavia, then Slovenia: republic", "none")],
    "BIH": [(1500, "Ottoman Empire · Osman", "osman"), (1878, "Austria-Hungary · Habsburg-Lorraine", "habsburg"),
            (1918, "Kingdom of Serbs, Croats and Slovenes (Yugoslavia) · Karađorđević", "other"),
            (1941, "Axis occupation and puppet state", "none"), (1945, "Yugoslavia, then Bosnia and Herzegovina: republic", "none")],
    "MNE": [(1500, "Ottoman Empire · Osman", "osman"), (1696, "Montenegro · Petrović-Njegoš", "other"),
            (1918, "Kingdom of Serbs, Croats and Slovenes (Yugoslavia) · Karađorđević", "other"),
            (1941, "Axis occupation", "none"), (1945, "Yugoslavia, then Montenegro: republic", "none")],
    "MKD": [(1500, "Ottoman Empire · Osman", "osman"), (1912, "Kingdom of Serbia, then Yugoslavia · Karađorđević", "other"),
            (1941, "Bulgarian occupation · Boris III (Saxe-Coburg)", "wettin"), (1944, "Yugoslavia, then North Macedonia: republic", "none")],
    "ALB": [(1500, "Ottoman Empire · Osman", "osman"), (1912, "Albania: independent, provisional government", "none"),
            (1914, "Principality of Albania · Wilhelm of Wied", "other"), (1915, "Albania: war and occupation, then regency and republic", "none"),
            (1928, "Kingdom of Albania · Zog I", "other"), (1939, "Kingdom of Albania · Victor Emmanuel III (Savoy)", "savoy"),
            (1943, "German occupation, then a communist republic", "none")],
    "XKX": [(1500, "Ottoman Empire · Osman", "osman"), (1912, "Kingdom of Serbia, then Yugoslavia · Karađorđević", "other"),
            (1941, "Albania under Italy · Victor Emmanuel III (Savoy)", "savoy"), (1944, "Yugoslavia, then Serbia; Kosovo from 2008", "none")],
    "CYP": [(1500, "Republic of Venice", "none"), (1571, "Ottoman Empire · Osman", "osman"),
            (1878, "British administration · Victoria (Hanover)", "hanover"), (1901, "British crown · Saxe-Coburg and Gotha", "wettin"),
            (1917, "British crown · Windsor", "wettin"), (1960, "Republic of Cyprus", "none")],
    "MLT": [(1500, "Kingdom of Sicily, Crown of Aragon · Trastámara", "other"), (1516, "Kingdom of Sicily · Habsburg (Spain)", "habsburg"),
            (1530, "Knights Hospitaller (elected grand masters)", "other"), (1798, "Occupied by the French Republic", "none"),
            (1800, "British crown · Hanover", "hanover"), (1901, "British crown · Saxe-Coburg and Gotha", "wettin"),
            (1917, "British crown · Windsor", "wettin"), (1964, "State of Malta, Elizabeth II as queen · Windsor", "wettin"),
            (1974, "Republic of Malta", "none")],
}

# ------------------------------------------------------------------ cards
K_ENG = {
    "crown": {"label": "Crowns and successions", "color": "c5", "icon": "crown"},
    "war": {"label": "Battles and revolts", "color": "c2", "icon": "swords"},
    "law": {"label": "Laws and unions", "color": "c1", "icon": "flag"},
}


def card(title, date, at, kind, text, src, julian=False, **kw):
    it = {"title": title, "date": date, "at": at, "kind": kind, "text": text, "source": "Wikipedia, '" + src + "'",
          "url": WP + src.replace(" ", "_")}
    if julian:
        it["cal"] = "julian"
    it.update(kw)
    return it


ENG = [
    card("Alfred becomes king of Wessex", 871, [-1.31, 51.06], "crown",
         "Alfred became king of the West Saxons in 871, in the middle of the Viking wars. By the 880s he called himself king of the Anglo-Saxons; his grandson Æthelstan ruled all England from 927.",
         "Alfred the Great"),
    card("Æthelstan, first king of all England", jul(927, 7, 12), [-2.73, 54.65], "crown",
         "At Eamont, near Penrith, the kings of Scotland, Strathclyde and Bamburgh accepted Æthelstan's rule on 12 July 927. Historians count him as the first king of England.",
         "Æthelstan", julian=True),
    card("Cnut, a Danish king of England", 1016, [-0.13, 51.51], "crown",
         "After Edmund Ironside died in November 1016, the Danish prince Cnut became king of all England. He later ruled Denmark and Norway too.",
         "Cnut"),
    card("Battle of Stamford Bridge", jul(1066, 9, 25), [-0.91, 53.99], "war",
         "Harold II defeated the Norwegian king Harald Hardrada, who had invaded with Harold's brother Tostig. Three days later William of Normandy landed in the south.",
         "Battle of Stamford Bridge", julian=True),
    card("Battle of Hastings", jul(1066, 10, 14), [0.49, 50.91], "war",
         "William, Duke of Normandy, defeated and killed Harold II. He was crowned in Westminster Abbey on Christmas Day 1066, and Norman lords replaced most of the English nobility.",
         "Battle of Hastings", julian=True),
    card("Henry II: the first Plantagenet", jul(1154, 12, 19), [0.24, 47.17], "crown",
         "Henry, Count of Anjou and Duke of Normandy, and through his wife Duke of Aquitaine, became king of England in 1154. He ruled more of France than the French king; he died at Chinon in 1189.",
         "Henry II of England", julian=True),
    card("Normandy lost", 1204, [1.09, 49.44], "war",
         "King John lost Normandy to Philip II of France when Rouen surrendered in 1204. English kings kept Gascony, around Bordeaux, until 1453.",
         "John, King of England"),
    card("Magna Carta", jul(1215, 6, 15), [-0.565, 51.444], "law",
         "Barons in revolt made King John agree a charter at Runnymede that limited royal power. The Pope annulled it within weeks, but it was reissued and became a founding text of English law.",
         "Magna Carta", julian=True),
    card("Battle of Agincourt", jul(1415, 10, 25), [2.14, 50.46], "war",
         "Henry V of Lancaster defeated a larger French army. By the Treaty of Troyes in 1420 he was to inherit the French crown, but he died in 1422 and France was lost by 1453.",
         "Battle of Agincourt", julian=True),
    card("Wars of the Roses end at Bosworth", jul(1485, 8, 22), [-1.41, 52.59], "war",
         "Henry Tudor, heir of the Lancastrian claim, defeated and killed Richard III of York. He married Elizabeth of York, uniting the two houses; the Tudor rose joins their emblems.",
         "Battle of Bosworth Field", julian=True),
    card("Henry VIII heads the Church", jul(1534, 11, 3), [-0.127, 51.4995], "law",
         "The Act of Supremacy made the king Supreme Head of the Church of England, ending the Pope's authority after Rome refused to annul Henry's first marriage.",
         "Acts of Supremacy", julian=True),
    card("Calais, the last foothold in France, is lost", jul(1558, 1, 7), [1.86, 50.95], "war",
         "France took Calais from Mary I. English kings had held it since 1347.",
         "Siege of Calais (1558)", julian=True),
    card("Union of the Crowns", jul(1603, 3, 24), [-3.19, 55.95], "crown",
         "Elizabeth I died childless. Her cousin James VI, king of Scotland since 1567, became James I of England: one king, but still two kingdoms with their own parliaments.",
         "Union of the Crowns", julian=True),
    card("Charles I executed", jul(1649, 1, 30), [-0.126, 51.504], "war",
         "After two civil wars, Parliament tried the king and beheaded him outside the Banqueting House in Whitehall. England was ruled without a king until 1660.",
         "Execution of Charles I", julian=True),
    card("The Restoration", jul(1660, 5, 29), [-0.13, 51.5], "crown",
         "Charles II, son of the executed king, returned to London on his 30th birthday and took the throne.",
         "Stuart Restoration", julian=True),
    card("The Glorious Revolution", jul(1688, 11, 5), [-3.51, 50.39], "crown",
         "The Dutch stadtholder William of Orange landed at Brixham with an army; the Catholic James II fled. In 1689 William III and Mary II were offered the crown together with the Bill of Rights.",
         "Glorious Revolution", julian=True),
    card("Act of Settlement", 1701, [-0.127, 51.4995], "law",
         "Parliament settled the crown on Sophia of Hanover, a granddaughter of James I, and her Protestant heirs, passing over closer Catholic relatives. Every monarch since descends from her.",
         "Act of Settlement 1701"),
    card("Acts of Union: Great Britain", jul(1707, 5, 1), [-3.19, 55.95], "law",
         "England and Scotland merged into one Kingdom of Great Britain with one parliament at Westminster. Scotland kept its own law and church.",
         "Acts of Union 1707", julian=True),
    card("George I: a German king", jul(1714, 8, 1), [9.73, 52.37], "crown",
         "Queen Anne died; Sophia had died weeks before, so her son George, Elector of Hanover, became king. Britain and Hanover shared a ruler until 1837.",
         "George I of Great Britain", julian=True),
    card("Union with Ireland", 18010101, [-6.26, 53.35], "law",
         "The Kingdom of Ireland merged with Great Britain into the United Kingdom of Great Britain and Ireland; the Irish parliament in Dublin closed.",
         "Acts of Union 1800"),
    card("Hanover goes its own way", 18370620, [9.73, 52.37], "crown",
         "Victoria became queen of the UK, but Hanover's law barred women while a male heir lived, so her uncle Ernest Augustus became king of Hanover.",
         "Kingdom of Hanover"),
    card("Windsor", 19170717, [-0.604, 51.483], "crown",
         "In the middle of the war with Germany, George V renamed the royal house from Saxe-Coburg and Gotha to Windsor, after the castle.",
         "House of Windsor"),
    card("Edward VIII abdicates", 19361211, [-0.6, 51.41], "crown",
         "Edward VIII gave up the throne to marry Wallis Simpson, an American divorcée; his brother became George VI.",
         "Abdication of Edward VIII"),
    card("Charles III", 20220908, [-3.23, 57.04], "crown",
         "Elizabeth II died at Balmoral after 70 years on the throne, the longest reign in British history. Her son became Charles III.",
         "Death and state funeral of Elizabeth II"),
]

K_EU = {
    "crown": {"label": "Crowns and successions", "color": "c5", "icon": "crown"},
    "war": {"label": "Wars and revolutions", "color": "c2", "icon": "swords"},
    "law": {"label": "Treaties and laws", "color": "c1", "icon": "flag"},
}
EU = [
    card("Charles of Habsburg inherits Spain", 1516, [-3.70, 40.42], "crown",
         "Charles, grandson of Ferdinand and Isabella and of Emperor Maximilian, inherited Castile and Aragon, with Naples, Sicily and Sardinia. In 1519 he was also elected Holy Roman Emperor as Charles V.",
         "Charles V, Holy Roman Emperor"),
    card("Mohács: Hungary's king falls", jul(1526, 8, 29), [18.68, 45.99], "war",
         "Louis II of Hungary and Bohemia died fleeing the Ottoman army. Under a marriage treaty, his brother-in-law Ferdinand of Habsburg was elected king in both kingdoms.",
         "Battle of Mohács", julian=True),
    card("Charles V divides his empire", 1556, [5.35, 50.93], "crown",
         "Charles V abdicated: Spain, the Netherlands and the Italian lands went to his son Philip II, Austria and the imperial title to his brother Ferdinand. Two Habsburg lines ruled from then on.",
         "Abdication of Charles V"),
    card("Spain's king takes Portugal", 1580, [-9.14, 38.72], "crown",
         "After Portugal's king died without heirs, Philip II of Spain claimed the crown and won it by force. Portugal regained its own king, John IV of Braganza, in 1640.",
         "Iberian Union"),
    card("Henry IV, the first Bourbon", 1589, [2.35, 48.86], "crown",
         "The last Valois king, Henry III, was murdered; his distant cousin Henry of Navarre succeeded him. Bourbons ruled France until 1792 and again 1814-1848.",
         "Henry IV of France"),
    card("Michael Romanov elected tsar", jul(1613, 2, 21), [37.62, 55.75], "crown",
         "After 15 years of famine, civil war and Polish occupation, an assembly in Moscow chose 16-year-old Michael Romanov as tsar. His family ruled until 1917.",
         "Michael I of Russia", julian=True),
    card("Augustus of Saxony elected king of Poland", 1697, [21.01, 52.23], "crown",
         "The Elector of Saxony, Frederick Augustus I, converted to Catholicism and won the election to the Polish throne as Augustus II. Saxon kings ruled Poland for most of 1697-1763.",
         "Augustus II the Strong"),
    card("War of the Spanish Succession", 1701, [-3.70, 40.42], "war",
         "Charles II, the last Spanish Habsburg, left his crowns to Philip of Anjou, grandson of Louis XIV. Britain, Austria and the Dutch went to war to stop a Bourbon union of France and Spain.",
         "War of the Spanish Succession"),
    card("A king in Prussia", 17010118, [20.51, 54.71], "crown",
         "Elector Frederick III of Brandenburg crowned himself Frederick I, King in Prussia, at Königsberg, today's Kaliningrad, outside the Holy Roman Empire.",
         "Frederick I of Prussia"),
    card("Peace of Utrecht", 1713, [5.12, 52.09], "law",
         "Philip V kept Spain but gave up any claim to France. Austria took Spain's Netherlands, Milan, Naples and Sardinia; Savoy got Sicily, which it swapped for Sardinia in 1720.",
         "Peace of Utrecht"),
    card("Napoleon crowns himself emperor", 18041202, [2.35, 48.85], "crown",
         "In Notre-Dame, Napoleon Bonaparte crowned himself Emperor of the French. Within four years his brothers were kings of Naples, Holland, Westphalia and Spain.",
         "Coronation of Napoleon"),
    card("A French marshal for Sweden", 18100821, [18.07, 59.33], "crown",
         "The childless Charles XIII needed an heir. Sweden's estates elected Napoleon's marshal Jean-Baptiste Bernadotte; he became king in 1818, and his descendants still reign.",
         "Charles XIV John"),
    card("Leopold I, king of the Belgians", 18310721, [4.35, 50.85], "crown",
         "After Belgium broke away from the Netherlands, Prince Leopold of Saxe-Coburg took the new throne. The Coburgs later also married into the thrones of Portugal and Britain and won Bulgaria's.",
         "Leopold I of Belgium"),
    card("Kingdom of Italy", 18610317, [7.69, 45.07], "crown",
         "Victor Emmanuel II of Savoy, king of Sardinia, became king of Italy. Venice joined in 1866 and Rome in 1870.",
         "Kingdom of Italy"),
    card("A Danish prince for Greece", 18630330, [23.73, 37.98], "crown",
         "After Greece deposed the Bavarian Otto, its assembly elected the 17-year-old Danish prince William, who reigned as George I until 1913.",
         "George I of Greece"),
    card("German Empire proclaimed", 18710118, [2.12, 48.80], "crown",
         "In the Hall of Mirrors at Versailles, King Wilhelm I of Prussia was proclaimed German Emperor. Bavaria, Saxony and the other states kept their own kings and dukes inside the empire.",
         "Proclamation of the German Empire"),
    card("Haakon VII: Norway's own king", 19051118, [10.75, 59.91], "crown",
         "After Norway left its union with Sweden, it chose Prince Carl of Denmark as king; he took the name Haakon VII.",
         "Haakon VII"),
    card("Empires fall", 19181109, [13.40, 52.52], "war",
         "Defeat in the First World War ended Europe's great monarchies: Russia's in 1917, Germany's and Austria-Hungary's in November 1918, the Ottoman sultanate in 1922.",
         "Abdication of Wilhelm II"),
    card("Italy votes for a republic", 19460602, [12.50, 41.90], "law",
         "In a referendum, 54% of voters chose a republic; the Savoy king Umberto II left for exile in Portugal.",
         "1946 Italian institutional referendum"),
    card("Juan Carlos restores the Spanish crown", 19751122, [-3.70, 40.42], "crown",
         "Two days after Franco's death, Juan Carlos of Bourbon, Franco's chosen successor and grandson of the last king, was proclaimed king.",
         "Juan Carlos I"),
]

K_COUS = {
    "crown": {"label": "Thrones and marriages", "color": "c5", "icon": "crown"},
    "war": {"label": "War and revolution", "color": "c2", "icon": "swords"},
}
COUS = [
    card("Vicky marries into Prussia", 18580125, [13.40, 52.52], "crown",
         "Victoria's eldest daughter married Prince Frederick of Prussia. Their son Wilhelm, born in 1859, was Victoria's first grandchild and became German Emperor in 1888.",
         "Victoria, Princess Royal"),
    card("Alexandra marries the Prince of Wales", 18630310, [-0.60, 51.48], "crown",
         "Christian IX's eldest daughter Alexandra married Victoria's son, the future Edward VII. Their son became George V.",
         "Alexandra of Denmark"),
    card("Dagmar marries the Russian heir", 18661109, [30.31, 59.94], "crown",
         "Christian IX's daughter Dagmar married the future Alexander III of Russia and took the name Maria Feodorovna. Their son became Nicholas II.",
         "Maria Feodorovna (Dagmar of Denmark)"),
    card("Alix of Hesse becomes empress", 18941126, [30.31, 59.94], "crown",
         "Victoria's granddaughter Alix of Hesse married Nicholas II weeks after he became emperor. She passed the haemophilia she carried from Victoria to their son Alexei.",
         "Alexandra Feodorovna (Alix of Hesse)"),
    card("Victoria dies", 19010122, [-1.30, 50.75], "crown",
         "Queen Victoria died at Osborne House on the Isle of Wight. Her grandson Wilhelm II was at her bedside.",
         "Death and state funeral of Queen Victoria"),
    card("Ena becomes queen of Spain", 19060531, [-3.71, 40.42], "crown",
         "Victoria's granddaughter Victoria Eugenie of Battenberg married Alfonso XIII. On the way back from the wedding an anarchist threw a bomb at the royal carriage; the couple survived, but people in the crowd were killed.",
         "Victoria Eugenie of Battenberg"),
    card("Nine kings at one funeral", 19100520, [-0.13, 51.50], "crown",
         "Nine reigning kings followed Edward VII's coffin through London, among them George V, Wilhelm II, Haakon VII and George I of Greece: most were his relatives.",
         "Death and state funeral of Edward VII"),
    card("The Willy-Nicky telegrams", 19140729, [13.06, 52.40], "war",
         "Between 29 July and 1 August 1914 Wilhelm II and Nicholas II exchanged ten telegrams in English, signed 'Willy' and 'Nicky', trying and failing to stop the war.",
         "Willy–Nicky correspondence"),
    card("Nicholas II abdicates", jul(1917, 3, 2), [28.33, 57.82], "war",
         "Facing revolution in Petrograd, Nicholas II abdicated in his train at Pskov. On 17 July 1918 the Bolsheviks shot him, Alexandra and their five children at Yekaterinburg.",
         "Abdication of Nicholas II", julian=True),
    card("Windsor", 19170717, [-0.60, 51.48], "crown",
         "With Britain at war with Germany, George V dropped the German name Saxe-Coburg and Gotha and named his house after Windsor Castle.",
         "House of Windsor"),
    card("Wilhelm II flees to the Netherlands", 19181110, [5.36, 52.05], "war",
         "With Germany defeated and revolution in Berlin, Wilhelm II crossed into the neutral Netherlands. He abdicated formally on 28 November and lived at Doorn until 1941.",
         "Abdication of Wilhelm II"),
]

CARDS = {"england": (K_ENG, ENG), "europe": (K_EU, EU), "cousins": (K_COUS, COUS)}

# ------------------------------------------------------------------ chapter 3: courts, lines, thrones
_C = {"London": [-0.14, 51.50], "Copenhagen": [12.59, 55.68], "Berlin": [13.40, 52.52], "St Petersburg": [30.31, 59.94],
      "Athens": [23.73, 37.98], "Kristiania (Oslo)": [10.75, 59.91], "Madrid": [-3.71, 40.42], "Bucharest": [26.10, 44.43],
      "Darmstadt": [8.65, 49.87], "Coburg": [10.96, 50.26]}


def _ln(name, a, b, frm, to, color, **kw):
    d = {"name": name, "path": [_C[a], _C[b]], "from": frm, "to": to, "color": color}
    d.update(kw)
    return d


# empires of 1914 drawn on the areas of data/geo/regions/royal-crowns.json
_EXPAND = {
    "GBR": ["GB-ENG", "GB-SCT", "GB-NIR", "IRL"],
    "DEU": ["DE-PRU", "DE-BAV", "DE-SAX", "DE-HAN", "DE-OTH", "RU-KGD"],
    "RUS": ["RUS", "FIN", "POL", "LTU", "LVA", "EST", "BLR", "UKR", "MDA"],
    "AUT": ["AUT", "CZE", "SVK", "HUN", "HRV", "SVN", "BIH", "IT-TRE"],
}


def _areas(d):
    out = {}
    for k, v in d.items():
        for u in _EXPAND.get(k, [k]):
            out[u] = v
    return out


COUSINS = {
    "source": "editorial", "asOf": "2026-10-14", "retrieved": "2026-10-14",
    "note": "Descendants of Queen Victoria (Wikipedia, 'Descendants of Queen Victoria', 'Queen Victoria') and of Christian IX of "
            "Denmark (Wikipedia, 'Christian IX') who reigned, or were the spouse of a reigning monarch, with the years they "
            "held the throne (articles on each person). Lines run from the founder's court to the court of the descendant; "
            "years are Gregorian.",
    "points": {"courts": [{"name": k, "at": v} for k, v in _C.items()]},
    "lines": {
        "victoria": [
            _ln("Wilhelm II, grandson: German Emperor 1888-1918", "London", "Berlin", 1888, 1918, "c2"),
            _ln("Ernest Louis, grandson: Grand Duke of Hesse 1892-1918", "London", "Darmstadt", 1892, 1918, "c2"),
            _ln("Alexandra, granddaughter: Empress of Russia 1894-1917", "London", "St Petersburg", 1894, 1917, "c2"),
            _ln("Charles Edward, grandson: Duke of Saxe-Coburg and Gotha 1900-1918", "London", "Coburg", 1900, 1918, "c2"),
            _ln("Maud, granddaughter: Queen of Norway 1905-1938", "London", "Kristiania (Oslo)", 1905, 1938, "c2"),
            _ln("Victoria Eugenie, granddaughter: Queen of Spain 1906-1931", "London", "Madrid", 1906, 1931, "c2"),
            _ln("Sophia, granddaughter: Queen of Greece 1913-1917, 1920-1922", "London", "Athens", 1913, 1917, "c2"),
            _ln("Marie, granddaughter: Queen of Romania 1914-1927", "London", "Bucharest", 1914, 1927, "c2"),
        ],
        "christian": [
            _ln("George I, son: King of Greece 1863-1913", "Copenhagen", "Athens", 1863, 1913, "c1"),
            _ln("Maria Feodorovna (Dagmar), daughter: Empress of Russia 1881-1894", "Copenhagen", "St Petersburg", 1881, 1894, "c1"),
            _ln("Nicholas II, grandson: Emperor of Russia 1894-1917", "Copenhagen", "St Petersburg", 1894, 1917, "c1", dash=True),
            _ln("Alexandra, daughter: Queen of the UK 1901-1910", "Copenhagen", "London", 1901, 1910, "c1"),
            _ln("George V, grandson: King of the UK 1910-1936", "Copenhagen", "London", 1910, 1936, "c1", dash=True),
            _ln("Haakon VII, grandson: King of Norway 1905-1957", "Copenhagen", "Kristiania (Oslo)", 1905, 1957, "c1"),
            _ln("Constantine I, grandson: King of Greece 1913-1917, 1920-1922", "Copenhagen", "Athens", 1913, 1917, "c1", dash=True),
        ],
    },
    "sets": {
        "thrones": {
            "label": "Who sat on the throne",
            "labels": {"victoria": "Victoria or her descendants", "christian": "Christian IX or his descendants",
                       "both": "Descendants of both", "fallen": "Monarchy abolished"},
            "byYear": {k: _areas(v) for k, v in {
                "1863": {"GBR": "victoria", "DNK": "christian", "GRC": "christian"},
                "1881": {"GBR": "victoria", "DNK": "christian", "GRC": "christian", "RUS": "christian"},
                "1888": {"GBR": "victoria", "DNK": "christian", "GRC": "christian", "RUS": "christian", "DEU": "victoria"},
                "1894": {"GBR": "victoria", "DNK": "christian", "GRC": "christian", "RUS": "both", "DEU": "victoria"},
                "1901": {"GBR": "both", "DNK": "christian", "GRC": "christian", "RUS": "both", "DEU": "victoria"},
                "1905": {"GBR": "both", "DNK": "christian", "GRC": "christian", "RUS": "both", "DEU": "victoria", "NOR": "both"},
                "1906": {"GBR": "both", "DNK": "christian", "GRC": "christian", "RUS": "both", "DEU": "victoria", "NOR": "both",
                         "ESP": "victoria"},
                "1913": {"GBR": "both", "DNK": "christian", "GRC": "both", "RUS": "both", "DEU": "victoria", "NOR": "both",
                         "ESP": "victoria"},
                "1914": {"GBR": "both", "DNK": "christian", "GRC": "both", "RUS": "both", "DEU": "victoria", "NOR": "both",
                         "ESP": "victoria", "ROU": "victoria"},
                "1917": {"GBR": "both", "DNK": "christian", "GRC": "both", "RUS": "fallen", "DEU": "victoria", "NOR": "both",
                         "ESP": "victoria", "ROU": "victoria"},
                "1918": {"GBR": "both", "DNK": "christian", "GRC": "both", "RUS": "fallen", "DEU": "fallen", "NOR": "both",
                         "ESP": "victoria", "ROU": "victoria"},
            }.items()},
        },
        "heirs": {
            "label": "Today's hereditary monarchs in Europe",
            "labels": {"yes": "Descends from Christian IX", "no": "Does not"},
            "values": {"DNK": "yes", "GBR": "yes", "BEL": "yes", "NOR": "yes", "ESP": "yes", "LUX": "yes",
                       "SWE": "no", "NLD": "no", "LIE": "no", "MCO": "no"},
        },
        "war1914": {
            "label": "Sides in August 1914",
            "labels": {"allies": "Allies: Russia, France, Britain, Serbia, Belgium", "central": "Central Powers: Germany, Austria-Hungary"},
            "values": _areas({"RUS": "allies", "FRA": "allies", "GBR": "allies", "SRB": "allies", "BEL": "allies", "MNE": "allies",
                              "DEU": "central", "AUT": "central"}),
        },
    },
}

# ------------------------------------------------------------------ chapter 4: today's monarchies
_TYPE = {  # Wikipedia, 'List of current monarchies' (table, column 'Type'), 2026-10-14
    "parl": ["AND", "ATG", "AUS", "BHS", "BEL", "BLZ", "KHM", "CAN", "DNK", "GRD", "JAM", "JPN", "LSO", "LUX", "MYS", "NLD", "NZL",
             "NOR", "PNG", "KNA", "LCA", "VCT", "SLB", "ESP", "SWE", "THA", "TUV", "GBR"],
    "semi": ["BHR", "BTN", "JOR", "KWT", "LIE", "MCO", "MAR", "QAT", "TON", "ARE"],
    "abs": ["BRN", "SWZ", "OMN", "SAU", "VAT"],
}
_REALMS = ["ATG", "AUS", "BHS", "BLZ", "CAN", "GRD", "JAM", "NZL", "PNG", "KNA", "LCA", "VCT", "SLB", "TUV", "GBR"]
_ELECT = {"VAT": "elected", "MYS": "elected", "AND": "exofficio", "KHM": "council", "SWZ": "council", "JOR": "council",
          "SAU": "council", "ARE": "council"}
_HOUSES = {"GBR": "windsor", "ESP": "bourbon", "BEL": "belgium", "NLD": "orange", "LUX": "nassau", "DNK": "glucksburg",
           "NOR": "glucksburg", "SWE": "bernadotte", "LIE": "liechtenstein", "MCO": "grimaldi", "AND": "none", "VAT": "none"}
TODAY_SETS = {
    "source": "editorial", "asOf": "2026-10-14", "retrieved": "2026-10-14",
    "note": "43 sovereign states with a monarch as head of state, with the type and succession given in Wikipedia's 'List of "
            "current monarchies' (read 14 Oct 2026; 'parliamentary' shown as constitutional). Commonwealth realms: the same "
            "list and 'Commonwealth realm'. Houses of Europe's reigning monarchs: the infobox of each monarch's Wikipedia "
            "article (Denmark: 'Monarchy of Denmark'). Norway: Haakon VIII since 28 August 2026; Luxembourg: Guillaume V "
            "since 3 October 2025.",
    "sets": {
        "type": {"label": "Type of monarchy", "labels": {"parl": "Constitutional: the monarch reigns, parliament governs",
                                                          "semi": "Mixed: the monarch keeps real power",
                                                          "abs": "Absolute: the monarch rules"},
                 "values": {c: k for k, v in _TYPE.items() for c in v}},
        "realms": {"label": "Charles III's realms", "labels": {"realm": "Commonwealth realm: Charles III is king"},
                   "values": {c: "realm" for c in _REALMS}},
        "elect": {"label": "How the monarch is chosen", "labels": {
            "elected": "Elected (pope; Malaysia's rulers pick a king every five years)",
            "exofficio": "By office (Andorra: France's president and a Catalan bishop)",
            "council": "Inherited, but a royal council chooses or confirms the heir",
            "heredit": "Inherited by birth"},
            "values": {c: _ELECT.get(c, "heredit") for v in _TYPE.values() for c in v}},
        "houses": {"label": "Europe's reigning houses", "labels": {
            "windsor": "Windsor", "bourbon": "Bourbon", "belgium": "Belgium (Saxe-Coburg)", "orange": "Orange-Nassau",
            "nassau": "Nassau (Luxembourg)", "glucksburg": "Glücksburg", "bernadotte": "Bernadotte",
            "liechtenstein": "Liechtenstein", "grimaldi": "Grimaldi", "none": "No reigning house (pope, co-princes)"},
            "values": _HOUSES},
    },
}
assert sum(len(v) for v in _TYPE.values()) == 43
