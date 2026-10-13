// ---------- shared reference data ----------
const AFRICA = "DZA AGO BEN BWA BFA BDI CMR CAF TCD COD COG CIV DJI EGY GNQ ERI SWZ ETH GAB GMB GHA GIN GNB KEN LSO LBR LBY MDG MWI MLI MRT MAR MOZ NAM NER NGA RWA SEN SLE SOM SOL ZAF SSD SDN TZA TGO TUN UGA ESH ZMB ZWE".split(" ");
const EU27 = "AUT BEL BGR HRV CYP CZE DNK EST FIN FRA DEU GRC HUN IRL ITA LVA LTU LUX NLD POL PRT ROU SVK SVN ESP SWE".split(" ");
const SSA = AFRICA.filter(c => !["DZA","EGY","LBY","MAR","TUN","ESH"].includes(c));

const NATO_JOIN = {USA:1949,CAN:1949,GBR:1949,FRA:1949,BEL:1949,NLD:1949,LUX:1949,NOR:1949,DNK:1949,ISL:1949,ITA:1949,PRT:1949,
  GRC:1952,TUR:1952,DEU:1955,ESP:1982,CZE:1999,HUN:1999,POL:1999,BGR:2004,EST:2004,LVA:2004,LTU:2004,ROU:2004,SVK:2004,SVN:2004,
  ALB:2009,HRV:2009,MNE:2017,MKD:2020,FIN:2023,SWE:2024};
// Warsaw Pact 1955–1991. Soviet republics shown as today's states; East Germany cannot be split from today's Germany at this scale.
const WARSAW = {RUS:[1955,1991],UKR:[1955,1991],BLR:[1955,1991],EST:[1955,1991],LVA:[1955,1991],LTU:[1955,1991],MDA:[1955,1991],
  GEO:[1955,1991],ARM:[1955,1991],AZE:[1955,1991],KAZ:[1955,1991],UZB:[1955,1991],TKM:[1955,1991],KGZ:[1955,1991],TJK:[1955,1991],
  POL:[1955,1991],CZE:[1955,1991],SVK:[1955,1991],HUN:[1955,1991],ROU:[1955,1991],BGR:[1955,1991],ALB:[1955,1968]};
const EU_JOIN = {BEL:1958,FRA:1958,DEU:1958,ITA:1958,LUX:1958,NLD:1958,DNK:1973,IRL:1973,GBR:1973,GRC:1981,PRT:1986,ESP:1986,
  AUT:1995,FIN:1995,SWE:1995,CYP:2004,CZE:2004,EST:2004,HUN:2004,LVA:2004,LTU:2004,POL:2004,SVK:2004,SVN:2004,BGR:2007,ROU:2007,HRV:2013};
const BRICS_JOIN = {BRA:2009,RUS:2009,IND:2009,CHN:2009,ZAF:2011,EGY:2024,ETH:2024,IRN:2024,ARE:2024,IDN:2025};
const range = (a,b,s=1)=>{const r=[];for(let i=a;i<=b;i+=s)r.push(i);return r;};

// Current memberships for the explore mode
const BLOCS = {
  EU: {label:"European Union", ids:EU27},
  NATO: {label:"NATO", ids:Object.keys(NATO_JOIN)},
  BRICS: {label:"BRICS", ids:Object.keys(BRICS_JOIN)},
  G7: {label:"G7", ids:"USA CAN GBR FRA DEU ITA JPN".split(" ")},
  ASEAN: {label:"ASEAN", ids:"BRN KHM IDN LAO MYS MMR PHL THA VNM TLS".split(" ")},
  OPEC: {label:"OPEC", ids:"DZA COG GNQ GAB IRN IRQ KWT LBY NGA SAU ARE VEN".split(" ")},
  AU: {label:"African Union", ids:AFRICA.filter(c=>c!=="SOL")}
};

// Places
const P = {
  vienna:[16.37,48.21], tokyo:[139.69,35.69], nyc:[-74.0,40.71], singapore:[103.82,1.35], frankfurt:[8.68,50.11], la:[-118.24,34.05],
  rotterdam:[4.48,51.92], yokohama:[139.64,35.44], shanghai:[121.47,31.23], baumgarten:[16.87,48.31]
};
const SUEZ_ROUTE = [[121.5,31.0],[118,22],[110,10],[104.5,1.6],[100.5,3.5],[95,6],[80,5.5],[60,12.5],[50,12.8],[43.4,12.6],[38.5,20.5],[33.5,27.5],[32.5,30.2],[32.3,31.4],[25,34],[12,37.3],[0,37],[-5.6,35.95],[-9.6,38],[-9.8,43],[-5.5,48.6],[1.5,50.6],[4.0,52.0]];
const SUEZ_YOKO = [[139.7,35.2],[132,31],[125,28],[118,22]].concat(SUEZ_ROUTE.slice(2));
const CAPE_ROUTE = [[121.5,31.0],[118,22],[110,10],[104.5,1.6],[100.5,3.5],[95,6],[80,5.5],[65,-5],[48,-28],[35,-36.5],[18.5,-35.2],[8,-25],[0,-8],[-12,5],[-19,15],[-19,28],[-12,38],[-9.8,43],[-5.5,48.6],[1.5,50.6],[4.0,52.0]];

