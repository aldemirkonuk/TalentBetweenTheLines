import json, numpy as np, pandas as pd, re, os, tempfile, glob, py7zr, sys
HOOPS=np.array([[5.25,25.],[88.75,25.]])

def extract(p):
    if p.endswith('.json'): return p
    d=tempfile.mkdtemp()
    with py7zr.SevenZipFile(p) as z: z.extractall(path=d)
    return os.path.join(d,os.listdir(d)[0])

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
        win=ms[-50:]
        # ball z apex => release just before it
        zs=[(k,m[5][0][4]) for k,m in enumerate(win) if m[5]]
        if not zs: continue
        apex=max(zs,key=lambda t:t[1])[0]
        # release: last moment <=apex where shooter within 4ft of ball
        rel=None
        for k in range(apex,-1,-1):
            pos=win[k][5]
            if not pos: continue
            sh=[p for p in pos[1:11] if p[1]==pid]
            if not sh: continue
            s=np.array(sh[0][2:4])
            if np.hypot(*(np.array(pos[0][2:4])-s))<4: rel=(s,pos); break
        if rel is None:   # fallback: min ball-shooter dist
            bd=1e9
            for m in win:
                pos=m[5]
                if not pos: continue
                sh=[p for p in pos[1:11] if p[1]==pid]
                if not sh: continue
                s=np.array(sh[0][2:4]); d=np.hypot(*(np.array(pos[0][2:4])-s))
                if d<bd: bd=d; rel=(s,pos)
        if rel is None: continue
        s,pos=rel
        hoop=HOOPS[int(np.argmin([np.hypot(*(HOOPS[k]-s)) for k in range(2)]))]
        dist=float(np.hypot(*(s-hoop)))
        if dist>35: continue
        steam=[p[0] for p in pos[1:11] if p[1]==pid][0]
        defs=[np.hypot(*(np.array(p[2:4])-s)) for p in pos[1:11] if p[0]!=steam]
        md=re.search(r"(\d+)'",desc)
        rows.append(dict(game=gid,event=eid,made=int(mt==1),shot_dist=dist,
                         def_dist=float(min(defs)) if defs else np.nan,
                         is3=int('3PT' in desc),pbp_dist=float(md.group(1)) if md else np.nan))
    return pd.DataFrame(rows)

if __name__=='__main__':
    pbp=pd.read_csv('pbp_1516.csv')
    files=['game1/0021500502.json']+sorted(glob.glob('/sessions/fervent-clever-meitner/mnt/Claude/Projects/Portfolio/data/tracking/*.7z'))[:6]
    alld=[]
    for f in files:
        try:
            d=label_game(extract(f),pbp); alld.append(d); print('ok',os.path.basename(f),len(d))
        except Exception as e: print('ERR',os.path.basename(f),str(e)[:60])
    df=pd.concat(alld,ignore_index=True).dropna(subset=['def_dist'])
    df.to_csv('shots_dataset.csv',index=False)
    both=df.dropna(subset=['pbp_dist']); both=both[both.pbp_dist>3]  # jumpers
    err=(both.shot_dist-both.pbp_dist).abs()
    print('TOTAL shots:',len(df),'| jumper dist median err %.2f ft within3ft %.0f%%'%(err.median(),(err<3).mean()*100))
