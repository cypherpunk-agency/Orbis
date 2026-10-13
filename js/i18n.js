// ---------- language ----------
// English is the source language. Stories in other languages live in stories/<lang>/ with the same structure;
// interface strings are translated here. Choose with ?lang=de, remembered per browser.
const LANGS = { en: "English", de: "Deutsch" };
const LANG = (() => {
  const q = new URLSearchParams(location.search).get("lang");
  let saved = null; try { saved = localStorage.getItem("orbis-lang"); } catch (e) {}
  const nav = (navigator.language || "en").slice(0, 2);
  const l = q || saved || (LANGS[nav] ? nav : "en");
  if (q) { try { localStorage.setItem("orbis-lang", q); } catch (e) {} }
  return LANGS[l] ? l : "en";
})();
document.documentElement.lang = LANG;

const STRINGS = {
  de: {
    "Stories": "Geschichten", "Map": "Karte", "Political": "Politisch", "Satellite": "Satellit", "Night lights": "Nachtlichter", "Terrain": "Relief",
    "Globe": "Globus", "Flat": "Flach", "Zoom in": "Vergrößern", "Zoom out": "Verkleinern", "Map shape": "Kartenform",
    "Play": "Play", "Pause": "Pause", "Play timeline": "Zeitleiste abspielen", "Pause timeline": "Zeitleiste anhalten", "Year": "Jahr",
    "Back": "Zurück", "Next": "Weiter", "Previous story": "Vorige Geschichte", "Next story": "Nächste Geschichte", "All stories": "Alle Geschichten",
    "Sources and notes": "Quellen und Anmerkungen", "Data": "Daten", "All licences": "Alle Lizenzen", "Close": "Schließen",
    "Stories on a turning world": "Geschichten von einer sich drehenden Welt",
    "short stories about power, money, numbers and people. Each one moves the map for you. Switch between globe and flat map any time to see what changes.":
      "kurze Geschichten über Macht, Geld, Zahlen und Menschen. Jede bewegt die Karte für Sie. Zwischen Globus und flacher Karte lässt sich jederzeit wechseln.",
    "Explore the map freely": "Die Karte frei erkunden",
    "Data and licences": "Daten und Lizenzen",
    "The base map and engine only use material licensed for commercial use. Story layers may use other licences; each one is labelled where it appears.":
      "Grundkarte und Technik verwenden nur Material, das kommerziell genutzt werden darf. Ebenen in Geschichten können andere Lizenzen haben; jede ist dort gekennzeichnet, wo sie erscheint.",
    "Base map and engine (commercial use required)": "Grundkarte und Technik (kommerzielle Nutzung erforderlich)", "Story layers": "Ebenen in Geschichten",
    "Commercial use allowed": "Kommerzielle Nutzung erlaubt", "Non-commercial only": "Nur nicht-kommerziell", "Used with permission": "Mit Genehmigung verwendet", "Source": "Quelle",
    "Explore": "Erkunden", "The world, your way": "Die Welt nach Ihrer Wahl",
    "Drag to turn the world, pinch or scroll to zoom, tap a country to see its name. Switch between political, satellite and night views with the map button. Show a group of countries:":
      "Ziehen dreht die Welt, Zwei-Finger-Geste oder Mausrad zoomt, Antippen zeigt den Namen eines Landes. Über die Karten-Schaltfläche zwischen politischer, Satelliten- und Nachtansicht wechseln. Eine Ländergruppe zeigen:",
    "None": "Keine", "Loading…": "Wird geladen …", "This story could not load": "Diese Geschichte konnte nicht geladen werden",
    "No data": "Keine Daten", "Show": "Zeigen", "Scene": "Szene",
    "line width = value": "Linienbreite = Wert", "line width = tonnes": "Linienbreite = Tonnen", "Tap a country to see only its flows": "Ein Land antippen, um nur seine Ströme zu sehen",
    "Showing {x} only · tap it again for all": "Nur {x} · erneut antippen für alle", "tower height = amount": "Turmhöhe = Menge", "country size = amount": "Ländergröße = Menge",
    "circle area = amount": "Kreisfläche = Menge", "Disputed areas, drawn as seen from {x}": "Umstrittene Gebiete aus Sicht von {x}",
    "Each streak is a parcel of air; bright = faster than 35 m/s": "Jeder Strich ist ein Luftpaket; hell = schneller als 35 m/s",
    "{n} shown": "{n} gezeigt", "Borders as of {y}": "Grenzen von {y}", "Borders of {y}": "Grenzen von {y}", "Not an independent state in {y}": "{y} kein unabhängiger Staat",
    "disputed": "umstritten",
    "Energy": "Energie", "Geopolitics": "Geopolitik", "Economics": "Wirtschaft", "Planet": "Planet", "Statistics": "Statistik", "Rights": "Rechte", "People": "Menschen",
    "European Union": "Europäische Union", "NATO": "NATO", "BRICS": "BRICS", "G7": "G7", "ASEAN": "ASEAN", "OPEC": "OPEC", "African Union": "Afrikanische Union",
    "Language": "Sprache", "Save image": "Bild speichern", "Record video": "Video aufnehmen", "Stop recording": "Aufnahme beenden", "Share": "Teilen", "Embed": "Einbetten",
    "Quiz": "Quiz", "Your city": "Ihre Stadt", "Open in Orbis": "In Orbis öffnen", "Copied": "Kopiert",
    "Copy link": "Link kopieren", "Copy embed code": "Einbettungscode kopieren", "Recording…": "Aufnahme läuft …",
    "Which has more people?": "Wo leben mehr Menschen?", "Where is {x}?": "Wo liegt {x}?", "Tap the country on the map.": "Das Land auf der Karte antippen.",
    "Right!": "Richtig!", "Not quite.": "Nicht ganz.", "Next question": "Nächste Frage", "{n} in a row": "{n} in Folge", "Score": "Punkte",
    "Test yourself: people and places.": "Testen Sie sich: Menschen und Orte.", "That was {x}.": "Das war {x}.",
    "Find your city": "Ihre Stadt finden", "Use my location": "Meinen Standort verwenden", "Type a city": "Stadt eingeben",
    "How far is everything from where you are? Pick a city, or use your location.": "Wie weit ist alles von Ihnen entfernt? Eine Stadt wählen oder den Standort verwenden.",
    "Distances from {x}": "Entfernungen von {x}", "Directly through the Earth from {x} lies {y}.": "Genau gegenüber von {x}, durch die Erde hindurch, liegt {y}.",
    "the open ocean": "offenes Meer", "Write a story": "Geschichte schreiben", "Machine translation, not yet reviewed.": "Maschinelle Übersetzung, noch nicht geprüft.", "your location": "Ihrem Standort", "Location not available": "Standort nicht verfügbar",
    // units used by number formats
    " m b/d": " Mio. b/d", " k b/d": " Tsd. b/d", " bcm": " Mrd. m³", " bcf/d": " Mrd. ft³/d", " bn": " Mrd.", " tn": " Bio.", " m": " Mio.",
    " barrels": " Barrel", " per km²": " pro km²", " yrs": " J.", " M": " Mio.", " B": " Mrd.", "Int$ ": "Int$ "
  }
};
const t = (s, vars) => { let r = (STRINGS[LANG] && STRINGS[LANG][s]) || s; if (vars) for (const k in vars) r = r.replace("{" + k + "}", vars[k]); return r; };
if (LANG === "de" && typeof d3 !== "undefined") d3.formatDefaultLocale({ decimal: ",", thousands: ".", grouping: [3], currency: ["", " €"] });
// translate static markup: elements with data-t (text) or data-t-aria (aria-label)
function applyStaticStrings() {
  document.querySelectorAll("[data-t]").forEach(e => { e.textContent = t(e.dataset.t); });
  document.querySelectorAll("[data-t-aria]").forEach(e => e.setAttribute("aria-label", t(e.dataset.tAria)));
}
