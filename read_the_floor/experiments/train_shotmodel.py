import pandas as pd, numpy as np, json
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, brier_score_loss
df=pd.read_csv('shots_dataset.csv').dropna(subset=['def_dist'])
df['def_dist']=df.def_dist.clip(0,15)
X=df[['shot_dist','def_dist','is3']].values; y=df.made.values; groups=df.game.values
def cv(model):
    aucs=[];briers=[];oof=np.zeros(len(y))
    for tr,te in GroupKFold(n_splits=df.game.nunique()).split(X,y,groups):
        model.fit(X[tr],y[tr]); p=model.predict_proba(X[te])[:,1]; oof[te]=p
        if len(set(y[te]))>1: aucs.append(roc_auc_score(y[te],p))
        briers.append(brier_score_loss(y[te],p))
    return np.mean(aucs),np.mean(briers),oof
for name,m in [('logreg',LogisticRegression(max_iter=1000)),
               ('gbm',GradientBoostingClassifier(n_estimators=120,max_depth=3,learning_rate=0.05))]:
    auc,br,oof=cv(m); 
    print('%s  leave-game-out AUC %.3f  Brier %.3f'%(name,auc,br))
# calibration with gbm oof
df['p']=oof
print('\\ncalibration (predicted vs actual make%):')
df['pb']=pd.cut(df.p,[0,.3,.4,.5,.6,1])
print(df.groupby('pb',observed=True).agg(pred=('p','mean'),actual=('made','mean'),n=('made','size')).round(3).to_string())
# fit final logreg on all, save coefficients -> expected points model
final=LogisticRegression(max_iter=1000).fit(X,y)
coef=dict(intercept=float(final.intercept_[0]),
          shot_dist=float(final.coef_[0][0]),def_dist=float(final.coef_[0][1]),is3=float(final.coef_[0][2]))
json.dump(coef,open('shot_model.json','w'),indent=2)
print('\\nsaved shot_model.json:',coef)
# expected points sanity
def ep(d,dd,is3):
    z=coef['intercept']+coef['shot_dist']*d+coef['def_dist']*min(dd,15)+coef['is3']*is3
    p=1/(1+np.exp(-z)); return p,p*(3 if is3 else 2)
for (d,dd,i3,lbl) in [(2,2,0,'open layup'),(2,1,0,'contested layup'),(24,6,1,'open 3'),(24,2,1,'contested 3'),(18,4,0,'mid 18ft')]:
    p,e=ep(d,dd,i3); print('  %-16s P(make)=%.2f  expPts=%.2f'%(lbl,p,e))
