"""Fetch NASA's fixed January/March/May 2022 Kyiv comparison for M7.

The output images are published display composites, not calibrated radiance.
No georeferencing or military-control inference is performed.
"""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / '.cache' / 'ukraine-lights'
OUT = ROOT / 'data' / 'history' / 'ukraine'
PAGE = 'https://science.nasa.gov/earth/earth-observatory/tracking-night-lights-in-ukraine-150002/'
BASE = 'https://assets.science.nasa.gov/dynamicimage/assets/science/esd/eo/images/imagerecords/150000/150002/'


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    observations = []
    for month in ['202201', '202203', '202205']:
        name = f'kyiv_bmhd_{month}_lrg.jpg'
        url = BASE + name + '?crop=faces%2Cfocalpoint&fit=clip&h=921&w=1073'
        raw = CACHE / name
        if not raw.exists():
            with urlopen(Request(url, headers={'User-Agent': 'Orbis source build'}), timeout=90) as response:
                payload = response.read()
            with Image.open(__import__('io').BytesIO(payload)) as im:
                im.verify()
            raw.write_bytes(payload)
        dest = OUT / f'kyiv-lights-{month}.webp'
        with Image.open(raw) as im:
            im.convert('RGB').save(dest, 'WEBP', quality=90, method=6)
        if dest.stat().st_size >= 1_000_000:
            raise ValueError('Image exceeds release file-size gate')
        observations.append(dict(month=month, url=url, sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                                 image=dest.relative_to(ROOT).as_posix(), bytes=dest.stat().st_size))
    metadata = dict(source='nasa-ukraine-lights', asOf='2022-05', retrieved='2026-10-14',
                    title='Kyiv night-light display composites, January/March/May 2022', url=PAGE,
                    credit='NASA Earth Observatory / Joshua Stevens; Black Marble data courtesy Ranjay Shrestha / NASA GSFC',
                    licence='NASA imagery, public use with credit',
                    note='NASA selected cloud-free nights for monthly composites, with Landsat 9 near-infrared context. Display images retained without georeferencing; WebP compression by Orbis. Outdoor lighting may be intentionally dimmed. Light change is not a direct count of displaced people or damaged infrastructure; no front or territory control is inferred.',
                    observations=observations)
    (OUT / 'lights.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Three NASA Kyiv composites validated; observation dates 2022-01, 2022-03, 2022-05.')


if __name__ == '__main__':
    main()
