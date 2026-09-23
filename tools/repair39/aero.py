"""Shared closed cambered foil builder. Visual geometry, not an aero solver."""
from .common import *


def foil(stations,color='metal',samples=18,camber=.018):
    """Stations: (span_x, chord, centre_z, height_y, thickness_ratio, twist_deg).

    Leading edge is -Z; quarter-chord twist and progressively thinner tips are
    explicit. Trailing edge keeps finite thickness so exports have no zero faces.
    """
    us=[.5-.5*math.cos(math.pi*j/samples) for j in range(samples+1)]
    sec=[(u,1) for u in us]+[(u,-1) for u in reversed(us)]
    pp=[]
    for x,chord,cz,cy,tr,tw in stations:
        a=math.radians(tw)
        for u,s in sec:
            half=5*tr*chord*(.2969*math.sqrt(u)-.1260*u-.3516*u*u+.2843*u**3-.1036*u**4)+.00025
            yy=camber*chord*math.sin(math.pi*u)+s*half;zz=(u-.25)*chord
            pp.append([x,cy+yy*math.cos(a)-zz*math.sin(a),cz+yy*math.sin(a)+zz*math.cos(a)-chord*.25])
    n=len(sec);ff=[]
    for j in range(len(stations)-1):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff += [list(range(n-1,-1,-1)),list(range((len(stations)-1)*n,len(stations)*n))]
    return mesh(pp,ff,C(color),smooth_angle=34)
