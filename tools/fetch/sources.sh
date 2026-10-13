#!/bin/sh
# Download raw inputs into .cache/ (gitignored). Re-run to refresh.
set -e
cd "$(dirname "$0")/../.."
mkdir -p .cache/eia .cache/tex .cache/baci
# US EIA international energy data (public domain)
curl -sS -o .cache/eia/INTL.zip https://www.eia.gov/opendata/bulk/INTL.zip && (cd .cache/eia && unzip -o -q INTL.zip)
# NASA Blue Marble NG and Black Marble 2016 via GIBS WMS (NASA, CC0)
for L in BlueMarble_NextGeneration VIIRS_Black_Marble BlueMarble_ShadedRelief_Bathymetry; do
  curl -sS -o ".cache/tex/$L.jpg" "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=$L&STYLES=&CRS=EPSG:4326&BBOX=-90,-180,90,180&WIDTH=8192&HEIGHT=4096&FORMAT=image/jpeg"
done
# CEPII BACI, HS2017 nomenclature, 2017–2024 (Etalab 2.0), ~800 MB
curl -sS -o .cache/baci/BACI_HS17_V202601.zip https://www.cepii.fr/DATA_DOWNLOAD/baci/data/BACI_HS17_V202601.zip
