#!/usr/bin/env python3
"""Hand-entered event cards for the Roman Empire series -> data/history/rome-events-{rise,frontier,fall}.json (source: editorial)."""
# writes data/history/rome-events-*.json (hand-entered cards; each card cites its source)
import json, os, time
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "history")
T = time.strftime("%Y-%m-%d")
W = "https://en.wikipedia.org/wiki/"
KINDS = {"war": {"label": "Battles and wars", "color": "c2", "icon": "swords"},
         "rule": {"label": "Rulers and states", "color": "c5", "icon": "crown"},
         "city": {"label": "Cities", "color": "c1", "icon": "star"},
         "wall": {"label": "Frontier works", "color": "c3", "icon": "flag"}}
def card(title, date, at, kind, text, src, art, **kw):
    d = {"title": title, "date": date, "at": at, "kind": kind, "text": text, "source": src, "url": W + art}
    d.update(kw); return d
NOTE = ("Event cards typed by Orbis. Dates: astronomical years (1 BC = 0); ancient dates before 45 BC follow the Roman "
        "tradition and are given as years only. Each card names its source (an ancient author and/or the Wikipedia article).")
def write(name, items, note=NOTE, moves=None):
    d = {"source": "editorial", "asOf": T, "retrieved": T, "note": note, "kinds": KINDS, "items": sorted(items, key=lambda e: e["date"] if not isinstance(e["date"], list) else e["date"][0])}
    if moves: d["moves"] = moves
    p = os.path.join(OUT, name); json.dump(d, open(p, "w"), ensure_ascii=False, indent=1); print(p, len(items))

RISE = [
 card("Rome is founded", -752, [12.49, 41.89], "city", "Roman tradition dated the founding of the city to 753 BC. The Roman way of counting years 'from the founding of the city' (ab urbe condita, AUC) starts here; the date itself is legend, not record.", "Varro's date, via Livy 1; Wikipedia 'Founding of Rome'", "Founding_of_Rome", circa=True),
 card("The Republic", -508, [12.49, 41.89], "rule", "Romans expelled their last king and began to elect two consuls each year. The year 509 BC is the traditional date.", "Livy 2.1; Wikipedia 'Roman Republic'", "Roman_Republic", circa=True),
 card("Gauls sack Rome", -389, [12.52, 42.05], "war", "A Gallic army beat the Romans at the Allia river and sacked the city. Livy dates it to 390 BC, Polybius to 387 BC.", "Livy 5.37–43; Wikipedia 'Battle of the Allia'", "Battle_of_the_Allia", date_text=None),
 card("First war with Carthage", [-263, -240], [15.55, 38.19], "war", "Rome and Carthage fought for 23 years over Sicily, mostly at sea. Rome won and made Sicily its first province outside Italy.", "Polybius 1; Wikipedia 'First Punic War'", "First_Punic_War"),
 card("Hannibal crosses the Alps", -217, [6.9, 45.2], "war", "Hannibal marched an army with war elephants from Carthago Nova in Spain over the Pyrenees and the Alps into Italy. The exact pass is still debated.", "Polybius 3; Wikipedia \"Hannibal's crossing of the Alps\"", "Hannibal%27s_crossing_of_the_Alps"),
 card("Cannae", -215, [16.13, 41.31], "war", "Hannibal encircled a much larger Roman army. Roman dead: about 48,000 according to Livy, 70,000 according to Polybius.", "Livy 22.49; Polybius 3.117; Wikipedia 'Battle of Cannae'", "Battle_of_Cannae"),
 card("Zama", -201, [9.29, 36.11], "war", "Scipio defeated Hannibal in Africa. Carthage gave up Spain and its fleet, and needed Rome's permission to wage war.", "Polybius 15; Wikipedia 'Battle of Zama'", "Battle_of_Zama"),
 card("Carthage destroyed", -145, [10.32, 36.85], "war", "After a three-year siege Rome razed Carthage and made its land the province of Africa. The same year Rome destroyed Corinth in Greece.", "Appian, Punica; Wikipedia 'Third Punic War'", "Third_Punic_War"),
 card("Pompey takes Syria", -63, [36.18, 36.22], "war", "Pompey ended the Seleucid kingdom and made Syria a Roman province.", "Wikipedia 'Roman Syria'", "Roman_Syria"),
 card("Caesar in Gaul", [-57, -49], [4.5, 47.54], "war", "Julius Caesar conquered Gaul in eight years of war; the siege of Alesia in 52 BC decided it.", "Caesar, Gallic War; Wikipedia 'Gallic Wars'", "Gallic_Wars"),
 card("Caesar murdered", -43, [12.48, 41.9], "rule", "Senators stabbed Caesar on the Ides of March, 44 BC, after he had made himself dictator for life.", "Suetonius, Divus Julius 82; Wikipedia 'Assassination of Julius Caesar'", "Assassination_of_Julius_Caesar"),
 card("Actium and Egypt", -30, [20.74, 38.95], "war", "Octavian's fleet beat Antony and Cleopatra at Actium. A year later Egypt became a Roman province.", "Plutarch, Antony; Wikipedia 'Battle of Actium'", "Battle_of_Actium"),
 card("Augustus, first emperor", -26, [12.49, 41.89], "rule", "The Senate gave Octavian the name Augustus in 27 BC. Historians count the Empire from here.", "Cassius Dio 53; Wikipedia 'Augustus'", "Augustus"),
 card("Teutoburg Forest", 9, [8.13, 52.41], "war", "Germanic tribes under Arminius destroyed three Roman legions. Rome gave up the land between the Rhine and the Elbe.", "Cassius Dio 56; Wikipedia 'Battle of the Teutoburg Forest'", "Battle_of_the_Teutoburg_Forest"),
 card("Britain invaded", 43, [1.07, 51.28], "war", "Claudius sent four legions across the Channel; southern Britain became a province.", "Cassius Dio 60; Wikipedia 'Roman conquest of Britain'", "Roman_conquest_of_Britain"),
 card("Dacia and Arabia", 106, [23.32, 45.67], "war", "Trajan conquered Dacia (today's Romania) and annexed the Nabataean kingdom as the province of Arabia.", "Wikipedia \"Trajan's Dacian Wars\"", "Trajan%27s_Dacian_Wars"),
 card("Trajan reaches the Gulf", [115, 116], [44.58, 33.09], "war", "Trajan took the Parthian capital Ctesiphon and reached the Persian Gulf. His successor Hadrian gave up Mesopotamia in 117.", "Cassius Dio 68; Wikipedia \"Trajan's Parthian campaign\"", "Trajan%27s_Parthian_campaign"),
]
for c in RISE: c.pop("date_text", None)

