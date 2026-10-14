"""Build the six Roman history chapters from cited factual annotations.

Offline, deterministic. No boundary reconstruction is implied by event locations.
Optional --overlay creates the Mitchell 1880 reconstruction from a cached scan.
"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/history/rome'
OUT.mkdir(parents=True, exist_ok=True)
MET = 'https://www.metmuseum.org/essays/the-roman-empire-27-b-c-393-a-d'
REP = 'https://www.metmuseum.org/essays/the-roman-republic'
BYZ = 'https://www.metmuseum.org/essays/byzantium-ca-330-1453'
EH = 'https://www.english-heritage.org.uk/visit/places/hadrians-wall/hadrians-wall-history-and-stories/history/'
FRE = 'https://whc.unesco.org/en/list/430/'
DAN = 'https://whc.unesco.org/en/list/1608/'
POL = 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Polybius/'
APP = 'https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0230%3Atext%3DPun.%3Achapter%3D20%3Asection%3D133'
SITES = 'https://whc.unesco.org/en/list/91/'
PONT = 'https://whc.unesco.org/en/list/344/'
RAV = 'https://whc.unesco.org/en/list/788/'
ROME=[12.49,41.89]; CAR=[10.32,36.85]; CON=[28.98,41.01]
def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def ev(title, year, at, text, url, source, kind='event'):
    return dict(title=title,date=year,at=at,text=text,url=url,source=source,kind=kind)
def scene(title,text,center,zoom,items,years=None,extra=None):
    s=dict(title=title,text=text,view=dict(mode='globe',center=center,zoom=zoom),modernBorders=False,
        layers=[dict(type='cards',data='events',year='t',list=True,kinds=items)],sources=['editorial'])
    if years:s['timeline']=dict(years=years,start=years[-1],era=True,calendar='auc')
    if extra:s.update(extra)
    return s
def story(id,title,hook,events,scenes,notes='',places=None):
    kinds={e['kind']:dict(label=e['kind'].replace('_',' ').title(),color=['c2','c3','c4','c1','c5'][i%5]) for i,e in enumerate(events)}
    ds=dict(source='editorial',asOf='Historical synthesis, cutoff 2026-10-14',retrieved='2026-10-14',note='Original factual annotations. Event URLs cite dates and claims; coordinates locate the named place approximately, not battlefield boundaries. BC dates use astronomical years (1 BC = 0).',kinds=kinds,items=events)
    if places:ds['places']=places
    write(OUT/(id+'.json'),ds)
    st=dict(id=id,cat='People',title=title,hook=hook,updated='2026-10-14',notes='Historical locations are approximate city/site anchors, not surveyed battle sites or territorial polygons. No modern state is used as a proxy for Roman sovereignty. Events follow cited ancient accounts and institutional histories; ancient authors are not neutral eyewitnesses to every event. BC dates use astronomical years internally. '+notes,data=dict(events='data/history/rome/'+id+'.json'),sources=['editorial'],scenes=scenes)
    write(ROOT/'stories'/(id+'.json'),st)

events=[
ev('Two rivals',-263,ROME,'Rome and Carthage began their first war over Sicily in 264 BC.',POL+'1*.html','Polybius, Histories 1.10–12','rivals'),
ev('Carthage',-263,CAR,'Carthage was the African maritime power confronting Rome across the central Mediterranean.',POL+'1*.html','Polybius, Histories 1','rivals'),
ev('Sicily surrendered',-240,[12.43,37.8],'The peace of 241 BC required Carthage to withdraw from Sicily; this marker locates the island, not the treaty signing.',POL+'1*.html','Polybius, Histories 1.62–63','sicily'),
ev('Hannibal reaches Italy',-217,[7.7,45.0],'In 218 BC Hannibal crossed the Alps into Italy. This Po-valley anchor deliberately does not choose a disputed Alpine pass.',POL+'3*.html','Polybius, Histories 3.50–56','hannibal'),
ev('Cannae',-215,[16.13,41.31],'Hannibal defeated Roman armies at Cannae in 216 BC.',POL+'3*.html','Polybius, Histories 3.107–117','hannibal'),
ev('Zama region',-201,[9.2,36.1],'Scipio defeated Hannibal in 202 BC. Zama is located only at regional precision; the battlefield is debated.',POL+'15*.html','Polybius, Histories 15.5–16','africa'),
ev('Carthage destroyed',-145,CAR,'Roman forces destroyed Carthage in 146 BC; this was a later war, not the immediate outcome of Zama.',APP,'Appian, Punic Wars 127–135','africa')]
story('rome-carthage','Rome and Carthage','A struggle for Sicily became a contest across the western Mediterranean.',events,[
scene('Across the water','Italy and the African coast faced each other across Sicily. Polybius traces the first war to intervention on that island in 264 BC.',[12,38],3.5,['rivals','sicily'],[-263,-240]),
scene('The war moves north','Hannibal carried the next war from Iberia across the Alps into Italy in 218 BC. The map anchors his arrival in the Po valley and his victory at Cannae; it does not invent his disputed route.',[11,43],4,['hannibal'],[-217,-215]),
scene('The decision in Africa','At Zama in 202 BC, Scipio defeated Hannibal. Victory shifted the balance toward Rome, but Carthage survived the peace.',[10.4,36.8],7,['africa'],[-201,-145]),
scene('A city destroyed','In 146 BC another Roman army destroyed Carthage. Compare the African battle-region marker with the coastal city: conquest involved both armies in the field and the destruction of urban communities.',[10,36.7],6,['africa'])],notes='Polybius Histories 1, 3 and 15; Appian Punic Wars 127–135. These ancient narratives supply chronology. Zama and the Alpine crossing remain geographically uncertain.')

events=[ev('Republican Rome',-43,ROME,'Caesar was assassinated in Rome in 44 BC after civil wars and conquest.',REP,'Met, The Roman Republic','republic'),
ev('Augustus',-26,ROME,'Octavian received the title Augustus in 27 BC.',MET,'Met, The Roman Empire','augustus'),
ev('Britannia',43,[-0.13,51.51],'Permanent Roman conquest of Britain began in AD 43. Londinium is a regional anchor, not the landing site.',EH,'English Heritage, History of Hadrian’s Wall','britain'),
ev('Dacia',117,[23.31,45.62],'Trajan’s wars extended Roman power into Dacia. Sarmizegetusa locates the region; AD 117 is the end-of-reign snapshot, not its conquest date.',MET,'Met, The Roman Empire: Trajan','trajan'),
ev('Parthian campaign',117,[44.58,33.09],'Trajan also fought in Parthia. Ctesiphon anchors that eastern theatre; the marker is not a permanent-border claim.',MET,'Met, The Roman Empire: Trajan','trajan')]
story('rome-expansion','Growth by conquest','Republican conquest became imperial rule, then reached Britain and the eastern theatres.',events,[
scene('Conquest before emperors','The republic acquired territory by war and diplomacy. Its final civil wars culminated in Caesar’s dictatorship and assassination in 44 BC.',[12.5,41.9],5,['republic']),
scene('A new kind of ruler','In 27 BC Octavian became Augustus. Move the timeline from the republican crisis to imperial rule: power changed at Rome before the empire’s outer geography stopped changing.',[12.5,41.9],5,['republic','augustus'],[-43,-26]),
scene('Across a channel, beyond a river','Britain’s conquest began in AD 43. Under Trajan, war extended into Dacia and Parthia. These widely separated anchors show theatres of expansion rather than implying a continuous surveyed border.',[20,43],2.3,['britain','trajan'],[43,117]),
scene('How an atlas imagined the empire','Mitchell’s 1880 atlas reconstructed Rome at its greatest extent. The cleared historical overlay offers an empire-wide view; it is a nineteenth-century interpretation with approximate georeferencing, not an exact AD 117 boundary. Adjust its opacity to compare coastlines.',[19,40],2.5,[],extra={'layers':[{'type':'overlay','data':'atlas','opacity':0.8}],'sources':['rome-mitchell1880']})],notes='Met: The Roman Republic and The Roman Empire; English Heritage for AD 43. Historical geometry fallback: georeferenced Mitchell 1880 map, inset removed; its provincial divisions and colouring are retained as historical cartography, not authoritative boundaries. Credit: David Rumsey Map Collection, David Rumsey Map Center, Stanford Libraries. Adaptation CC BY-NC-SA 3.0.')
st=json.loads((ROOT/'stories/rome-expansion.json').read_text(encoding='utf-8'));st['data']['atlas']='data/history/rome/mitchell1880.json';write(ROOT/'stories/rome-expansion.json',st)

events=[ev('Hadrian’s Wall: west',122,[-3.22,54.95],'Bowness-on-Solway marks the western end of the wall begun after Hadrian’s visit in AD 122.',EH,'English Heritage','hadrian'),
ev('Hadrian’s Wall: east',122,[-1.53,54.99],'Wallsend marks the eastern end. Endpoint markers do not trace the wall’s surveyed course.',EH,'English Heritage','hadrian'),
ev('Antonine frontier',142,[-3.9,55.98],'In the 140s Rome pushed north to the Forth–Clyde isthmus. AD 142 is the conventional start date, not an instantaneous completed line.',FRE,'UNESCO, Frontiers of the Roman Empire','antonine'),
ev('Rhine frontier',150,[7.33,50.49],'Rheinbrohl anchors the northern end of the Upper German–Raetian frontier, built in stages during the second century. AD 150 is a period anchor.',FRE,'UNESCO, Frontiers of the Roman Empire','continental'),
ev('Danube frontier',150,[9.46,48.85],'Bad Gögging to Iža was a fortified river frontier; this point locates its western segment. AD 150 is a period anchor.',DAN,'UNESCO, Danube Limes','continental')]
# Correct the Danube anchor to Bad Gögging (not an unrelated location).
events[-1]['at']=[11.78,48.82]
story('rome-frontier','The frontier','Walls, rivers and forts made a frontier that moved and admitted traffic.',events,[
scene('A wall across Britain','Hadrian’s Wall crossed northern Britain from Wallsend to Bowness-on-Solway. Its endpoints show how a fortified zone joined the Tyne and Solway coasts; they do not mark today’s Scottish border.',[-2.3,55],12,['hadrian']),
scene('The frontier moves','The Antonine frontier shifted north to the Forth–Clyde isthmus in the 140s. It was later abandoned in favour of Hadrian’s Wall. Move the timeline to see the northern anchor appear; earlier markers remain as archaeological context.',[-3,55.5],9,['hadrian','antonine'],[122,142]),
scene('Continental frontiers','The Upper German–Raetian frontier joined the Rhine and Danube regions. Its second-century fortifications existed beside settlements and transport links, rather than a sealed national boundary.',[10,49],7,['continental']),
scene('A river system','Along the Danube, forts, towers, roads and patrol fleets worked together. The Bad Gögging anchor locates UNESCO’s western segment; it represents a river-frontier system, not a fabricated empire polygon.',[14,48],5,['continental'])],notes='English Heritage supplies wall history and endpoint names; UNESCO Frontiers of the Roman Empire and Danube Limes supply frontier context. AD 142 and AD 150 are conventional/period anchors as marked in cards, not precise construction dates.')

events=[ev('Shared government',293,[16.44,43.51],'Diocletian established the Tetrarchy in AD 293. Split locates his later palace, not the exact place this arrangement was proclaimed.',MET,'Met, The Roman Empire','tetrarchy'),
ev('Constantinople',330,CON,'Constantine founded his new capital at Byzantium in AD 330.',MET,'Met, The Roman Empire','capital'),
ev('Western court',395,ROME,'After Theodosius died in AD 395, his sons ruled western and eastern portions. Rome is a western urban anchor, not a claim that it was the sole court residence.',MET,'Met, The Roman Empire','division'),
ev('Eastern court',395,CON,'Arcadius ruled in the East after Theodosius’s death.',MET,'Met, The Roman Empire','division'),
ev('Ravenna',402,[12.2,44.42],'Ravenna became the seat of the Western Roman Empire in AD 402.',RAV,'UNESCO, Early Christian Monuments of Ravenna','ravenna')]
places=[dict(at=CON,names=[{'name':'Byzantium','from':None,'to':330},{'name':'Constantinople','from':330,'to':1453}])]
story('rome-split','East and West','Several courts governed one Roman world before its western and eastern paths diverged.',events,[
scene('Power shared','Diocletian’s Tetrarchy shared imperial authority from AD 293. His later palace at Split gives a geographic anchor for the ruler; multiple emperors did not mean modern nation-states.',[17,43],5,['tetrarchy']),
scene('Byzantium becomes Constantinople','Constantine’s capital stood on the Bosporus between Mediterranean and Black Sea routes. Move from AD 324 to AD 330 to watch the historical place-name change.',[29,41],7,['capital'],[324,330],extra={'layers':[dict(type='places',data='events',year='t',color='c3'),dict(type='cards',data='events',year='t',kinds=['capital'],list=True)]}),
scene('Two courts','After Theodosius’s death in AD 395, western and eastern government passed to different sons. The city markers locate the two political worlds; they do not draw an exact partition line.',[21,41],3,['division'],[330,395]),
scene('Ravenna and Constantinople','Ravenna became the western imperial seat in AD 402. Comparing it with Constantinople shows how Rome’s old centrality differed from the geography of late imperial government.',[21,43],3,['ravenna','capital'])],notes='Met, The Roman Empire (Tetrarchy, Constantine and Theodosius); UNESCO Ravenna for AD 402. Historical place-name change is tied to the AD 330 foundation; no claim of an instantaneous universal name replacement.',places=places)

events=[ev('Rome sacked',410,ROME,'Alaric’s forces sacked Rome in AD 410.',MET,'Met, The Roman Empire','west'),ev('Western deposition',476,[12.2,44.42],'Odoacer deposed Romulus Augustulus in AD 476. Ravenna locates the western court; this conventional endpoint did not end all Roman institutions.',MET,'Met, The Roman Empire; UNESCO Ravenna','west'),ev('Eastern survival',476,CON,'Constantinople remained the seat of Roman imperial government. Justinian’s sixth-century rule belongs to this continuing eastern history.',BYZ,'Met, Byzantium','east'),ev('Crusader conquest',1204,CON,'The Fourth Crusade captured Constantinople in 1204 and established a Latin empire.',BYZ,'Met, Byzantium','crusade'),ev('Imperial restoration',1261,CON,'Constantinople returned to Byzantine imperial rule in 1261.', 'https://www.metmuseum.org/exhibitions/listings/2004/byzantium-faith-and-power','Met, Byzantium: Faith and Power','restoration'),ev('Ottoman conquest',1453,CON,'The Ottoman conquest of Constantinople in 1453 ended its Byzantine imperial government.',BYZ,'Met, Byzantium','ottoman')]
story('rome-fall','The falls of Rome and Constantinople','AD 476 ended the western court; Constantinople followed a much longer, interrupted history.',events,[
scene('Rome is not the western court','Rome’s sack in AD 410 and the deposition at the western court in AD 476 were different events. Ravenna and Rome locate that distinction.',[12.4,43],7,['west'],[410,476]),
scene('The East continues','Imperial government persisted at Constantinople after AD 476. Its sixth-century world retained Roman law and classical culture alongside Christian imperial institutions.',[29,41],6,['east']),
scene('Conquest, then restoration','Constantinople fell to the Fourth Crusade in 1204; Byzantine imperial rule returned in 1261. Move the timeline to compare these changes at the same city.',[29,41],8,['crusade','restoration'],[1204,1261]),
scene('A different endpoint','In 1453 the Ottomans conquered Constantinople. The western deposition and eastern conquest were separated by centuries: one date cannot describe both histories.',[23,42],3,['west','ottoman'],[476,1453])],notes='Met Roman Empire for AD 410 and 476; Met Byzantium and Byzantium: Faith and Power for 1204, 1261 and 1453. AD 476 marks western deposition and eastern continuity, not a boundary snapshot. Western deposition is conventionally associated with Ravenna; Roman institutions survived it.')

events=[ev('Rome’s monuments',2026,ROME,'Forums, the Pantheon and imperial monuments remain embedded in Rome’s later city.',SITES,'UNESCO, Historic Centre of Rome','city'),ev('Pont du Gard',2026,[4.535,43.947],'The aqueduct bridge preserves Roman hydraulic construction; UNESCO’s detailed statement dates the aqueduct to the middle of the first century.',PONT,'UNESCO, Pont du Gard: Outstanding Universal Value','water'),ev('Hadrian’s Wall survives',2026,[-2.33,55.0],'Surviving wall, forts and civilian settlements make the frontier visible as archaeology.',FRE,'UNESCO, Frontiers of the Roman Empire','frontier'),ev('Ravenna’s mosaics',2026,[12.2,44.42],'Ravenna’s monuments preserve late Roman and Byzantine religious and artistic history.',RAV,'UNESCO, Early Christian Monuments of Ravenna','art'),ev('Constantinople’s inheritance',2026,CON,'The eastern Roman tradition forms part of Istanbul’s layered history; the city is not reduced to one ancient identity.',BYZ,'Met, Byzantium','east')]
story('rome-legacy','What remains','Infrastructure, city fabric and eastern Roman art survive in different forms and places.',events,[
scene('An ancient city inside a later one','Rome’s forums and imperial monuments sit within a city remade over centuries. The urban anchor shows persistence of place, not an unchanged population or government.',ROME,9,['city']),
scene('Water and settlement','Near Nîmes, the Pont du Gard still reveals how Roman builders carried water across a valley. This site is an infrastructure example, not a map of the entire aqueduct.',[4.54,43.95],10,['water']),
scene('A frontier becomes heritage','Hadrian’s Wall survives as forts, walls and settlements. Its archaeology preserves encounters at an imperial edge, including the communities who lived around the garrisons.',[-2.4,55],10,['frontier']),
scene('The eastern inheritance','Ravenna and Constantinople preserve different parts of late Roman and Byzantine history. Comparing the sites prevents the empire’s cultural legacy from being collapsed into Rome alone.',[21,43],3,['art','east'])],notes='Present-day site anchors, reviewed 2026-10-14. UNESCO Rome, Pont du Gard, Frontiers and Ravenna; Met Byzantium. No population, modern ancestry, or language distribution is inferred from these monuments. Pont du Gard’s detailed UNESCO statement and site institution take precedence over the inconsistent short UNESCO summary.')

if '--overlay' in sys.argv:
    import numpy as np
    from PIL import Image
    # Coordinates below refer to a 1400-pixel-wide preview, then scaled to the source.
    im=Image.open(ROOT/'.cache/roadmap-review/M3/mitchell1880.jpg').convert('RGBA')
    scale=im.width/1400
    # Identifiable coastal/city anchors. Only the main panel participates in the fit.
    g=np.array([[396,418,-.13,51.51],[184,693,-9.14,38.72],[254,758,-5.35,36.14],[588,635,12.49,41.89],[535,730,10.32,36.85],[788,607,28.98,41.01],[875,852,29.92,31.2],[790,758,25.13,35.34],[467,560,5.37,43.3],[922,750,32.88,34.69]],float)
    g[:,:2]*=scale
    def terms(x,y):return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],axis=-1)
    A=terms(g[:,2],g[:,3]);cx=np.linalg.lstsq(A,g[:,0],rcond=None)[0];cy=np.linalg.lstsq(A,g[:,1],rcond=None)[0]
    err=np.hypot(A@cx-g[:,0],A@cy-g[:,1])
    W=1400; bbox=[-12,27,48,59];H=round(W*32/60)
    X,Y=np.meshgrid(np.linspace(-12,48,W),np.linspace(59,27,H));T=terms(X,Y);px=T@cx;py=T@cy
    src=np.asarray(im);xi=np.rint(px).astype(int);yi=np.rint(py).astype(int)
    inside=(xi>=132*scale)&(xi<1300*scale)&(yi>=210*scale)&(yi<910*scale)
    inside &= ~((xi>=767*scale)&(yi<537*scale)) # remove unrelated Greek inset
    arr=src[np.clip(yi,0,im.height-1),np.clip(xi,0,im.width-1)].copy();arr[~inside]=0
    Image.fromarray(arr).save(OUT/'mitchell1880.webp',quality=65)
    meta=dict(source='rome-mitchell1880',title='Mitchell’s 1880 reconstruction (approximate)',asOf='1880 interpretation of greatest extent',retrieved='2026-10-14',image='data/history/rome/mitchell1880.webp',bbox=bbox,licence='CC BY-NC-SA 3.0',credit='David Rumsey Map Collection, David Rumsey Map Center, Stanford Libraries',url='https://www.davidrumsey.com/luna/servlet/detail/RUMSEY~8~1~30544~1140071',note='Main panel only; Greek inset masked. Second-order warp using ten approximate city/coast anchors. A nineteenth-century reconstruction, not a surveyed AD 117 border. Accuracy is suitable for overview only; coastlines do not align exactly.',fit=dict(order=2,gcps=10,meanErrorPx=round(float(err.mean()),1),maxErrorPx=round(float(err.max()),1)),gcps=g.tolist())
    write(OUT/'mitchell1880.json',meta)
    print('overlay fit:',meta['fit'],'bytes:',(OUT/'mitchell1880.webp').stat().st_size)
print('Built six Rome chapters and their sourced event datasets.')