// ---------- stories ----------
const STORIES = [

// ===== STATISTICS =====
{
  id:"map-lies", cat:"Statistics", title:"The map lies",
  hook:"Greenland looks as big as Africa. It's fourteen times smaller.",
  notes:"Areas: Africa ≈ 30.4 million km², Greenland ≈ 2.2 million km², USA ≈ 9.8, China ≈ 9.6, India ≈ 3.3, EU ≈ 4.2 million km². Mercator shown clipped at 85° latitude, as web maps do.",
  scenes:[
    {title:"The map you grew up with", text:"This is the Mercator projection, the map on classroom walls and in most web maps. Look at Greenland and Africa: they seem about the same size.",
      view:{mode:"mercator", center:[0,20], zoom:1}, fills:Object.assign({GRL:"c2"}, Object.fromEntries(AFRICA.map(c=>[c,"c4"]))),
      legend:[{color:"c2",label:"Greenland"},{color:"c4",label:"Africa"}]},
    {title:"Why it happens", text:"Mercator keeps angles true, which made it perfect for sailors with compasses. The price: everything gets stretched the further it sits from the equator. Near the poles, the stretch becomes enormous.",
      view:{mode:"mercator", center:[-30,55], zoom:1.6}, fills:{GRL:"c2"}, highlight:["GRL"]},
    {title:"Now on a globe", text:"A globe has no stretch at all. Here Greenland shows its true size: big, but nowhere near a continent.",
      view:{mode:"globe", center:[-40,68], zoom:1.1}, fills:{GRL:"c2"}, highlight:["GRL"]},
    {title:"And Africa", text:"Africa covers about 30 million km². Greenland covers about 2.2 million. Africa is roughly fourteen times larger.",
      view:{mode:"globe", center:[18,4], zoom:1}, fills:Object.fromEntries(AFRICA.map(c=>[c,"c4"])) },
    {title:"Africa holds a lot", text:"The USA, China, India and the whole European Union together cover about 27 million km². All of them would fit inside Africa, with room to spare. This flat map uses an equal-area projection, so sizes are honest.",
      view:{mode:"equal", center:[30,10], zoom:1}, fills:Object.assign(Object.fromEntries(AFRICA.map(c=>[c,"c4"])), {USA:"c1",CHN:"c3",IND:"c2"}, Object.fromEntries(EU27.map(c=>[c,"c5"]))),
      legend:[{color:"c4",label:"Africa ≈ 30.4M km²"},{color:"c1",label:"USA ≈ 9.8M"},{color:"c3",label:"China ≈ 9.6M"},{color:"c2",label:"India ≈ 3.3M"},{color:"c5",label:"EU ≈ 4.2M"}]}
  ]
},
{
  id:"circle", cat:"Statistics", title:"Half the world in one circle",
  hook:"More people live inside this circle than outside it.",
  notes:"Circle after Danny Quah (2015), refining a 2013 observation by Reddit user valeriepieris: radius ≈ 3,300 km, centred near Mong Khet, Myanmar. Population figures ≈ 2025, UN World Population Prospects 2024, rounded.",
  scenes:[
    {title:"Draw a circle here", text:"Centre it in northern Myanmar and give it a radius of about 3,300 km. Inside: India, Bangladesh, most of China and Pakistan, and nearly all of Southeast Asia. More than half of all humans. Japan is just outside.",
      view:{mode:"globe", center:[100,22], zoom:1.05},
      circles:[{center:[99.9,21.3], km:3300, color:"c2", label:"≈ 50%+ of humanity"}]},
    {title:"Where people actually are", text:"Population by country. Two countries, India and China, have about 1.4 billion people each. Together they hold more than a third of the world.",
      view:{mode:"equal", center:[20,15], zoom:1}, choro:{data:"POP", title:"Population, millions (≈ 2025)", log:true, fmt:v=>d3.format(",")(Math.round(v))+" M"}},
    {title:"The empty side", text:"Turn the globe around and you find a hemisphere that is almost entirely water. Fewer than one in twenty people live on this side of the planet.",
      view:{mode:"globe", center:[-160,-15], zoom:1}, circles:[{center:[99.9,21.3], km:3300, color:"c2"}]},
    {title:"Population on the globe", text:"The same numbers on a sphere. Africa is the fastest-growing region: Nigeria alone has about 240 million people today.",
      view:{mode:"globe", center:[30,15], zoom:1}, choro:{data:"POP", title:"Population, millions (≈ 2025)", log:true, fmt:v=>d3.format(",")(Math.round(v))+" M"}}
  ]
},
{
  id:"demography", cat:"Statistics", title:"The world in 2100",
  hook:"Europe and East Asia are greying. Africa is young.",
  notes:"Median ages ≈ 2024 and projections from UN World Population Prospects 2024 (medium scenario), rounded. Projections are scenarios, not certainties.",
  scenes:[
    {title:"Median age today", text:"Half the people in each country are older than this number. Japan and Italy sit near 48–49. Niger sits near 15.",
      view:{mode:"equal", center:[20,15], zoom:1}, choro:{data:"MEDAGE", title:"Median age, years (≈ 2024)", fmt:v=>v+" yrs"}},
    {title:"Peak humanity", text:"The UN expects the world population to rise from about 8.2 billion today to a peak near 10.3 billion in the mid-2080s, then slowly decline.",
      view:{mode:"globe", center:[40,20], zoom:1}, choro:{data:"MEDAGE", title:"Median age, years (≈ 2024)", fmt:v=>v+" yrs"}},
    {title:"Shrinking giants", text:"China's population is already falling and is projected to roughly halve by 2100. Japan, South Korea, Italy and much of Eastern Europe are shrinking too.",
      view:{mode:"globe", center:[115,35], zoom:1.4}, fills:{CHN:"c2",JPN:"c2",KOR:"c2"}, highlight:["CHN","JPN","KOR"]},
    {title:"Africa's century", text:"Sub-Saharan Africa will account for more than half of global population growth to 2050. By 2100, Nigeria, the DR Congo and Ethiopia are projected to be among the most populous countries on Earth.",
      view:{mode:"globe", center:[20,0], zoom:1.1}, fills:Object.fromEntries(SSA.map(c=>[c,"c4"])), highlight:["NGA","COD","ETH"]},
    {title:"India's peak", text:"India passed China as the most populous country in 2023. It is projected to peak around 1.7 billion in the early 2060s.",
      view:{mode:"globe", center:[80,22], zoom:1.6}, fills:{IND:"c3"}, highlight:["IND"]}
  ]
},
{
  id:"dark", cat:"Statistics", title:"Who is in the dark",
  hook:"One in ten people on Earth still has no electricity.",
  notes:"Access to electricity, % of population, ≈ 2022, World Bank / Tracking SDG7. Values rounded; countries not coloured are at or near universal access (≈ 95%+).",
  scenes:[
    {title:"Light is not evenly spread", text:"About 91% of humans have electricity at home. Of the roughly 700 million who don't, more than 80% live in sub-Saharan Africa.",
      view:{mode:"equal", center:[20,5], zoom:1}, choro:{data:"POWER", title:"Access to electricity, %", reverse:true, fmt:v=>v+"%"}},
    {title:"The deepest darkness", text:"In South Sudan, Chad and Burundi, roughly one person in ten has power at home. Across sub-Saharan Africa, it is about half.",
      view:{mode:"globe", center:[22,2], zoom:1.6}, choro:{data:"POWER", title:"Access to electricity, %", reverse:true, fmt:v=>v+"%"}},
    {title:"A border you can see from space", text:"At night, satellite images show South Korea glowing. North of the border, almost everything is dark apart from Pyongyang.",
      view:{mode:"globe", center:[127.5,38.5], zoom:4.5}, fills:{KOR:"c3",PRK:"muted"}, points:[{at:[125.75,39.03],label:"Pyongyang",r:3},{at:[126.98,37.57],label:"Seoul",r:5,color:"c3"}],
      legend:[{color:"c3",label:"Lit"},{color:"muted",label:"Mostly dark"}]}
  ]
},

// ===== GEOPOLITICS =====
{
  id:"chokepoints", cat:"Geopolitics", title:"Chokepoints",
  hook:"A handful of narrow straits carry the world's oil and goods.",
  notes:"Oil flows from the US Energy Information Administration (World Oil Transit Chokepoints; Hormuz ≈ 20 million barrels/day in 2024, Malacca ≈ 23 million in 2023). Trade share and Red Sea disruption: UNCTAD, 2024. Routes are schematic; distances are computed along the drawn line.",
  scenes:[
    {title:"Seven narrow doors", text:"Most of the world's seaborne trade squeezes through a few straits and canals. Block one, and prices move worldwide within days.",
      view:{mode:"globe", center:[50,20], zoom:1}, points:"CHOKE", political:true},
    {title:"Strait of Hormuz", text:"About 20 million barrels of oil pass here every day, roughly a fifth of global consumption. At its narrowest the strait is about 33 km wide.",
      view:{mode:"globe", center:[55,26], zoom:5}, points:[{at:[56.4,26.6],label:"Hormuz",r:7,color:"c2"}], highlight:["IRN","OMN","ARE"]},
    {title:"Strait of Malacca", text:"The busiest oil route by volume, linking the Indian Ocean to China, Japan and Korea. Tens of thousands of ships a year thread between Malaysia and Sumatra.",
      view:{mode:"globe", center:[101,3], zoom:4.5}, points:[{at:[100.8,2.8],label:"Malacca",r:7,color:"c2"}], highlight:["MYS","IDN"]},
    {title:"The Red Sea detour", text:"Since attacks on shipping began in late 2023, many ships avoid Suez and sail around Africa. Compare the two routes from Shanghai to Rotterdam.",
      view:{mode:"globe", center:[45,5], zoom:0.95},
      routes:[{path:SUEZ_ROUTE,color:"c1",width:2.5,label:"Via Suez",dist:true,flow:true,labelAt:15},{path:CAPE_ROUTE,color:"c2",width:2.5,label:"Around the Cape",dist:true,flow:true,labelAt:11}],
      points:[{at:[43.4,12.6],label:"Bab el-Mandeb",r:5},{at:[32.4,30.6],label:"Suez Canal",r:5}]},
    {title:"The Panama Canal", text:"The canal runs on fresh water from lakes. A severe drought in 2023 forced it to cut daily ship crossings by roughly a third, showing that climate is a chokepoint too.",
      view:{mode:"globe", center:[-80,10], zoom:5}, points:[{at:[-79.7,9.1],label:"Panama Canal",r:7,color:"c2"}], highlight:["PAN"]}
  ]
},
{
  id:"blocs", cat:"Geopolitics", title:"Blocs over time",
  hook:"Watch alliances grow, split and shift from 1945 to today.",
  notes:"Membership by year of accession. Soviet republics are shown as today's states; East Germany (Warsaw Pact) cannot be separated from today's Germany at this scale, so Germany shows West Germany's NATO membership from 1955. Albania left the Warsaw Pact formally in 1968. The UK left the EU in 2020.",
  scenes:[
    {title:"Two camps", text:"Drag the slider or press play. NATO forms in 1949, the Warsaw Pact in 1955. After 1991, many former Warsaw Pact members join NATO.",
      view:{mode:"globe", center:[30,52], zoom:1.3},
      timeline:{years:range(1945,2025), start:5, label:y=>y, frame:y=>{
        const g1=Object.keys(NATO_JOIN).filter(c=>NATO_JOIN[c]<=y), g2=Object.keys(WARSAW).filter(c=>y>=WARSAW[c][0]&&y<=WARSAW[c][1]);
        return {groups:[{label:"NATO ("+g1.length+")",color:"c1",ids:g1},{label:"Warsaw Pact",color:"c2",ids:g2}]};}}},
    {title:"The European project", text:"Six countries found the European Economic Community in 1958. Enlargement waves follow in 1973, the 1980s, 1995 and the big eastern expansion of 2004. In 2020 the UK leaves.",
      view:{mode:"globe", center:[15,52], zoom:1.8},
      timeline:{years:range(1957,2025), start:1, label:y=>y, frame:y=>{
        const g=Object.keys(EU_JOIN).filter(c=>EU_JOIN[c]<=y && !(c==="GBR"&&y>=2020));
        return {groups:[{label:(y<1993?"EEC / EC (":"EU (")+g.length+")",color:"c1",ids:g}]};}}},
    {title:"BRICS", text:"Starting as an investment-bank acronym, BRICS became a club in 2009. South Africa joins in 2011, five more countries in 2024 and Indonesia in 2025.",
      view:{mode:"equal", center:[40,10], zoom:1},
      timeline:{years:range(2008,2025), start:1, label:y=>y, frame:y=>{
        const g=Object.keys(BRICS_JOIN).filter(c=>BRICS_JOIN[c]<=y);
        return {groups:[{label:"BRICS ("+g.length+")",color:"c3",ids:g}]};}}}
  ]
},
{
  id:"borders", cat:"Geopolitics", title:"Same border, different truths",
  hook:"Every map takes a side. Here are six places where it shows.",
  notes:"Simplified. Kashmir shares: ≈ India 55%, Pakistan 30%, China 15% of the territory. Taiwan: recognised by 12 states incl. the Holy See (2024); smaller recognisers are islands too small for this map. Kosovo: recognition counts vary by source. Map makers such as Google show different borders depending on the country you view from.",
  scenes:[
    {title:"Western Sahara, as the UN sees it", text:"The UN lists Western Sahara as a non-self-governing territory. Its status has been disputed since Spain withdrew in 1975.",
      view:{mode:"globe", center:[-9,26], zoom:3.2}, fills:{MAR:"c1",ESH:"c3"}, legend:[{color:"c1",label:"Morocco"},{color:"c3",label:"Disputed territory"}]},
    {title:"Western Sahara, as Morocco sees it", text:"Maps sold in Morocco show one country, no border. Morocco controls most of the territory. The United States recognised Moroccan sovereignty in 2020.",
      view:{mode:"globe", center:[-9,26], zoom:3.2}, fills:{MAR:"c1",ESH:"c1"}, legend:[{color:"c1",label:"Morocco, as drawn in Rabat"}]},
    {title:"Kashmir", text:"India, Pakistan and China each administer part of Kashmir, and the two largest each claim more. Indian maps show all of it as Indian; Pakistani maps differ.",
      view:{mode:"globe", center:[76,33], zoom:4}, fills:{IND:"c1",PAK:"c4",CHN:"c3"}, points:[{at:[76.5,34.5],label:"Kashmir",r:7,color:"c2"}]},
    {title:"Crimea", text:"Russia annexed Crimea in 2014. In a 2014 UN General Assembly vote, 100 countries affirmed Ukraine's territorial integrity; most maps still show it as Ukraine.",
      view:{mode:"globe", center:[34,47], zoom:4}, fills:{UKR:"c3",RUS:"c2"}, points:[{at:[34.1,44.95],label:"Crimea",r:7,color:"c2"}]},
    {title:"Taiwan", text:"Taiwan governs itself, while Beijing claims it. Only about a dozen states recognise Taiwan officially; those large enough to see on this map are highlighted.",
      view:{mode:"equal", center:[0,10], zoom:1}, fills:{TWN:"c3",CHN:"c2",BLZ:"c3",GTM:"c3",HTI:"c3",PRY:"c3",SWZ:"c3"}, points:[{at:[121,23.7],label:"Taiwan",r:4,color:"c3"}],
      legend:[{color:"c3",label:"Taiwan and states recognising it"},{color:"c2",label:"PRC"}]},
    {title:"Kosovo", text:"Kosovo declared independence from Serbia in 2008. Roughly half of UN members recognise it; Serbia, Russia, China and five EU states do not.",
      view:{mode:"globe", center:[20.9,42.6], zoom:7}, fills:{XKX:"c3",SRB:"c1"}, points:[{at:[21.17,42.66],label:"Pristina",r:3}]}
  ]
},
{
  id:"arctic", cat:"Geopolitics", title:"The Arctic opens",
  hook:"Melting ice is creating a new ocean, and new claims.",
  notes:"September Arctic sea-ice minimum ≈ 7 million km² around 1980 vs ≈ 3.4 million in 2012 (record low), NSIDC. Ice is drawn as a circle of equal area, schematic. Routes schematic; distances computed along the drawn line.",
  scenes:[
    {title:"Looking down from the pole", text:"Most maps cut the Arctic into an edge. On a globe it is the centre of a ring of powers: Russia, the US, Canada, Denmark via Greenland, Norway.",
      view:{mode:"globe", center:[0,88], zoom:1.25}, fills:{RUS:"c2",USA:"c1",CAN:"c1",GRL:"c4",NOR:"c4",ISL:"c4"}},
    {title:"The ice is shrinking", text:"Around 1980, September sea ice covered about 7 million km². In 2012 it fell to about 3.4 million. Each circle has the same area as the ice in that year.",
      view:{mode:"globe", center:[0,88], zoom:1.25},
      circles:[{center:[0,90], km:1500, color:"c1", label:"≈ 1980", labelAt:[135,74]},{center:[0,90], km:1040, color:"c3", label:"≈ 2012", labelAt:[-45,84]}]},
    {title:"A shortcut to Asia", text:"The Northern Sea Route along Russia's coast is far shorter between Europe and East Asia than the route via Suez. Ice, cost and politics still keep most ships away.",
      view:{mode:"globe", center:[60,65], zoom:0.95},
      routes:[{path:"NSR",color:"c4",width:2.5,label:"Northern Sea Route",dist:true,flow:true},{path:SUEZ_YOKO,color:"c1",width:2,label:"Via Suez",dist:true}]},
    {title:"The Northwest Passage", text:"On the Canadian side, a maze of islands. Canada calls these internal waters; the US and others call it an international strait.",
      view:{mode:"globe", center:[-100,72], zoom:2}, routes:[{path:"NWP",color:"c2",width:2.5,label:"Northwest Passage",flow:true}], fills:{CAN:"c1"}},
    {title:"Who owns the pole", text:"Russia, Denmark and Canada have all filed UN claims to the seabed of the Lomonosov Ridge. Their claims overlap, and all three include the North Pole.",
      view:{mode:"globe", center:[0,88], zoom:1.6}, fills:{RUS:"c2",GRL:"c4",CAN:"c1"},
      routes:[{path:[[142,77],[-5,90],[-70,83]],color:"c3",width:3,label:"Lomonosov Ridge"}], points:[{at:[0,90],label:"North Pole",r:4}]}
  ]
},
{
  id:"cables", cat:"Geopolitics", title:"The internet is under the sea",
  hook:"Almost all intercontinental data travels through cables on the seabed.",
  notes:"Around 600 cables are active or planned (TeleGeography). Routes here are schematic and a small sample. Cable faults: about 150–200 per year, mostly from fishing and anchors (International Cable Protection Committee).",
  scenes:[
    {title:"Not satellites, cables", text:"Your video call to New York almost certainly runs through a cable about the width of a garden hose, lying on the ocean floor.",
      view:{mode:"globe", center:[-40,35], zoom:1.05}, routes:"CABLES_ATL"},
    {title:"Big tech builds its own", text:"Google, Meta, Microsoft and Amazon now pay for many new cables themselves. MAREA, Dunant and Grace Hopper cross the Atlantic; JUPITER crosses the Pacific.",
      view:{mode:"globe", center:[-130,30], zoom:1}, routes:"CABLES_ALL"},
    {title:"Wrapping a continent", text:"2Africa, led by Meta with partners, circles the African continent and is one of the longest cables ever built, around 45,000 km.",
      view:{mode:"globe", center:[15,5], zoom:1.05}, routes:"CABLES_AFR"},
    {title:"When cables break", text:"In early 2024, a ship's dragging anchor in the Red Sea cut three major cables at once. Repairs need specialised ships, and there are only a few dozen in the world.",
      view:{mode:"globe", center:[42,16], zoom:3.5}, routes:"CABLES_RED", points:[{at:[42.7,13.6],label:"Cables cut, 2024",r:7,color:"c2"}]}
  ]
},

// ===== ECONOMICS =====
{
  id:"gravity", cat:"Economics", title:"The economic centre of gravity",
  hook:"For 2,000 years, the world's economic centre has been on the move.",
  notes:"Illustrative reconstruction after McKinsey Global Institute (2012), 'Urban world'. Positions are approximate. The centre of gravity is calculated through the Earth and then placed on the surface, which is why it sits so far north.",
  scenes:[
    {title:"A single moving dot", text:"Weight every place on Earth by its economic output and find the balance point. Drag the slider to watch it travel.",
      view:{mode:"globe", center:[30,60], zoom:1.15},
      timeline:{years:[1,1000,1500,1820,1870,1913,1940,1950,1960,1970,1980,1990,2000,2010,2025], start:0, label:y=>y===2025?"2025 (projected)":"Year "+y, frame:(y,i)=>{
        const pts=GRAVITY.slice(0,i+1);
        return {routes:[{path:pts.map(p=>p.at),color:"c2",width:2.5}],
          points:pts.map((p,j)=>({at:p.at,r:j===i?8:3,color:j===i?"c2":"c1",label:j===i?(p.y===1?"Year 1":String(p.y)):null})),
          caption:GRAVITY[i].note};}}},
    {title:"Back to Asia", text:"For most of history, China and India produced most of the world's output. Industrialisation pulled the centre to the North Atlantic. Since 1980 it has been racing back east.",
      view:{mode:"equal", center:[30,40], zoom:1.5},
      routes:[{path:"GRAVITY",color:"c2",width:2.5}], points:"GRAVITY_ENDS"}
  ]
},
{
  id:"phone", cat:"Economics", title:"Where your phone comes from",
  hook:"Follow a smartphone from the mine to your pocket.",
  notes:"An illustrative, typical smartphone supply chain. Specific suppliers and shares vary by brand and model and change every year.",
  scenes:[
    {title:"Dug out of the ground", text:"Cobalt from the DR Congo. Lithium from Australia and Chile. Rare earths from China. Tin from Indonesia. A phone contains dozens of elements.",
      view:{mode:"globe", center:[60,-10], zoom:0.95}, points:"PHONE_MINE"},
    {title:"Refined in China", text:"Much of it travels to China, which refines most of the world's cobalt, lithium and rare earths.",
      view:{mode:"globe", center:[90,5], zoom:0.95}, routes:"PHONE_REFINE", points:"PHONE_MINE"},
    {title:"Chips: a global relay", text:"Designed in California. Made in Taiwan, on machines that only one Dutch company, ASML, can build. Memory from South Korea, camera sensors from Japan.",
      view:{mode:"globe", center:[150,35], zoom:0.95}, routes:"PHONE_CHIPS", points:"PHONE_CHIP_PTS"},
    {title:"Assembly", text:"Final assembly mostly happens in China, with a fast-growing share in India and Vietnam.",
      view:{mode:"globe", center:[105,22], zoom:1.6}, routes:"PHONE_ASSEMBLY", points:"PHONE_ASM_PTS"},
    {title:"To your pocket", text:"By the time a phone reaches a shop in Vienna, its parts may have travelled further than a trip around the Earth.",
      view:{mode:"globe", center:[60,35], zoom:1}, routes:"PHONE_HOME", points:[{at:P.vienna,label:"Vienna",r:7,color:"c2"}]}
  ]
},
{
  id:"minerals", cat:"Economics", title:"Critical minerals",
  hook:"The energy transition runs on minerals from very few places.",
  notes:"Mine production shares ≈ 2023, US Geological Survey Mineral Commodity Summaries 2024, rounded. Refining shares ≈ IEA Global Critical Minerals Outlook 2024. China export controls: gallium and germanium (2023), graphite (2023), selected rare earths (2025).",
  scenes:[
    {title:"Cobalt", text:"About three quarters of the world's cobalt is mined in the DR Congo. It goes into most lithium-ion batteries.",
      view:{mode:"globe", center:[25,-5], zoom:1}, choro:{data:"COBALT", title:"Share of world cobalt mining, %", fmt:v=>v+"%"}},
    {title:"Lithium", text:"Australia digs about half of the world's lithium; Chile and China follow.",
      view:{mode:"equal", center:[30,0], zoom:1}, choro:{data:"LITHIUM", title:"Share of world lithium mining, %", fmt:v=>v+"%"}},
    {title:"Rare earths", text:"China mines roughly 70% of rare earths, the metals inside wind turbine and electric-car magnets.",
      view:{mode:"globe", center:[105,30], zoom:1}, choro:{data:"RARE", title:"Share of world rare-earth mining, %", fmt:v=>v+"%"}},
    {title:"The real bottleneck: refining", text:"Mining is spread out. Refining is not. China processes about 90% of rare earths, around 75% of cobalt and two thirds of lithium, and has started restricting exports of some of them.",
      view:{mode:"globe", center:[105,32], zoom:1.3}, fills:{CHN:"c2"}, routes:"REFINE_IN",
      legend:[{color:"c2",label:"China: ≈ 90% rare earths, ≈ 75% cobalt, ≈ 65% lithium refining"}]}
  ]
},
{
  id:"austria-gas", cat:"Economics", title:"Austria's gas",
  hook:"How a country near Vienna ran on Siberian gas, then stopped.",
  notes:"Russian share of Austrian gas imports ≈ 80% in 2021, peaking near 98% in late 2023 (Austrian ministry for climate and energy). Gazprom halted deliveries to OMV in Nov 2024; OMV terminated the contract in Dec 2024; transit through Ukraine ended 1 Jan 2025. Pipeline routes schematic.",
  scenes:[
    {title:"Baumgarten", text:"A village on the March river, east of Vienna, is one of Central Europe's biggest gas hubs. For decades, Soviet and then Russian gas arrived here first.",
      view:{mode:"globe", center:[16.8,48.3], zoom:8}, points:[{at:P.baumgarten,label:"Baumgarten",r:7,color:"c2"},{at:P.vienna,label:"Vienna",r:4}], highlight:["AUT"]},
    {title:"A 4,000 km pipe", text:"Gas from West Siberia crossed Russia, Ukraine and Slovakia to reach Austria. Austria was the first Western country to sign a gas deal with the Soviet Union, in 1968.",
      view:{mode:"globe", center:[45,55], zoom:1.6}, routes:"GAS_RU", points:[{at:[76.5,66.1],label:"Urengoy",r:5},{at:P.baumgarten,label:"Baumgarten",r:5,color:"c2"}]},
    {title:"Deeper dependence", text:"Even after Russia invaded Ukraine in 2022, Russian gas made up most of Austria's imports, close to 98% at one point in late 2023, largely because of a long-term OMV contract running to 2040.",
      view:{mode:"globe", center:[30,52], zoom:2.2}, fills:{AUT:"c2",RUS:"c2"}, routes:"GAS_RU"},
    {title:"The tap closes", text:"In November 2024 Gazprom stopped deliveries to OMV, which cancelled the contract. On 1 January 2025, transit through Ukraine ended. Austria now imports via Germany and Italy, including Norwegian gas and LNG.",
      view:{mode:"globe", center:[12,51], zoom:2.3}, routes:"GAS_NEW", fills:{AUT:"c1"}}
  ]
},
{
  id:"remittances", cat:"Economics", title:"Money sent home",
  hook:"Migrants send home more than all foreign aid and investment combined.",
  notes:"World Bank Migration and Development Brief 40 (2024): ≈ USD 656 billion to low- and middle-income countries in 2023, larger than FDI and official aid combined (excl. China). Shares of GDP ≈ 2023, rounded. Flows drawn are major corridors, schematic.",
  scenes:[
    {title:"A quiet giant", text:"In 2023, migrants sent about 656 billion dollars to families in low- and middle-income countries. That is more than foreign direct investment and development aid combined.",
      view:{mode:"globe", center:[20,25], zoom:1}, routes:"REMIT"},
    {title:"The biggest receivers", text:"India received about 120 billion dollars, more than any country in history. Mexico followed with about 66 billion, then China, the Philippines and Pakistan.",
      view:{mode:"equal", center:[0,20], zoom:1}, choro:{data:"REMIT_USD", title:"Remittances received, USD billion (2023)", log:true, fmt:v=>"$"+v+" B"}},
    {title:"Where it matters most", text:"In Tajikistan, money sent home is close to half of the whole economy, mostly from workers in Russia. In Nepal, Honduras and Lebanon, it is about a quarter.",
      view:{mode:"globe", center:[45,30], zoom:1}, choro:{data:"REMIT_GDP", title:"Remittances, % of GDP (≈ 2023)", fmt:v=>v+"%"}}
  ]
},

// ===== PEOPLE =====
{
  id:"darien", cat:"People", title:"One journey north",
  hook:"From Caracas to the US border, through one of the world's most dangerous jungles.",
  notes:"A composite route built from widely reported migrant journeys, not one individual's story. Darién crossings counted by Panama's migration authority: ≈ 520,000 in 2023, ≈ 300,000 in 2024; numbers fell sharply in 2025 after US policy changes.",
  scenes:[
    {title:"Leaving Caracas", text:"Since 2014, close to 8 million people have left Venezuela, one of the largest displacement crises in the world. Most stay in South America. Some head north.",
      view:{mode:"globe", center:[-70,8], zoom:3.5}, routes:[{path:"DARIEN",color:"c2",width:2,until:1,flow:true}], points:"DARIEN_STOPS:1"},
    {title:"Necoclí, Colombia", text:"On the Caribbean coast, boats carry people across the Gulf of Urabá to the edge of the jungle. Families wait here for days.",
      view:{mode:"globe", center:[-76.5,8.3], zoom:9}, routes:[{path:"DARIEN",color:"c2",width:2.5,until:3,flow:true}], points:"DARIEN_STOPS:3"},
    {title:"The Darién Gap", text:"About 100 km of roadless jungle, rivers and mountains between Colombia and Panama. The crossing takes most people four to ten days on foot. In 2023, about 520,000 people made it.",
      view:{mode:"globe", center:[-77.4,8.2], zoom:6}, routes:[{path:"DARIEN",color:"c2",width:3,until:5,flow:true}], points:"DARIEN_STOPS:5"},
    {title:"Through Central America", text:"Buses north through Costa Rica, Nicaragua, Honduras and Guatemala. Every border is a new set of checks, fees and risks.",
      view:{mode:"globe", center:[-86,12], zoom:4}, routes:[{path:"DARIEN",color:"c2",width:2.5,until:10,flow:true}], points:"DARIEN_STOPS:10"},
    {title:"The last border", text:"From Tapachula, it is still more than 3,000 km across Mexico to the US border. In 2025, crossings through Darién fell to a trickle, and many people began travelling south again.",
      view:{mode:"globe", center:[-85,18], zoom:2}, routes:[{path:"DARIEN",color:"c2",width:2.5,until:99,flow:true,dist:true,label:"Whole journey"}], points:"DARIEN_STOPS:99"}
  ]
},
{
  id:"plate", cat:"People", title:"What's on your plate",
  hook:"A Viennese breakfast, traced back to its fields.",
  notes:"Shares rounded and approximate: Côte d'Ivoire ≈ 40% of world cocoa; Brazil the largest coffee producer and ≈ 3/4 of orange-juice exports; Ecuador the largest banana exporter (FAO, ICCO, USDA).",
  scenes:[
    {title:"Coffee", text:"The Melange starts in Brazil, the world's largest coffee producer, or Vietnam, the second. Coffee itself first grew wild in Ethiopia.",
      view:{mode:"globe", center:[-10,15], zoom:0.95}, routes:"PLATE_COFFEE", points:[{at:P.vienna,label:"Vienna",r:6,color:"c2"}]},
    {title:"Chocolate and orange juice", text:"Cocoa for the spread comes mostly from Côte d'Ivoire and Ghana. The orange juice almost certainly came from São Paulo state in Brazil.",
      view:{mode:"globe", center:[-15,10], zoom:1}, routes:"PLATE_CJ", points:[{at:P.vienna,label:"Vienna",r:6,color:"c2"}]},
    {title:"The banana", text:"Ecuador ships more bananas than any other country, around a quarter of the world's exports.",
      view:{mode:"globe", center:[-40,25], zoom:1}, routes:"PLATE_BANANA", points:[{at:P.vienna,label:"Vienna",r:6,color:"c2"}]},
    {title:"And from next door", text:"The roll, the butter, the sugar from Lower Austrian beet, and the apricot jam from the Wachau travelled less than 100 km.",
      view:{mode:"globe", center:[16,48.3], zoom:9}, routes:"PLATE_LOCAL", points:"PLATE_LOCAL_PTS"}
  ]
},
{
  id:"flights", cat:"People", title:"Why planes fly curves",
  hook:"The straight line on a globe is a curve on a flat map.",
  notes:"Distances are great-circle distances computed live. Real flight paths also follow winds, airspace and air-traffic rules. The southern Vienna–Tokyo route is schematic.",
  scenes:[
    {title:"The shortest way", text:"On a globe, the shortest path between two cities is a great circle. Here is Frankfurt to Los Angeles: straight over Greenland.",
      view:{mode:"globe", center:[-50,65], zoom:1.1}, routes:[{path:[P.frankfurt,P.la],color:"c2",width:3,dist:true,label:"Frankfurt–Los Angeles",flow:true}]},
    {title:"Now flatten it", text:"Same line, flat map. It bends up towards the Arctic. Nothing changed but the projection.",
      view:{mode:"mercator", center:[-50,50], zoom:1.3}, routes:[{path:[P.frankfurt,P.la],color:"c2",width:3,dist:true,label:"Frankfurt–Los Angeles",flow:true}]},
    {title:"The longest flight", text:"New York to Singapore is one of the longest scheduled flights, around 15,000 km and close to 19 hours. Its shortest path runs close to the North Pole.",
      view:{mode:"globe", center:[100,75], zoom:1}, routes:[{path:[P.nyc,P.singapore],color:"c2",width:3,dist:true,label:"New York–Singapore",flow:true}]},
    {title:"Vienna to Tokyo, then and now", text:"Before 2022, flights crossed Siberia. Since Russia's airspace closed to European airlines, they detour south over Central Asia and China.",
      view:{mode:"globe", center:[80,50], zoom:1.3}, fills:{RUS:"muted"},
      routes:[{path:[P.vienna,P.tokyo],color:"c1",width:2,dist:true,label:"Before 2022",dash:true},{path:[P.vienna,[33,42],[50,41],[66,42],[82,43],[100,40],[118,38],P.tokyo],color:"c2",width:3,dist:true,label:"Since 2022",flow:true}]}
  ]
},
{
  id:"languages", cat:"People", title:"Languages going quiet",
  hook:"About 7,000 languages, and many have only a few speakers left.",
  notes:"Ethnologue (2024): ≈ 7,160 living languages, ≈ 44% endangered; half the world speaks one of ≈ 23 languages. Language counts per country approximate.",
  scenes:[
    {title:"Where languages live", text:"Papua New Guinea alone has around 840 languages. Indonesia, Nigeria and India each have hundreds. Half of humanity speaks one of just 23 languages.",
      view:{mode:"equal", center:[60,0], zoom:1}, choro:{data:"LANGS", title:"Living languages (≈)", log:true, fmt:v=>v}},
    {title:"The last speaker", text:"In 2022, Cristina Calderón died in Puerto Williams, Chile. She was the last native speaker of Yaghan, the language of people who lived at the southern tip of the Americas.",
      view:{mode:"globe", center:[-68,-54], zoom:5}, points:[{at:[-67.6,-54.93],label:"Puerto Williams",r:6,color:"c2"}]},
    {title:"Livonian", text:"In 2013, Grizelda Kristiņa, the last native speaker of Livonian from the Latvian coast, died at 103. A small community still learns it today.",
      view:{mode:"globe", center:[22,57.5], zoom:7}, points:[{at:[22.0,57.6],label:"Livonian coast",r:6,color:"c2"}]},
    {title:"Coming back", text:"Languages can return. Manx lost its last native speaker in 1974 and now has a primary school. Hawaiian, once nearly gone, is taught from preschool to university. Ainu in Japan is being revived too.",
      view:{mode:"globe", center:[-170,40], zoom:0.95}, points:[{at:[-4.5,54.2],label:"Manx",r:6,color:"c4"},{at:[-157.8,21.3],label:"Hawaiian",r:6,color:"c4"},{at:[142.8,43.2],label:"Ainu",r:6,color:"c4"}]}
  ]
}
];

