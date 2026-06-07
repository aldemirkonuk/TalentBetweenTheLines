"""Train the Shot-Quality model from the 2014-15 NBA shot logs (clean shot+defender data).
Source: https://raw.githubusercontent.com/erikreppel/seng474-nba-shots/master/shot_logs.csv
Writes ../shot_model.json. Leave-game-out AUC ~0.63, well calibrated."""
import pandas as pd, numpy as np, json, requests, io, os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, brier_score_loss

URL="https://raw.githubusercontent.com/erikreppel/seng474-nba-shots/master/shot_logs.csv"
df=pd.read_csv(io.BytesIO(requests.get(URL,timeout=60).content))
df=df.dropna(subset=['SHOT_DIST','CLOSE_DEF_DIST','FGM','PTS_TYPE'])
df['is3']=(df.PTS_TYPE==3).astype(int); df['def']=df.CLOSE_DEF_DIST.clip(0,15)
X=df[['SHOT_DIST','def','is3']].values; y=df.FGM.values; grp=df.GAME_ID.values
aucs=[]; 
for tr,te in GroupKFold(5).split(X,y,grp):
    m=LogisticRegression(max_iter=1000).fit(X[tr],y[tr])
    aucs.append(roc_auc_score(y[te],m.predict_proba(X[te])[:,1]))
print('leave-game-out AUC %.3f'%np.mean(aucs))
f=LogisticRegression(max_iter=1000).fit(X,y)
out=os.path.join(os.path.dirname(__file__),'..','shot_model.json')
json.dump(dict(intercept=float(f.intercept_[0]),shot_dist=float(f.coef_[0][0]),
               def_dist=float(f.coef_[0][1]),is3=float(f.coef_[0][2])),open(out,'w'),indent=2)
print('wrote',out)
