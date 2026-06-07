import json, numpy as np, pandas as pd, re, os, tempfile
HOOPS=np.array([[5.25,25.],[88.75,25.]])

def label_game(json_path, pbp):
    j=json.load(open(json_path)); gid=int(j['gameid'])
    g=pbp[(pbp['GAME_ID']==gid)&(pbp['EVENTMSGTYPE'].isin([1,2]))]
    sm={int(r.EVENTNUM):(int(r.PLAYER1_ID),int(r.EVENTMSGTYPE),
        str(r.HOMEDESCRIPTION)+str(r.VISITORDESCRIPTION)) for r in g.itertuples()}
    rows=[]
    for ev in j['events']:
        eid=int(ev['eventId'])
        if eid not in sm: continue
        pid,mt,desc=sm[eid]; ms=ev.get('moments',[])
        if len(ms)<10: continue
        win=ms[-40:]                                  # shot is at the END of the event
        # hoop = nearest rim to the ball at the final valid moment
        lastball=None
        for m in reversed(win):
            if m[5]: lastball=np.array(m[5][0][2:4]); break
        if lastball is None: continue
        hoop=HOOPS[int(np.argmin([np.hypot(*(HOOPS[k]-lastball)) for k in range(2)]))]
        # release = moment in window minimizing ball-shooter distance (the gather)
        best=None; bd=1e9
        for m in win:
            pos=m[5]
            if not pos: continue
            sh=[p for p in pos[1:11] if p[1]==pid]
            if not sh: continue
            s=np.array(sh[0][2:4]); d=np.hypot(*(np.array(pos[0][2:4])-s))
            if d<bd: bd=d; best=(s,pos)
        if best is None: continue
        s,pos=best
        steam=[p[0] for p in pos[1:11] if p[1]==pid][0]
        defs=[np.hypot(*(np.array(p[2:4])-s)) for p in pos[1:11] if p[0]!=steam]
        dist=float(np.hypot(*(s-hoop)))
        if dist>35: continue                          # drop heaves/mislabels
        is3='3PT' in desc
        md=re.search(r"(\d+)'",desc)
        rows.append(dict(game=gid,event=eid,shooter=pid,made=(mt==1),
                         shot_dist=round(dist,2),def_dist=round(min(defs),2) if defs else np.nan,
                         is3=is3,pbp_dist=float(md.group(1)) if md else np.nan))
    return pd.DataFrame(rows)

if __name__=='__main__':
    import sys
    pbp=pd.read_csv('pbp_1516.csv')
    df=label_game('game1/0021500502.json',pbp)
    both=df.dropna(subset=['pbp_dist'])
    err=(both.shot_dist-both.pbp_dist).abs()
    print('shots:',len(df),'| dist median abs err %.2f ft  within3ft %.0f%%'%(err.median(),(err<3).mean()*100))
    print('make rate by distance bucket:')
    df['bucket']=pd.cut(df.shot_dist,[0,4,10,16,23.75,40])
    print(df.groupby('bucket',observed=True).made.agg(['mean','count']).round(3).to_string())
