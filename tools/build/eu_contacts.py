"""Build legible local contact sheets for manual review; no production assets."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[2]/'.cache/roadmap-review/M5'
for story in root.glob('eu-*'):
 for view in ['desktop','mobile']:
  paths=sorted((story/view).glob('*.png'))
  w,h,n=(640,425,6)if view=='desktop'else(390,875,4)
  for start in range(0,len(paths),n):
   chunk=paths[start:start+n];out=Image.new('RGB',(2*w,h*((len(chunk)+1)//2)),'white');draw=ImageDraw.Draw(out)
   for i,p in enumerate(chunk):
    at=((i%2)*w,(i//2)*h);out.paste(ImageOps.contain(Image.open(p),(w,h-28)),at);draw.text((at[0]+4,at[1]+h-24),p.name,fill='black')
   out.save(story/(view+'-contact-'+str(start//n+1)+'.png'))