// ---------- datasets ----------
const DATA = {
POP:{IND:1464,CHN:1416,USA:347,IDN:286,PAK:255,NGA:238,BRA:213,BGD:176,RUS:144,ETH:135,MEX:131,JPN:123,EGY:118,PHL:116,COD:112,VNM:101,IRN:92,TUR:87,DEU:84,THA:72,GBR:69,TZA:70,FRA:66,ZAF:64,ITA:59,KEN:57,MMR:55,COL:53,KOR:51,SDN:51,UGA:51,ESP:48,DZA:47,IRQ:47,ARG:46,AFG:43,CAN:40,POL:38,MAR:38,UKR:38,AGO:39,UZB:37,SAU:34,PER:34,MYS:36,GHA:35,MOZ:35,YEM:41,VEN:28,NPL:30,MDG:32,CIV:32,CMR:30,NER:27,AUS:27,PRK:26,TWN:23,MLI:25,BFA:24,SYR:25,LKA:22,MWI:22,ZMB:21,KAZ:20,CHL:20,TCD:21,ROU:19,SOM:19,SEN:19,GTM:18,NLD:18,ECU:18,KHM:18,ZWE:17,GIN:15,BEN:14,RWA:14,BDI:14,BOL:13,TUN:12,HTI:12,BEL:12,JOR:11,CUB:11,SWE:10.6,CZE:10.6,GRC:10,PRT:10,AZE:10,HUN:9.6,AUT:9.1,BLR:9,CHE:9,ISR:10,TJK:10,PNG:10,ARE:11,HND:11,SSD:12,TGO:9.5,SRB:6.6,LAO:7.8,PRY:6.9,LBY:7.4,KGZ:7.2,NIC:7,SLV:6.4,BGR:6.4,TKM:7.5,DNK:6,FIN:5.6,NOR:5.6,SVK:5.4,COG:6.3,CAF:5.5,IRL:5.3,NZL:5.2,LBN:5.8,CRI:5.1,PSE:5.5,OMN:5.3,LBR:5.6,MRT:5.2,KWT:5,PAN:4.5,HRV:3.8,GEO:3.8,ERI:3.6,MNG:3.5,URY:3.4,BIH:3.1,ARM:3,ALB:2.8,LTU:2.8,JAM:2.8,QAT:3,MDA:2.4,NAM:3,BWA:2.5,GMB:2.8,GAB:2.5,LSO:2.3,SVN:2.1,MKD:1.8,LVA:1.8,GNB:2.2,GNQ:1.9,TTO:1.5,EST:1.4,TLS:1.4,SWZ:1.2,DJI:1.2,FJI:0.9,CYP:1.4,GUY:0.8,BTN:0.8,SLB:0.8,MNE:0.6,SUR:0.6,LUX:0.7,ISL:0.4,BHS:0.4,BLZ:0.4,VUT:0.3,BRN:0.5,SLE:8.8,DOM:11.4,XKX:1.6,SOL:5.7},
MEDAGE:{JPN:49,ITA:48,KOR:45,DEU:45,GRC:46,PRT:46,ESP:45,AUT:43,BGR:45,HRV:45,SVN:45,LTU:44,LVA:44,EST:42,FIN:43,FRA:42,GBR:40,NLD:42,BEL:42,CHE:43,CZE:43,HUN:43,POL:41,ROU:43,SRB:43,UKR:42,BLR:41,RUS:39,SWE:40,NOR:40,DNK:42,IRL:39,CAN:41,USA:38,AUS:37,NZL:37,CHN:39,TWN:44,THA:40,VNM:33,MYS:30,IDN:30,PHL:25,IND:28,BGD:27,PAK:21,IRN:33,TUR:33,SAU:30,EGY:24,MAR:29,DZA:28,TUN:33,ISR:30,IRQ:20,AFG:17,KAZ:31,UZB:28,MNG:28,PRK:35,MMR:29,NPL:25,LKA:33,BRA:34,ARG:32,CHL:36,URY:36,COL:31,PER:30,VEN:30,ECU:29,BOL:25,MEX:30,GTM:23,HND:24,CUB:42,NGA:18,NER:15,MLI:16,TCD:16,ETH:19,KEN:20,TZA:17,UGA:16,COD:16,AGO:16,SOM:16,ZAF:28,GHA:21,CIV:19,CMR:18,SDN:19,SSD:18,MOZ:17,ZMB:17,ZWE:18,MDG:19,BFA:17,SEN:19,MWI:17,YEM:19,GIN:18,BEN:18,RWA:19,BDI:17,CAF:15,NAM:22,BWA:24,ERI:19,LBY:28,PNG:22,KHM:27,LAO:24,SYR:23,JOR:24,GEO:38,ARM:36,AZE:32,TKM:27,KGZ:26,TJK:22,MRT:18,TGO:19,SLE:19,LBR:18,GAB:21,COG:19,SWZ:22,LSO:23,PRY:28,NIC:27,SLV:28,DOM:28,HTI:23,JAM:31,PAN:30,CRI:34,BIH:44,MKD:40,ALB:38,MNE:39,MDA:38,ISL:37,OMN:30,ARE:32,QAT:33,KWT:37,LBN:30,PSE:20},
POWER:{SSD:8,TCD:12,BDI:10,MWI:14,NER:19,COD:22,CAF:16,MOZ:33,MDG:36,BFA:20,SLE:31,LBR:32,ETH:55,NGA:61,UGA:47,TZA:46,KEN:76,ZMB:47,ZWE:50,AGO:49,SDN:63,SOM:50,GIN:47,MLI:53,CMR:66,CIV:72,GHA:88,SEN:70,ZAF:87,HTI:49,PNG:20,MMR:74,GNB:37,TGO:57,BEN:45,MRT:50,LSO:50,SWZ:82,NAM:56,BWA:75,RWA:50,COG:50,GAB:93,GMB:64,DJI:65,ERI:55,AFG:85,YEM:77,SOL:50,PRK:52},
COBALT:{COD:74,IDN:7,RUS:4,AUS:2,PHL:2,CUB:2,CAN:2,PNG:1,MDG:1,CHN:1},
LITHIUM:{AUS:48,CHL:24,CHN:18,ZWE:8,ARG:5,BRA:3},
RARE:{CHN:69,USA:12,MMR:11,AUS:5,THA:2,IND:1},
REMIT_USD:{IND:120,MEX:66,CHN:50,PHL:39,PAK:27,EGY:20,BGD:22,GTM:20,NPL:11,NGA:20,UKR:14,VNM:14,COL:10,SLV:9,HND:9,DOM:10,MAR:12,UZB:12,LBN:7,JOR:4,KGZ:3,TJK:6,LKA:6,IDN:15,NIC:5,HTI:4,JAM:4,GHA:5,KEN:4,SEN:3,BRA:4,ECU:5,PER:4,MDA:2,ARM:4,GEO:4},
REMIT_GDP:{TJK:48,LBN:27,NIC:27,HND:26,NPL:26,SLV:24,LSO:21,GTM:19,HTI:19,JAM:19,KGZ:19,MDA:12,PHL:9,PAK:8,GMB:23,EGY:6,BGD:5,MEX:4,IND:3,UKR:8,ARM:10,GEO:12,SEN:10,UZB:13,JOR:9,DOM:8,MAR:8},
LANGS:{PNG:840,IDN:710,NGA:520,IND:450,USA:330,CHN:300,MEX:290,CMR:280,AUS:300,BRA:220,COD:210,PHL:180,MYS:130,TCD:130,TZA:120,VUT:110,NPL:120,CAF:70,RUS:110,ETH:90,SDN:70,MMR:110,VNM:110,LAO:85,GHA:80,CIV:80,BEN:55,TGO:40,KEN:70,UGA:45,COL:80,PER:90,BOL:40,CAN:90,SLB:75,NCL:40,AGO:40,MOZ:45,ZMB:45,THA:70,PAK:75,IRN:80,AFG:40,ARG:40,GTM:25,BFA:70,MLI:65,GIN:40,SEN:40,NER:20,SLE:25,LBR:30,ZAF:30,NAM:30,ZWE:20,MWI:20,MDG:10,BGD:40,TWN:20,JPN:15,KOR:2,DEU:30,FRA:25,ITA:35,ESP:15,GBR:12,AUT:10}
};