FRONT = [
 card("Hadrian's Wall", 122, [-2.3, 55.0], "wall", "Hadrian ordered a stone wall across northern Britain, 80 Roman miles (117 km) from the Tyne to the Solway, with a small fort every mile.", "Historia Augusta, Hadrian 11; Wikipedia \"Hadrian's Wall\"", "Hadrian%27s_Wall"),
 card("Antonine Wall", 142, [-4.0, 55.98], "wall", "Antoninus Pius moved the frontier north to a turf wall between the Forth and the Clyde. It was abandoned after about twenty years.", "Wikipedia 'Antonine Wall'", "Antonine_Wall"),
 card("The German limes", [100, 260], [9.0, 49.5], "wall", "A palisade, ditch and wall with forts and watchtowers ran about 550 km between the Rhine and the Danube. It was given up around 260.", "UNESCO 'Frontiers of the Roman Empire'; Wikipedia 'Limes Germanicus'", "Limes_Germanicus"),
 card("Fossatum Africae", [100, 200], [5.5, 35.0], "wall", "Ditches and walls along the edge of the Sahara controlled the movement of herders and traders; most scholars date them to the 2nd century.", "Wikipedia 'Fossatum Africae'", "Fossatum_Africae", circa=True),
 card("Marcomannic Wars", [166, 180], [16.37, 48.21], "war", "Germanic peoples crossed the Danube and reached northern Italy. Marcus Aurelius spent most of his last years fighting on the river.", "Cassius Dio 72; Wikipedia 'Marcomannic Wars'", "Marcomannic_Wars"),
 card("Citizens all", 212, [12.49, 41.89], "rule", "Caracalla made almost every free man in the empire a Roman citizen.", "Constitutio Antoniniana; Wikipedia 'Constitutio Antoniniana'", "Constitutio_Antoniniana"),
 card("An emperor captured", 260, [38.79, 37.16], "war", "The Persian king Shapur I captured the emperor Valerian near Edessa. In the same years breakaway states ruled the west (the Gallic Empire, 260–274) and, briefly, the east (Palmyra, 270–273).", "Shapur's inscription at Naqsh-e Rostam; Wikipedia 'Crisis of the Third Century'", "Crisis_of_the_Third_Century"),
 card("Dacia given up", [271, 275], [23.32, 45.67], "war", "Aurelian withdrew from Dacia north of the Danube, the first province Rome abandoned.", "Wikipedia 'Roman Dacia'", "Roman_Dacia"),
 card("Four emperors", 293, [29.92, 40.77], "rule", "Diocletian shared power with three co-emperors, each with his own capital: Nicomedia, Sirmium, Mediolanum and Augusta Treverorum.", "Wikipedia 'Tetrarchy'", "Tetrarchy"),
 card("Constantinople", 330, [28.97, 41.01], "city", "Constantine refounded Byzantium as his new capital and named it after himself, dedicating it on 11 May 330.", "Wikipedia 'Constantinople'", "Constantinople"),
 card("Adrianople", 378, [26.56, 41.68], "war", "Goths who had crossed the Danube destroyed an eastern Roman army and killed the emperor Valens.", "Ammianus Marcellinus 31; Wikipedia 'Battle of Adrianople'", "Battle_of_Adrianople"),
 card("Two empires", 395, [19.61, 44.97], "rule", "Theodosius I died in January 395. His sons split the empire: Arcadius ruled the east from Constantinople, Honorius the west from Mediolanum and later Ravenna.", "Wikipedia 'Theodosius I'", "Theodosius_I"),
]

