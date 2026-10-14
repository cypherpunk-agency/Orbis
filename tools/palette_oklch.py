import math
def oklch(L,C,h):
    a=C*math.cos(math.radians(h)); b=C*math.sin(math.radians(h))
    l_=L+0.3963377774*a+0.2158037573*b; m_=L-0.1055613458*a-0.0638541728*b; s_=L-0.0894841775*a-1.2914855480*b
    l,m,s=l_**3,m_**3,s_**3
    r=4.0767416621*l-3.3077115913*m+0.2309699292*s; g=-1.2684380046*l+2.6097574011*m-0.3413193965*s; bb=-0.0041960863*l-0.7034186147*m+1.7076147010*s
    def f(x): x=max(0,min(1,x)); return 1.055*x**(1/2.4)-0.055 if x>0.0031308 else 12.92*x
    return "#%02X%02X%02X"%tuple(round(f(v)*255) for v in (r,g,bb))
def tolch(hexs):
    r,g,b=[int(hexs[i:i+2],16)/255 for i in (1,3,5)]
    def lin(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
    r,g,b=lin(r),lin(g),lin(b)
    l=0.4122214708*r+0.5363325363*g+0.0514459929*b; m=0.2119034982*r+0.6806995451*g+0.1073969566*b; s=0.0883024619*r+0.2817188376*g+0.6299787005*b
    l,m,s=l**(1/3),m**(1/3),s**(1/3)
    L=0.2104542553*l+0.7936177850*m-0.0040720468*s; a=1.9779984951*l-2.4285922050*m+0.4505937099*s; bb=0.0259040371*l+0.7827717662*m-0.8086757660*s
    return round(L,3),round(math.hypot(a,bb),3),round(math.degrees(math.atan2(bb,a))%360)
HUES={"c1":250,"c2":35,"c3":85,"c4":185,"c5":300,"c6":140,"c7":355,"c8":60}
def palette(dark):
    P={}
    if dark:
        P.update(space=oklch(.19,.02,245),ocean=oklch(.33,.045,240),land=oklch(.47,.012,240),border=oklch(.68,.015,240),nodata=oklch(.56,.004,240),muted=oklch(.62,.01,240))
        for i,h in enumerate([240,200,280,160,320]): P[f"t{i}"]=oklch(.47+(i%2)*.012,.014,h)
        for k,h in HUES.items(): P[k]=oklch(.74,.085 if k!="c8" else .055,h)
        # sequential (cividis-like): low = near land, high = pale gold; diverging: equal-L ends through the land
        for i,(L,C,h) in enumerate([(.47,.03,250),(.60,.04,230),(.76,.07,100),(.92,.10,95)]): P[f"s{i}"]=oklch(L,C,h)
        for i,(L,C,h) in enumerate([(.80,.09,250),(.64,.075,250),(.47,.012,240),(.64,.075,40),(.80,.09,40)]): P[f"d{i}"]=oklch(L,C,h)
    else:
        P.update(space=oklch(.93,.008,240),ocean=oklch(.86,.025,230),land=oklch(.975,.004,240),border=oklch(.72,.012,240),nodata=oklch(.88,.003,240),muted=oklch(.65,.01,240))
        for i,h in enumerate([240,200,280,160,320]): P[f"t{i}"]=oklch(.955-(i%2)*.012,.012,h)
        for k,h in HUES.items(): P[k]=oklch(.56,.11 if k!="c8" else .07,h)
        for i,(L,C,h) in enumerate([(.95,.02,95),(.82,.06,95),(.6,.05,230),(.38,.06,250)]): P[f"s{i}"]=oklch(L,C,h)
        for i,(L,C,h) in enumerate([(.45,.12,250),(.68,.08,250),(.975,.004,240),(.68,.09,40),(.45,.13,40)]): P[f"d{i}"]=oklch(L,C,h)
    return P
if __name__=="__main__":
    for d in (True,False):
        P=palette(d); print("DARK" if d else "LIGHT")
        for k,v in P.items(): print(f"  {k:7}{v}  L,C,h={tolch(v)}")