const CHOKE_PTS = [
  {at:[56.4,26.6],label:"Hormuz",r:6,color:"c2"},{at:[100.8,2.8],label:"Malacca",r:6,color:"c2"},
  {at:[32.4,30.6],label:"Suez",r:6,color:"c2"},{at:[43.4,12.6],label:"Bab el-Mandeb",r:6,color:"c2"},
  {at:[-79.7,9.1],label:"Panama",r:6,color:"c2"},{at:[29.05,41.12],label:"Bosporus",r:6,color:"c2"},
  {at:[-5.6,35.95],label:"Gibraltar",r:6,color:"c2"}
];

const GRAVITY = [
  {y:1,at:[70,47],note:"Year 1: China and India dominate world output. The centre sits in Central Asia."},
  {y:1000,at:[72,46],note:"Year 1000: little changes for a millennium."},
  {y:1500,at:[68,48],note:"1500: Europe begins to grow, Asia still leads."},
  {y:1820,at:[55,52],note:"1820: the Industrial Revolution starts pulling the centre west."},
  {y:1870,at:[32,57],note:"1870: Britain is the workshop of the world."},
  {y:1913,at:[10,61],note:"1913: Europe and the US dominate."},
  {y:1940,at:[-12,62],note:"1940: the centre crosses into the Atlantic."},
  {y:1950,at:[-24,63],note:"1950: the most westerly point. The US alone produces over a quarter of world output."},
  {y:1960,at:[-20,64],note:"1960: Japan and Europe rebuild."},
  {y:1970,at:[-14,65],note:"1970: the turn begins."},
  {y:1980,at:[-10,66],note:"1980: China opens up."},
  {y:1990,at:[-3,66],note:"1990: back over Europe."},
  {y:2000,at:[5,67],note:"2000: heading east fast."},
  {y:2010,at:[24,66],note:"2010: faster than at any time in history."},
  {y:2025,at:[60,64],note:"2025 (projected): moving back towards Asia."}
];

