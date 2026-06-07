import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from scipy.optimize import linear_sum_assignment

EVENT=362
j=json.load(open('game1/0021500502.json'))
ev=j['events'][EVENT]
names={}
for side in ('home','visitor'):
    for p in ev[side]['players']: names[p['playerid']]=p['lastname']
HOOPS=np.array([[5.25,25.0],[88.75,25.0]])

# build per-frame arrays
frames=[]
for m in ev['moments']:
    pos=m[5]
    if not pos or len(pos)<11: continue
    ball=np.array(pos[0][2:4])
    players=[(p[0],p[1],p[2],p[3]) for p in pos[1:11]]
    if len(players)!=10: continue
    frames.append((m[2],ball,players))  # gameclock, ball, players

# identify offense = team of player nearest ball, majority vote
teamcnt={}
for gc,ball,players in frames:
    d=[np.hypot(px-ball[0],py-ball[1]) for (_,_,px,py) in players]
    t=players[int(np.argmin(d))][0]; teamcnt[t]=teamcnt.get(t,0)+1
OFF=max(teamcnt,key=teamcnt.get)
# attacking hoop = nearest hoop to mean ball pos (last 40%)
lateball=np.array([f[1] for f in frames[int(len(frames)*0.6):]])
HOOP=HOOPS[int(np.argmin([np.hypot(*(HOOPS[k]-lateball.mean(0))) for k in range(2)]))]

def split(players):
    off=[(pid,np.array([px,py])) for (t,pid,px,py) in players if t==OFF]
    def_=[(pid,np.array([px,py])) for (t,pid,px,py) in players if t!=OFF]
    return off,def_

# per-frame assignment (Hungarian on expected-defender-position cost)
assigns=[]
for gc,ball,players in frames:
    off,def_=split(players)
    if len(off)!=5 or len(def_)!=5: assigns.append(None); continue
    C=np.zeros((5,5))
    for i,(_,d) in enumerate(def_):
        for k,(_,o) in enumerate(off):
            e=o+0.12*(HOOP-o)            # expected defender spot: between man & hoop
            C[i,k]=np.linalg.norm(d-e)
    ri,ci=linear_sum_assignment(C)
    assigns.append({ri[x]:ci[x] for x in range(5)})

# temporal smoothing: sticky majority over window
W=12
sm=[]
for n in range(len(assigns)):
    if assigns[n] is None: sm.append(None); continue
    votes={}
    for k in range(max(0,n-W),min(len(assigns),n+W)):
        a=assigns[k]
        if a is None: continue
        for di,oi in a.items(): votes.setdefault(di,{}).setdefault(oi,0); votes[di][oi]+=1
    sm.append({di:max(v,key=v.get) for di,v in votes.items()})

def beaten(d,o,hoop):
    u=hoop-o; nu=np.linalg.norm(u)+1e-6; uu=u/nu
    v=d-o
    proj=np.dot(v,uu)              # + = defender toward hoop (good contain)
    perp=np.linalg.norm(v-proj*uu) # lateral beat
    sep=np.linalg.norm(v)
    openness= sep + max(0,-proj)*1.6 + perp*0.9 - max(0,proj)*0.6
    return float(np.clip(100/(1+np.exp(-0.5*(openness-6))),0,100))

print('OFF team:',OFF,'attacking hoop:',HOOP,'frames:',len(frames))
# sample contact sheet
import matplotlib.gridspec as gs
idxs=[int(len(frames)*f) for f in (0.15,0.35,0.55,0.7,0.85,0.95)]
fig=plt.figure(figsize=(15,9)); 
def beat_color(b):
    t=b/100; return (0.30+0.62*t, 0.55-0.30*t, 0.47-0.30*t)
for n_,ii in enumerate(idxs):
    ax=fig.add_subplot(3,2,n_+1)
    gc,ball,players=frames[ii]; off,def_=split(players); a=sm[ii]
    ax.add_patch(Rectangle((0,0),94,50,fill=False,ec='#888',lw=1))
    ax.plot([47,47],[0,50],color='#bbb',lw=0.8)
    for hx,hy in HOOPS: ax.add_patch(Circle((hx,hy),0.75,fill=False,ec='#c99',lw=1.2))
    # tethers + beaten
    maxb=0; maxname=''
    if a:
        for di,oi in a.items():
            d=def_[di][1]; o=off[oi][1]; b=beaten(d,o,HOOP)
            ax.plot([d[0],o[0]],[d[1],o[1]],color=beat_color(b),lw=1+3*b/100,zorder=2)
            if b>maxb: maxb=b; maxname=names.get(off[oi][0],'?')
    for _,o in off: ax.add_patch(Circle(o,1.1,color='#2E8B72',zorder=3))
    for _,d in def_: ax.add_patch(Circle(d,1.1,color='#9a9486',zorder=3))
    ax.add_patch(Circle(ball,0.7,color='#C97A2A',zorder=4))
    ax.set_xlim(-2,96); ax.set_ylim(-2,52); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(f'gc {gc:.0f}s  most-beaten: {maxname} {maxb:.0f}',fontsize=10)