FALL = [
 card("Adrianople", 378, [26.56, 41.68], "war", "Goths destroyed an eastern Roman army and killed the emperor Valens.", "Ammianus Marcellinus 31; Wikipedia 'Battle of Adrianople'", "Battle_of_Adrianople"),
 card("The Rhine crossing", 406, [8.27, 50.0], "war", "Vandals, Alans and Suebi crossed the Rhine near Mogontiacum (Mainz) at the end of 406 and moved on into Gaul and Spain.", "Wikipedia 'Crossing of the Rhine'", "Crossing_of_the_Rhine"),
 card("Rome sacked", 410, [12.49, 41.89], "war", "Alaric's Visigoths plundered Rome for three days, the first time in 800 years an enemy had taken the city.", "Wikipedia 'Sack of Rome (410)'", "Sack_of_Rome_(410)"),
 card("Vandals take Carthage", 439, [10.32, 36.85], "war", "The Vandals took Carthage and Rome's richest grain provinces in Africa.", "Wikipedia 'Vandal Kingdom'", "Vandal_Kingdom"),
 card("Attila stopped", 451, [4.4, 48.9], "war", "Romans and Visigoths fought Attila's Huns to a halt in Gaul at the Catalaunian Plains; the exact site is unknown.", "Jordanes, Getica; Wikipedia 'Battle of the Catalaunian Plains'", "Battle_of_the_Catalaunian_Plains"),
 card("The last western emperor", 476, [12.2, 44.42], "rule", "The general Odoacer deposed the boy emperor Romulus Augustulus at Ravenna and sent the imperial regalia to Constantinople.", "Wikipedia 'Romulus Augustulus'", "Romulus_Augustulus"),
 card("Justinian's wars", [533, 554], [12.2, 44.42], "war", "Belisarius retook Africa from the Vandals in 533–534; Italy followed after a 20-year war with the Ostrogoths, and part of southern Spain in 552.", "Procopius, Wars; Wikipedia 'Justinian I'", "Justinian_I"),
 card("Lombards in Italy", 568, [9.19, 45.46], "war", "The Lombards invaded Italy; Constantinople kept only Ravenna, Rome, the south and the islands.", "Wikipedia 'Lombards'", "Lombards"),
 card("Yarmouk", 636, [35.95, 32.8], "war", "Arab armies defeated the Romans in Syria. Within six years Syria, Palestine and Egypt were lost.", "Wikipedia 'Battle of the Yarmuk'", "Battle_of_the_Yarmuk"),
 card("Carthage falls", 698, [10.32, 36.85], "war", "The Umayyads took Carthage, ending Roman rule in Africa.", "Wikipedia 'Battle of Carthage (698)'", "Battle_of_Carthage_(698)"),
 card("A new western emperor", 800, [12.45, 41.9], "rule", "The pope crowned the Frankish king Charlemagne emperor in Rome. Constantinople did not recognise the title.", "Wikipedia 'Charlemagne'", "Charlemagne"),
 card("Manzikert", 1071, [42.53, 39.14], "war", "The Seljuk Turks defeated and captured the emperor Romanos IV; Anatolia lay open to Turkish settlement.", "Wikipedia 'Battle of Manzikert'", "Battle_of_Manzikert"),
 card("Crusaders take Constantinople", 1204, [28.97, 41.01], "war", "The Fourth Crusade sacked the city and set up a Latin Empire. Byzantine rulers won it back in 1261.", "Wikipedia 'Sack of Constantinople'", "Sack_of_Constantinople"),
 card("Constantinople falls", 1453, [28.97, 41.01], "war", "Mehmed II's Ottoman army took the city after a siege of 53 days, on 29 May 1453 by the Julian calendar then in use (7 June in today's calendar). The last emperor, Constantine XI, died in the fighting.", "Wikipedia 'Fall of Constantinople'", "Fall_of_Constantinople"),
 card("Trebizond", 1461, [39.72, 41.0], "war", "The Ottomans took Trebizond on the Black Sea, the last Greek state that claimed the Roman succession.", "Wikipedia 'Empire of Trebizond'", "Empire_of_Trebizond"),
]
# Hannibal's march, schematic: stages named by Polybius 3 (Carthago Nova, the Ebro, the Pyrenees, the Rhone, the Alps, the Po
# valley, the Trebia, Lake Trasimene, Cannae); the Alpine pass is unknown. Years only.
HANNIBAL = {"army": [{"name": "Hannibal", "color": "c3", "path": [[-0.99, 37.6, -217.8], [0.6, 40.7, -217.7], [2.6, 42.5, -217.6],
    [4.6, 43.9, -217.4], [6.9, 45.2, -217.3], [7.68, 45.07, -217.2], [9.6, 45.05, -217.1], [12.1, 43.18, -216.5], [16.13, 41.31, -215.4]]}]}
# (fractional years only order the stages within 218 BC; they are not dates)
write("rome-events-rise.json", RISE, moves=HANNIBAL)
write("rome-events-frontier.json", FRONT)
write("rome-events-fall.json", FALL)