const ROUTES = {
  NSR:[[4.0,52.0],[5,58],[8,63],[18,70.5],[33,71],[50,72.5],[62,76.5],[80,77],[104,77.9],[130,76],[160,71],[-170,67.5],[-169,64],[178,62],[163,55],[150,45],[142,38],[139.7,35.2]],
  NWP:[[-55,68],[-62,73],[-80,74.2],[-95,74.3],[-105,69],[-115,68.6],[-125,70.5],[-140,71],[-156,71.5],[-168,66]],
  GRAVITY:GRAVITY.map(g=>g.at),
  DARIEN:[[-66.9,10.5],[-72.5,7.9],[-75.57,6.25],[-76.78,8.42],[-77.35,8.63],[-77.85,8.35],[-80.0,8.6],[-84.09,9.93],[-86.25,12.13],[-87.2,14.07],[-90.5,14.6],[-92.26,14.9],[-99.13,19.43],[-106.42,31.69]]
};
const DARIEN_NAMES = ["Caracas","Cúcuta","Medellín","Necoclí","Capurganá","Darién Gap","Panama","San José","Managua","Tegucigalpa","Guatemala City","Tapachula","Mexico City","Ciudad Juárez"];

const CABLES = {
  atl:[
    {path:[[-75.98,36.85],[-2.98,43.38]],label:"MAREA"},
    {path:[[-72.9,40.8],[-4.55,50.83]],label:"Grace Hopper"},
    {path:[[-75.98,36.85],[-1.95,46.72]],label:"Dunant"},
    {path:[[-38.5,-3.7],[-8.87,37.95]],label:"EllaLink"},
    {path:[[9.9,2.94],[-38.5,-3.7]],label:"SAIL"}
  ],
  pac:[
    {path:[[136.8,34.3],[-118.4,33.86]],label:"JUPITER"},
    {path:[[151.2,-33.9],[-158.0,21.4],[-120.85,35.37]],label:"Southern Cross"},
    {path:[[103.82,1.35],[95,6],[80,5.5],[72.8,19],[60,15],[43.15,11.6],[39.2,21.5],[32.5,29.9],[32.3,31.4],[20,34],[5.37,43.3]],label:"SEA-ME-WE 6"}
  ],
  afr:[{path:[[8.9,44.4],[2.2,41.4],[-5.6,35.95],[-17.5,14.7],[-4,5.3],[3.4,6.4],[9.7,4.0],[13.2,-8.8],[18.4,-33.9],[31.0,-29.9],[32.6,-25.97],[39.3,-6.8],[39.66,-4.05],[45.3,2.0],[43.15,11.6],[39.2,21.5],[32.5,29.9],[32.3,31.4],[28,33.5],[8.9,44.4]],label:"2Africa"},
       {path:[[-9.14,38.7],[-17,20],[-10,5],[3.4,6.4],[14.5,-22.7],[18.44,-33.72]],label:"Equiano"}]
};