plt.tight_layout(); plt.savefig('matchup_contact.png',dpi=80); print('saved contact sheet')

# ================= ANIMATION (portfolio palette) =================
import imageio
from matplotlib.patches import Arc
BG='#EDEAE0'; INK='#1B3C30'; SAGE='#6E8A7E'; STONE='#A39A88'; EARTH='#7A5E30'; TEAL='#2E8B72'
def ramp(b):
    t=b/100
    if t<0.5:  # pine -> earth
        s=t/0.5; c0=(0.24,0.39,0.30); c1=(0.48,0.37,0.19)
    else:      # earth -> warm red
        s=(t-0.5)/0.5; c0=(0.48,0.37,0.19); c1=(0.78,0.27,0.16)
    return tuple(c0[k]+(c1[k]-c0[k])*s for k in range(3))

def hoop_court(ax):
    ax.add_patch(Rectangle((0,0),94,50,fill=False,ec='#B8B4A8',lw=1.4))
    ax.plot([47,47],[0,50],color='#B8B4A8',lw=1)
    ax.add_patch(Arc((47,25),12,12,angle=0,theta1=-90,theta2=90,ec='#B8B4A8',lw=1))
    hx=88.75
    ax.add_patch(Circle((hx,25),0.75,fill=False,ec=EARTH,lw=1.6))
    ax.add_patch(Rectangle((75,17),19,16,fill=False,ec='#B8B4A8',lw=1))   # paint
    ax.add_patch(Arc((75,25),12,12,angle=0,theta1=-90,theta2=90,ec='#B8B4A8',lw=1))  # FT circle
    ax.add_patch(Arc((hx,25),47.5,47.5,angle=0,theta1=112,theta2=248,ec='#B8B4A8',lw=1))  # 3pt arc
    ax.plot([94,80.2],[3,3],color='#B8B4A8',lw=1); ax.plot([94,80.2],[47,47],color='#B8B4A8',lw=1)  # corners

W,H=940,520
imgs=[]
step=2
for ii in range(0,len(frames),step):
    gc,ball,players=frames[ii]; off,def_=split(players); a=sm[ii]
    fig=plt.figure(figsize=(W/100,H/100),dpi=100); ax=fig.add_axes([0,0,1,1])
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    hoop_court(ax)
    maxb=0; maxname=''; maxpos=None
    if a:
        for di,oi in a.items():
            d=def_[di][1]; o=off[oi][1]; b=beaten(d,o,HOOP)
            ax.plot([d[0],o[0]],[d[1],o[1]],color=ramp(b),lw=1.2+4.5*b/100,zorder=2,solid_capstyle='round',alpha=0.95)
            if b>maxb: maxb=b; maxname=names.get(off[oi][0],'?'); maxpos=o
    for _,o in off: ax.add_patch(Circle(o,1.25,color=TEAL,zorder=4,ec='#1f6b56',lw=0.6))
    for _,d in def_: ax.add_patch(Circle(d,1.25,color=STONE,zorder=4,ec='#7d7563',lw=0.6))
    ax.add_patch(Circle(ball,0.75,color=EARTH,zorder=5))
    if maxb>72 and maxpos is not None:
        ax.text(maxpos[0],maxpos[1]+2.6,f'{maxname.upper()} OPEN',color='#9c3a22',
                fontsize=9,ha='center',weight='bold',family='monospace',zorder=6)
    # HUD
    ax.text(48,53.3,'MATCHUP ENGINE',color=EARTH,fontsize=11,family='monospace',weight='bold',ha='left')
    ax.text(48,50.9,'who guards whom',color=INK,fontsize=8.5,family='monospace',ha='left')
    ax.text(92,53.3,f'{gc:0.0f}s',color=INK,fontsize=12,family='monospace',ha='right',weight='bold')
    ax.text(92,50.9,f'biggest gap  {maxname.upper()} {maxb:0.0f}',color=ramp(maxb),fontsize=9,family='monospace',ha='right',weight='bold')
    ax.set_xlim(43,97); ax.set_ylim(-3,56); ax.axis('off'); ax.set_aspect('equal')
    fig.canvas.draw()
    buf=np.frombuffer(fig.canvas.buffer_rgba(),dtype=np.uint8).reshape(int(fig.bbox.height),int(fig.bbox.width),4)[...,:3]
    imgs.append(buf.copy()); plt.close(fig)
imageio.mimsave('matchup_engine.gif',imgs,fps=12,loop=0)
print('GIF frames:',len(imgs),'saved matchup_engine.gif')
