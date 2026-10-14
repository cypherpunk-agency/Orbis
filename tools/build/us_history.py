"""Rebuild nine US chapters from cited factual annotations. No downloaded prose or media.
Historical geometry fallback: located events and schematic waypoint movements.
Modern Natural Earth admin-1 outlines are explicitly identified as reference geometry.
Run: python tools/build/us_history.py
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2]
OUT=R/'data/history/usa'
OUT.mkdir(parents=True,exist_ok=True)
def write(p,o):
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
A='https://www.archives.gov/'
N='https://www.nps.gov/'
H='https://history.state.gov/milestones/'
S='https://www.senate.gov/states/'
V={'mode':'globe','center':[-98,39],'zoom':3.5}
COMMON='Original Orbis factual synthesis; linked federal records and historic-site accounts, checked 14 October 2026. Points locate places approximately, not territorial extents. Modern national/state outlines are reference geography, never reconstructed historical borders. No archival images or source prose redistributed.'
MAP_NAMES={
 'Jamestown: a river foothold':'Jamestown','Plymouth: an inhabited shore':'Plymouth',
 'A declaration in Philadelphia':'Philadelphia','Thirteen names, an international treaty':'Original states',
 'Louisiana: the Mississippi gateway':'New Orleans','Texas and the Mexican cession':'Santa Fe',
 'An agreement on Oregon':'Columbia mouth','Beyond the contiguous mainland':'Sitka / Alaska',
 'Removal from the Southeast':'Cherokee homeland area','A treaty without national consent':'New Echota',
 'Forced west in 1838–1839':'Departure: Tennessee','Allotment fragmented collective lands':'Washington',
 'Ratifying the original union':'Delaware','California: admission after acquisition':'California / Sacramento',
 'Alaska: purchase, territory, state':'Alaska / Juneau','Hawaii: the fiftieth state':'Hawaii / Honolulu',
 'State affiliation was not control':'State affiliations','War begins at a harbour fort':'Fort Sumter',
 'The border states complicate the split':'Missouri / St Louis','Emancipation had a geographic limit':'Washington',
 'Appomattox was one surrender':'Appomattox','Surveyed land, federal promises':'Homestead site / Nebraska',
 'A Nebraska homestead':'Beatrice','Two construction fronts meet':'Promontory Summit',
 'Chinese workers built the western connection':'Promontory Summit','Nineteenth-century Atlantic migration':'New York',
 'Ellis Island: the Atlantic gateway':'Ellis Island','Exclusion shaped the Pacific crossing':'San Francisco',
 'Angel Island: entry and detention':'Angel Island','New Jersey breaks a simple winner map':'New Jersey',
 'Districts inside statewide outlines':'Nebraska','1898: a Pacific expansion':'Manila / Philippines',
 'A Caribbean acquisition':'Puerto Rico','Hawaii: annexation before statehood':'Hawaii / Honolulu',
 '1949: an Atlantic alliance':'Washington / signing',
}
SUPPLEMENT={
 'us-colonies':[N+'jame/faqs.htm'],
 'us-expansion':[N+'sitk/learn/historyculture/voices_of_change.htm',A+'milestone-documents/check-for-the-purchase-of-alaska'],
 'us-indigenous-land':['https://www.cherokee.gov/about-the-nation/remember-the-removal/our-journey/'],
 'us-civil-war':[N+'civilwar/facts.htm',N+'apco/learn/historyculture/surrender-events-after-appomattox.htm'],
 'us-frontier':[N+'im/ncpn/bpd-gosp.htm'],
}
def chapter(id,title,hook,rows,extras=None):
 # Each row: heading, text, approximate point, event year/date, citation URL, camera.
 items=[];scenes=[]
 for i,(heading,text,at,date,url,view) in enumerate(rows):
  kind=str(i)
  items.append({'title':MAP_NAMES.get(heading,heading),'text':text,'at':at,'date':date,'kind':kind,'source':'Federal record / historic-site account','url':url})
  scenes.append({'title':heading,'text':text,'view':view or V,'layers':[{'type':'cards','data':'history','year':date,'kinds':[kind],'list':True}], 'sources':['editorial']})
 data={'source':'editorial','asOf':'2026-10-14','retrieved':'2026-10-14','note':COMMON,'kinds':{str(i):{'label':row[0],'color':['c1','c2','c3','c4','c5'][i%5]} for i,row in enumerate(rows)},'items':items}
 st={'id':id,'cat':'Geopolitics','title':title,'hook':hook,'updated':'2026-10-14','notes':COMMON+' Sources by scene: '+ '; '.join(row[0]+': '+row[4] for row in rows), 'data':{'history':f'data/history/usa/{id}.json'},'sources':['editorial','naturalearth'],'scenes':scenes}
 if id in SUPPLEMENT:st['notes']+=' Supplementary date/location evidence: '+'; '.join(SUPPLEMENT[id])+'.'
 if extras:extras(st,data)
 write(OUT/(id+'.json'),data);write(R/'stories'/(id+'.json'),st)
 return st,data
east={'mode':'globe','center':[-76,38],'zoom':5}
def colonies(st,d):
 original='NH MA RI CT NY NJ PA DE MD VA NC SC GA'.split()
 d['sets']={'original':{'label':'Original states on modern outlines','values':{'US-'+x:'original' for x in original},'labels':{'original':'Original state (modern outline)'}}}
 st['scenes'][3]['layers'].append({'type':'categories','data':'history','set':'original','country':'USA','colors':{'original':'c4'}})
 st['scenes'][3]['text']+=' The coloured shapes locate their modern successor states; colonial claims extended beyond these outlines.'
chapter('us-colonies','Thirteen colonies','An Atlantic strip becomes an independent union.',[
 ('Jamestown: a river foothold','English settlers established Jamestown in 1607 on the James River, within Powhatan country. Its coastal location connected the settlement to Atlantic shipping.',[-76.76,37.21],1607,N+'jame/learn/historyculture/a-short-history-of-jamestown.htm',east),
 ('Plymouth: an inhabited shore','The land that became Plymouth Colony was Wampanoag land. The point locates Plymouth rather than outlining either Indigenous territory or a colonial claim.',[-70.67,41.96],1620,N+'rowi/learn/historyculture/wampanoag.htm',east),
 ('A declaration in Philadelphia','In 1776 the Declaration of Independence announced separation from Britain. Philadelphia is the location of the congressional decision, not a frontier between armies.',[-75.15,39.95],1776,A+'founding-docs/declaration',east),
 ('Thirteen names, an international treaty','The Treaty of Paris of 1783 named the thirteen states and recognised US independence. British recognition was a diplomatic act; it did not obtain Indigenous consent to the treaty’s western claims.',[-74,40],1783,A+'milestone-documents/treaty-of-paris',east),
],colonies)
def expansion(st,d):
 path=[[-90.48,38.81,18040516],[-92.57,38.98,18040607],[-111.5,45.92,18050725],[-124.06,46.28,18051115]]
 d['moves']={'expedition':[{'name':'Lewis & Clark (schematic)','path':path,'color':'c3','source':N+'subjects/travellewisandclark/expedition-by-date.htm','sources':[N+'subjects/travellewisandclark/expedition-by-date.htm',N+'places/st-charles-historic-district.htm']}]}
 d['note']+=' St Charles: 16 May 1804, direct Clark journal quotation on '+N+'places/st-charles-historic-district.htm preferred over contradictory May 14 summary/chronology.'
 sc=st['scenes'][1];sc['timeline']={'years':[p[2] for p in path],'format':'date','start':18051115};sc['layers']=[{'type':'moves','data':'history','set':'expedition','year':'t','labels':True}]
 st['notes']+=' Movement stops/dates: '+N+'subjects/travellewisandclark/expedition-by-date.htm. Connecting segments are schematic, not surveyed trails; marker position between dated stops is interpolated.'
 st['notes']+=' St Charles arrival uses 16 May 1804 from Clark’s journal quoted at '+N+'places/st-charles-historic-district.htm ; this detailed source conflicts with its own May 14 summary and the short expedition chronology. The journal quotation is preferred for this waypoint.'
chapter('us-expansion','Territorial expansion','Purchases, treaties and war moved US claims west.',[
 ('Louisiana: the Mississippi gateway','The Louisiana Purchase treaty was signed in 1803. New Orleans locates the river port central to negotiations; this point does not stand for the purchase’s boundaries.',[-90.07,29.95],1803,A+'milestone-documents/louisiana-purchase-treaty',None),
 ('Across the continent','Lewis and Clark travelled west in 1804–1805. Move the dated slider through selected NPS-documented stops: St Charles, Rocheport, Three Forks and Cape Disappointment. The connecting route is schematic.',[-90.48,38.81],1805,N+'subjects/travellewisandclark/expedition-by-date.htm',None),
 ('Texas and the Mexican cession','Texas entered the United States in 1845. The war with Mexico ended with the 1848 Treaty of Guadalupe Hidalgo and a major territorial cession; Santa Fe locates one affected region, not the whole cession.',[-105.94,35.69],1848,H+'1830-1860/texas-annexation',None),
 ('An agreement on Oregon','The Oregon Treaty of 1846 divided competing British and US claims in the Pacific Northwest. The point locates the Columbia mouth; it is not a treaty boundary.',[-124,46.25],1846,H+'1830-1860/oregon-territory',None),
 ('Beyond the contiguous mainland','The United States purchased Alaska from Russia in 1867. The acquisition preceded statehood by decades and did not mean that Alaska Native peoples had sold their own rights.',[-135.33,57.05],1867,H+'1866-1898/alaska-purchase',{'mode':'globe','center':[-147,58],'zoom':3}),
],expansion)
chapter('us-indigenous-land','Indigenous land loss','Treaties, forced removal and allotment changed landholding.',[
 ('Removal from the Southeast','Congress passed the Indian Removal Act in 1830. The NPS describes forced displacement from southeastern homelands to land west of the Mississippi; this chapter locates events instead of inventing a continental land-loss surface.',[-84.9,34.5],1830,N+'trte/learn/historyculture/index.htm',{'mode':'globe','center':[-88,36],'zoom':4}),
 ('A treaty without national consent','The Treaty of New Echota of 1835 ceded Cherokee lands east of the Mississippi. The NPS explains that the signatories did not represent the Cherokee national government and that many Cherokee protested.',[-84.91,34.51],1835,N+'articles/trailoftears.htm',{'mode':'globe','center':[-85,35],'zoom':5}),
 ('Forced west in 1838–1839','Federal troops and militia expelled Cherokee people in 1838. Detachments used several routes; the forced relocation ended in 1839. The two points locate a departure area and Indian Territory, not a single precise trail.',[-85.07,35.14],1839,N+'trte/learn/historyculture/index.htm',{'mode':'globe','center':[-90,36],'zoom':4}),
 ('Allotment fragmented collective lands','The Dawes Act of 1887 authorised reservation land allotment to individuals. Its assimilation policy weakened collective landholding; the Washington point locates the federal law, not a reservation or a quantified area lost.',[-77.01,38.89],1887,A+'milestone-documents/dawes-act',None),
],lambda st,d:(st['scenes'][2].update(points=[{'at':[-94.97,35.91],'label':'Tahlequah','color':'c2','r':5}]),st['scenes'][3].update(view=east)))
chapter('us-statehood','Becoming states','Acquisition and admission are different dates.',[
 ('Ratifying the original union','Delaware ratified the Constitution in 1787. Its position as the first state reflects ratification order; the state already existed before that constitutional decision.',[-75.53,39.16],1787,S+'DE/intro.htm',east),
 ('California: admission after acquisition','California became a state in 1850, after the Mexican cession of 1848. Admission brought representation in the federal union rather than a new international acquisition.',[-121.49,38.58],1850,S+'CA/intro.htm',{'mode':'globe','center':[-119,37],'zoom':4}),
 ('Alaska: purchase, territory, state','Alaska joined the union in January 1959. The gap from the 1867 purchase shows why an acquisition map and a statehood map answer different questions.',[-134.42,58.3],1959,S+'AK/intro.htm',{'mode':'globe','center':[-145,60],'zoom':3}),
 ('Hawaii: the fiftieth state','Hawaii became a state in August 1959. Its island geography places part of the union far beyond the contiguous mainland.',[-157.86,21.31],1959,S+'HI/intro.htm',{'mode':'globe','center':[-157,25],'zoom':3}),
])
def war(st,d):
 conf='SC MS FL AL GA LA TX VA AR NC TN'.split();border='DE MD KY MO'.split();union='CA CT IL IN IA ME MA MI MN NH NJ NY OH OR PA RI VT WI KS'.split()
 vals={**{'US-'+x:'confederacy' for x in conf},**{'US-'+x:'border' for x in border},**{'US-'+x:'union' for x in union}}
 d['sets']={'war':{'label':'State affiliations, late 1861','values':vals,'labels':{'confederacy':'Seceded states','border':'Slave states remaining in Union','union':'Other Union states'}}}
 st['scenes'][0]['layers']=[{'type':'categories','data':'history','set':'war','country':'USA','colors':{'confederacy':'c2','border':'c3','union':'c1'}}]
 st['scenes'][0]['view']={'mode':'globe','center':[-99,39],'zoom':2.7}
 st['notes']+=' Affiliations follow NPS Civil War facts and Border States; modern outlines are reference geometry. West Virginia is omitted because it was part of Virginia in 1861. Affiliations are not military-control polygons; Kentucky and Missouri had rival Confederate governments.'
chapter('us-civil-war','The Civil War split','Secession, slavery and military geography divided the union.',[
 ('State affiliation was not control','Slavery was central to secession. This late-1861 affiliation map uses modern state outlines; it does not map occupation or unanimity. West Virginia is omitted because it was then part of Virginia.',[-77,38],1861,N+'anti/learn/historyculture/roadtoseccession.htm',None),
 ('War begins at a harbour fort','Confederate forces opened fire on Fort Sumter on 12 April 1861. Charleston Harbour locates the attack that began the war; the point does not describe the later Union blockade.',[-79.87,32.75],18610412,N+'civilwar/search-battles-detail.htm?battleCode=SC001',{'mode':'globe','center':[-80,33],'zoom':6}),
 ('The border states complicate the split','Delaware, Maryland, Kentucky and Missouri retained slavery while remaining in the Union. Rival loyalties and fighting inside these states make a simple North–South colour divide misleading.',[-90.2,38.63],1861,N+'articles/the-border-states.htm',None),
 ('Emancipation had a geographic limit','The Emancipation Proclamation of 1863 applied to areas in rebellion, with specified exemptions. It did not itself abolish slavery everywhere in the United States; Washington locates the issuing government.',[-77.04,38.9],1863,A+'milestone-documents/emancipation-proclamation',east),
 ('Appomattox was one surrender','Lee surrendered the Army of Northern Virginia at Appomattox on 9 April 1865. The surrender was a major endpoint, but other Confederate armies surrendered later.',[-78.8,37.38],18650409,N+'appomattoxcourthouse',east),
],war)
chapter('us-frontier','Railroads and the frontier','Infrastructure and federal land policy transformed the West.',[
 ('Surveyed land, federal promises','The Homestead Act of 1862 offered qualifying settlers surveyed public land subject to residence and cultivation. Calling it public land reflected US law, not the absence of Indigenous societies.',[-96.82,40.29],1862,A+'milestone-documents/homestead-act',None),
 ('A Nebraska homestead','Daniel Freeman filed a claim in 1863 and settled near Beatrice, Nebraska. This located example shows the land policy at farm scale; it is not a map of all homestead claims.',[-96.82,40.29],1863,N+'articles/homestead-national-historical-park-s-landscape.htm',{'mode':'globe','center':[-98,40],'zoom':5}),
 ('Two construction fronts meet','The Central Pacific and Union Pacific met at Promontory Summit in May 1869. The labelled points locate the meeting and the two construction approaches; any connecting lines are schematic, not surveyed railway geometry.',[-112.55,41.62],1869,N+'gosp/learn/historyculture/a-moment-in-time.htm',None),
 ('Chinese workers built the western connection','Chinese workers were essential to Central Pacific construction and placed the final rail at Promontory on 10 May 1869. Their work belongs in the story of infrastructure as well as immigration.',[-112.55,41.62],18690510,N+'gosp/learn/historyculture/chinese-labor-and-the-iron-road.htm',{'mode':'globe','center':[-116,40],'zoom':4}),
],lambda st,d:st['scenes'][2].update(points=[{'at':[-121.49,38.58],'label':'Sacramento / Central Pacific','color':'c1'},{'at':[-95.94,41.26],'label':'Omaha / Union Pacific','color':'c2'}]))
chapter('us-immigration','Immigration waves','Atlantic and Pacific gateways reveal unequal access.',[
 ('Nineteenth-century Atlantic migration','Germany, Ireland and England were major sources of immigrants during the nineteenth century. The highlighted origin countries identify places described by the Library of Congress, without inventing counts or exact ship routes.',[-74.04,40.69],1880,'https://www.loc.gov/classroom-materials/united-states-history-primary-source-timeline/rise-of-industrial-america-1876-1900/immigration-to-united-states-1851-1900/',{'mode':'globe','center':[-35,45],'zoom':2}),
 ('Ellis Island: the Atlantic gateway','Ellis Island inspected immigrants entering through New York from 1892 to 1954. The island locates an inspection station; it cannot represent all arrivals or all immigrants’ final destinations.',[-74.04,40.7],1892,A+'dc/highlights/ellis-island-report',{'mode':'globe','center':[-74,40],'zoom':6}),
 ('Exclusion shaped the Pacific crossing','The Chinese Exclusion Act of 1882 barred Chinese labour immigration. The San Francisco point locates the Pacific gateway affected by federal exclusion, not the location where Congress enacted the law.',[-122.42,37.77],1882,A+'milestone-documents/chinese-exclusion-act',{'mode':'globe','center':[-155,35],'zoom':2}),
 ('Angel Island: entry and detention','Angel Island operated as an immigration station from 1910 to 1940. Many arrivals faced detention and interrogation; this Pacific history complicates a single story of welcome through New York.',[-122.43,37.87],1910,N+'places/u-s-immigration-station-angel-island.htm',{'mode':'globe','center':[-122,38],'zoom':6}),
],lambda st,d:(st['scenes'][0].update(fills={'DEU':'c1','IRL':'c3','GBR':'c4'}),st['scenes'][2].update(view={'mode':'globe','center':[-140,35],'zoom':2})))
def elections(st,d):
 lin='CA CT IL IN IA ME MA MI MN NH NY OH OR PA RI VT WI'.split();bre='AL AR DE FL GA LA MD MS NC SC TX'.split();bell='KY TN VA'.split()
 biden='AZ CA CO CT DE DC GA HI IL ME MD MA MI MN NV NH NJ NM NY OR PA RI VT VA WA WI'.split()
 allstates=[g['id'] for g in json.loads((R/'data/geo/admin1/USA.json').read_text())['objects']['regions']['geometries']]
 y1860={**{'US-'+x:'Lincoln' for x in lin},**{'US-'+x:'Breckinridge' for x in bre},**{'US-'+x:'Bell' for x in bell},'US-MO':'Douglas','US-NJ':'split'}
 y2020={x:('Biden' if x[3:] in biden else 'Trump') for x in allstates};y2020.update({'US-ME':'split','US-NE':'split'})
 d['sets']={'elections':{'label':'Certified electoral allocations','byYear':{'1860':y1860,'2020':y2020},'labels':{'split':'Split electors (see notes)'}}}
 colors={'Lincoln':'c1','Breckinridge':'c2','Bell':'c3','Douglas':'c4','split':'c5','Biden':'c1','Trump':'c2'}
 for sc,y in [(st['scenes'][0],1860),(st['scenes'][2],2020)]:
  sc['layers']=[{'type':'categories','data':'history','set':'elections','country':'USA','year':y,'colors':colors}]
  sc['view']={'mode':'globe','center':[-99,39],'zoom':2.7}
 st['scenes'][3]['points']=[{'at':[-69,45],'label':'Maine','color':'c5','r':5}]
 st['scenes'][3]['view']={'mode':'globe','center':[-90,42],'zoom':2.7}
 st['scenes'].append({'title':'The two noncontiguous states','text':'In the certified 2020 allocation, Alaska cast its electoral votes for Trump and Hawaii for Biden. Their distant geography belongs to the electoral map even though a continental camera cannot show every state at once. Source: National Archives 2020 results.', 'view':{'mode':'globe','center':[-150,42],'zoom':2.6},'layers':[{'type':'categories','data':'history','set':'elections','country':'USA','year':2020,'colors':colors}],'points':[{'at':[-149,64],'label':'Alaska','color':'c2','r':4},{'at':[-157.86,21.31],'label':'Hawaii','color':'c1','r':4}],'sources':['editorial','naturalearth']})
 st['notes']+=' Map encodes certified electoral allocation, not popular-vote share. 1860 New Jersey split Lincoln/Douglas; 2020 Maine split Biden/Trump 3/1, Nebraska 1/4. DC is shown in 2020. Neutral 1860 shapes are not-yet-admitted states; Maine, Virginia and other modern outlines differ from historical geography. Blank area is not a vote category.'
chapter('us-elections','The electoral map','Electoral allocations do not measure the popular vote.',[
 ('1860: four candidates, a sectional map','The National Archives records electoral votes for Lincoln, Douglas, Breckinridge and Bell. New Jersey split its electors. Colours show certified allocations on modern reference outlines, not vote shares or exact 1860 boundaries.',[-98,39],1860,A+'electoral-college/1860',None),
 ('New Jersey breaks a simple winner map','In 1860 New Jersey appointed electors individually. Lincoln received four of its electoral votes and Douglas three; assigning the state entirely to either candidate would erase the split.',[-74.5,40],1860,A+'electoral-college/1860',east),
 ('2020: two tickets, two split states','The certified 2020 Electoral College result was Biden 306, Trump 232. Maine and Nebraska split their allocations, so the purple category distinguishes them from states assigning all electors to one ticket.',[-98,39],2020,A+'electoral-college/2020',None),
 ('Districts inside statewide outlines','Maine allocated three votes to Biden and one to Trump; Nebraska allocated one to Biden and four to Trump. These points locate the states. This chapter does not invent district boundaries or imply proportional popular-vote representation.',[-99,41.5],2020,A+'electoral-college/2020',None),
],elections)
chapter('us-abroad','America abroad','From overseas acquisition to an Atlantic alliance.',[
 ('1898: a Pacific expansion','The 1898 war with Spain led to the cession of Guam and the Philippines to the United States. The points locate the islands; they do not imply those places retained identical political status afterward.',[121,14.6],1898,H+'1866-1898/spanish-american-war',{'mode':'globe','center':[145,20],'zoom':2}),
 ('A Caribbean acquisition','Spain also ceded Puerto Rico after the 1898 war. Cuba’s status followed a different path; it was not annexed by the United States under the peace treaty.',[-66.1,18.46],1898,H+'1866-1898/spanish-american-war',{'mode':'globe','center':[-75,21],'zoom':4}),
 ('Hawaii: annexation before statehood','The United States annexed Hawaii in 1898, following the overthrow of Queen Liliuokalani in 1893. It became a state only in 1959; acquisition and admission are separate historical changes.',[-157.86,21.31],1898,H+'1866-1898/spanish-american-war',{'mode':'globe','center':[-157,25],'zoom':3}),
 ('1949: an Atlantic alliance','The North Atlantic Treaty was signed in Washington in 1949. The alliance linked the United States and Canada with European partners. The map locates the signing and the Atlantic relationship, not a current map of military bases.',[-77.04,38.9],1949,H+'1945-1952/nato',{'mode':'globe','center':[-35,45],'zoom':2}),
],lambda st,d:(st['scenes'][0].update(points=[{'at':[144.8,13.45],'label':'Guam','color':'c3'}]),st['scenes'][3].update(fills={'USA':'c1','CAN':'c1','GBR':'c4','FRA':'c4'})))
print('Built nine chapters in data/history/usa and stories/us-*.json')