const PHONE = {
  mines:[{at:[25.47,-10.72],label:"Cobalt, DR Congo"},{at:[116.06,-33.85],label:"Lithium, Australia"},{at:[-68.2,-23.5],label:"Lithium, Chile"},{at:[109.97,41.77],label:"Rare earths, China"},{at:[106.1,-2.1],label:"Tin, Indonesia"}],
  refinery:[112,30],
  chips:[{at:[-121.95,37.35],label:"Design, California"},{at:[5.4,51.42],label:"ASML, Netherlands"},{at:[120.97,24.8],label:"Chips, Taiwan"},{at:[127.1,37.0],label:"Memory, South Korea"},{at:[130.7,32.8],label:"Sensors, Japan"}],
  assembly:[{at:[113.63,34.75],label:"Zhengzhou, China"},{at:[79.95,12.97],label:"Chennai, India"},{at:[105.9,21.1],label:"Bac Ninh, Vietnam"}]
};

const PLATE = {
  coffee:[{at:[-45.5,-21.5],label:"Brazil"},{at:[108.05,12.67],label:"Vietnam"},{at:[38.4,6.7],label:"Ethiopia"},{at:[-75.7,5.0],label:"Colombia"}],
  cj:[{at:[-5.5,6.8],label:"Côte d'Ivoire (cocoa)"},{at:[-1.6,6.7],label:"Ghana (cocoa)"},{at:[-48.5,-21.2],label:"São Paulo (oranges)"}],
  banana:[{at:[-79.96,-3.26],label:"Ecuador"}],
  local:[{at:[16.05,48.33],label:"Sugar beet, Tulln"},{at:[15.42,48.38],label:"Apricots, Wachau"},{at:[16.65,48.25],label:"Wheat, Marchfeld"},{at:[15.7,48.6],label:"Milk, Waldviertel"}]
};

