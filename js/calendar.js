// ---------- calendars and deep time ----------
// Years are stored as astronomical years (1 BC = 0, 2 BC = -1, …) and dates as yyyymmdd numbers in the
// proleptic Gregorian calendar. This module only changes how they are shown.
const Cal = (function(){
  const MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  // "27 BC", "AD 117" (era shown below AD 1000 or when asked), "1648"
  function year(y, era){ y = +y; if (y <= 0) return (1 - y) + " BC"; return (era || y < 1000) ? "AD " + y : String(y); }
  // Julian day number of a proleptic Gregorian or Julian date (Fliegel–Van Flandern / Meeus)
  function jdn(y, m, d, julian){
    const a = Math.floor((14 - m) / 12), yy = y + 4800 - a, mm = m + 12 * a - 3;
    return julian ? d + Math.floor((153 * mm + 2) / 5) + 365 * yy + Math.floor(yy / 4) - 32083
                  : d + Math.floor((153 * mm + 2) / 5) + 365 * yy + Math.floor(yy / 4) - Math.floor(yy / 100) + Math.floor(yy / 400) - 32045;
  }
  function fromJdn(J, julian){
    let b, c;
    if (julian){ b = 0; c = J + 32082; }
    else { const a = J + 32044; b = Math.floor((4 * a + 3) / 146097); c = a - Math.floor(146097 * b / 4); }
    const d = Math.floor((4 * c + 3) / 1461), e = c - Math.floor(1461 * d / 4), m = Math.floor((5 * e + 2) / 153);
    return [100 * b + d - 4800 + Math.floor(m / 10), m + 3 - 12 * Math.floor(m / 10), e - Math.floor((153 * m + 2) / 5) + 1];
  }
  const split = n => { n = +n; const s = n < 0 ? -1 : 1, a = Math.abs(n); return [s * Math.floor(a / 10000), Math.floor(a / 100) % 100, a % 100]; };
  // a yyyymmdd date in the main (Gregorian) style: "2 Apr 2025", "15 Mar 44 BC"
  function date(n){ const [y, m, d] = split(n); return d + " " + MON[m - 1] + " " + year(y); }
  // the same day in another calendar: "julian", "auc" (years since the founding of Rome), or any Intl calendar
  // (islamic-umalqura, hebrew, chinese, japanese, persian, buddhist, ethiopic, coptic, indian)
  function other(n, cal, isDate){
    if (cal === "auc"){ const y = isDate ? split(n)[0] : +n; return "AUC " + (y + 753); }
    if (!isDate) return "";
    const [y, m, d] = split(n);
    if (cal === "julian"){ const [jy, jm, jd] = fromJdn(jdn(y, m, d, false), true); return jd + " " + MON[jm - 1] + " " + year(jy) + " (Julian)"; }
    try { const x = new Date(Date.UTC(2000, m - 1, d)); x.setUTCFullYear(y);
      return new Intl.DateTimeFormat("en-GB-u-ca-" + cal, { dateStyle: "long", timeZone: "UTC" }).format(x); }
    catch (e) { return ""; }
  }
  // convert a Julian-calendar yyyymmdd to the Gregorian yyyymmdd used for storage
  function julianToGregorian(n){ const [y, m, d] = split(n), [gy, gm, gd] = fromJdn(jdn(y, m, d, true), false); return gy * 10000 + Math.sign(gy || 1) * (gm * 100 + gd); }
  return { MON, year, date, other, julianToGregorian, jdn, fromJdn };
})();