const REMIT = [[[-100,38],[-102,23]],[[-100,38],[-90.5,14.6]],[[-100,38],[121,14]],[[-100,38],[78,22]],[[45,24],[78,22]],[[54,24],[76,20]],[[45,24],[70,30]],[[45,24],[31,30]],[[37.6,55.7],[68.8,38.5]],[[37.6,55.7],[74.6,42.9]],[[50,26],[85,28]],[[10,50],[30,49]]];

// resolve named references used in scenes
function resolveRef(key, scene){
  if(key==="CHOKE") return CHOKE_PTS;
  if(key==="CABLES_ATL") return CABLES.atl.map(c=>({...c,color:"c1",width:2,flow:true}));
  if(key==="CABLES_ALL") return [...CABLES.atl,...CABLES.pac].map(c=>({...c,color:"c1",width:2,flow:true}));
  if(key==="CABLES_AFR") return [...CABLES.afr.map(c=>({...c,color:"c2",width:2.5,flow:true})),...CABLES.atl.map(c=>({...c,color:"c1",width:1.5}))];
  if(key==="CABLES_RED") return [...CABLES.afr.slice(0,1),...CABLES.pac.slice(2)].map(c=>({...c,color:"c1",width:2,label:null}));
  if(key==="GRAVITY_ENDS") return [{at:GRAVITY[0].at,label:"Year 1",r:5,color:"c1"},{at:GRAVITY[7].at,label:"1950",r:5,color:"c1"},{at:GRAVITY[14].at,label:"2025",r:7,color:"c2"}];
  if(key==="PHONE_MINE") return PHONE.mines.map(m=>({...m,r:5,color:"c3"}));
  if(key==="PHONE_REFINE") return PHONE.mines.map(m=>({path:[m.at,PHONE.refinery],color:"c3",width:2,flow:true}));
  if(key==="PHONE_CHIP_PTS") return PHONE.chips.map(m=>({...m,r:5,color:"c1"}));
  if(key==="PHONE_CHIPS") return [{path:[PHONE.chips[0].at,PHONE.chips[2].at],color:"c1",width:2,flow:true},{path:[PHONE.chips[1].at,PHONE.chips[2].at],color:"c1",width:2,flow:true},{path:[PHONE.chips[3].at,PHONE.assembly[0].at],color:"c1",width:2,flow:true},{path:[PHONE.chips[4].at,PHONE.assembly[0].at],color:"c1",width:2,flow:true},{path:[PHONE.chips[2].at,PHONE.assembly[0].at],color:"c1",width:2,flow:true}];
  if(key==="PHONE_ASM_PTS") return PHONE.assembly.map(m=>({...m,r:6,color:"c2"}));
  if(key==="PHONE_ASSEMBLY") return PHONE.assembly.slice(1).map(a=>({path:[PHONE.chips[2].at,a.at],color:"c1",width:2,flow:true}));
  if(key==="PHONE_HOME") return PHONE.assembly.map(a=>({path:[a.at,P.vienna],color:"c2",width:2,flow:true}));
  if(key==="REFINE_IN") return [...PHONE.mines.filter(m=>m.label.indexOf("China")<0).map(m=>({path:[m.at,PHONE.refinery],color:"c2",width:2,flow:true}))];
  if(key==="GAS_RU") return [{path:[[76.5,66.1],[60,61],[47.5,56.4],[36.2,51.7],[30.5,50.4],[22.3,48.62],[17.1,48.15],P.baumgarten],color:"c2",width:3,flow:true,dist:true,label:"Siberia to Baumgarten"}];
  if(key==="GAS_NEW") return [
    {path:[[3.7,60.6],[7.2,53.37],[11,50.5],[13.77,48.55],P.baumgarten],color:"c1",width:2.5,flow:true,label:"Norwegian gas",labelAt:0},
    {path:[[8.1,53.52],[11,50.5],[13.77,48.55]],color:"c4",width:2,flow:true,label:"LNG terminals, Germany",labelAt:0},
    {path:[[12.6,45.1],[13.58,46.5],[15.4,47.1],P.baumgarten],color:"c4",width:2.5,flow:true,label:"LNG, Italy",labelAt:0},
    {path:[[30.5,50.4],[22.3,48.62],[17.1,48.15]],color:"muted",width:2,dash:true,label:"Ukraine transit, closed 2025",labelAt:0}];
  if(key==="REMIT") return REMIT.map(r=>({path:r,color:"c4",width:2,flow:true}));
  if(key==="PLATE_COFFEE") return PLATE.coffee.map(p=>({path:[p.at,P.vienna],color:"c3",width:2,flow:true,label:p.label}));
  if(key==="PLATE_CJ") return PLATE.cj.map(p=>({path:[p.at,P.vienna],color:"c3",width:2,flow:true,label:p.label}));
  if(key==="PLATE_BANANA") return PLATE.banana.map(p=>({path:[p.at,P.vienna],color:"c3",width:2.5,flow:true,label:p.label,dist:true}));
  if(key==="PLATE_LOCAL") return PLATE.local.map(p=>({path:[p.at,P.vienna],color:"c4",width:2,flow:true}));
  if(key==="PLATE_LOCAL_PTS") return [...PLATE.local.map(p=>({...p,r:5,color:"c4"})),{at:P.vienna,label:"Vienna",r:6,color:"c2"}];
  if(key.startsWith("DARIEN_STOPS")){const n=+key.split(":")[1]; return ROUTES.DARIEN.slice(0,n+1).map((at,i,a)=>({at,label:i===a.length-1||i===0?DARIEN_NAMES[i]:null,r:i===a.length-1?6:3,color:i===a.length-1?"c2":"c1"}));}
  if(ROUTES[key]) return ROUTES[key];
  return [];
}
