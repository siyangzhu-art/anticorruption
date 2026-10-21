"""Plot NEW estimation outputs only; the delivered report remains an immutable snapshot."""
from pathlib import Path
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];d=pd.read_stata(R/'rerun/estimation/main/rerun_results.dta')
q=d[d.family.eq('annual')].copy();ks={'d_m4':-4,'d_m3':-3,'d_m2':-2,'d_p0':0,'d_p1':1,'d_p2':2,'d_p3':3,'d_p4':4}
fig,axs=plt.subplots(2,2,figsize=(14,10),sharex=True,sharey=True)
for ax,fe in zip(axs.flat,['I_YEAR','I_PXY','I_CITY_YEAR','I_CITY_PXY']):
 for method,off,col,mk in [('TWFE_fixed',-.06,'#ce8730','s'),('Sun_Abraham',.06,'#247f9f','o')]:
  z=q[q.fe.eq(fe)&q.method.eq(method)&q.term.isin(ks)].copy();z['k']=z.term.map(ks);z=z.sort_values('k')
  ax.errorbar(z.k+off,z.b,yerr=np.array([z.b-z.lo,z.hi-z.b]),fmt=mk,color=col,ls='none',capsize=3,label=method)
  ax.plot(-1+off,0,mk,mfc='white',mec=col)
 ax.axhline(0,color='gray',ls='--');ax.axvline(0,color='#b18b36',ls=':');ax.set_title(fe);ax.set_xticks(range(-4,5));ax.set_xlabel('Years relative to first inspection');ax.set_ylabel('Change in promotion gap (pp)');ax.grid(axis='y',alpha=.15)
axs.flat[0].legend();fig.suptitle('Reproduced C08 annual event study | 95% intervals | Reference k=-1')
out=R/'rerun/figures';out.mkdir(exist_ok=True,parents=True);fig.tight_layout();fig.savefig(out/'annual_four_FE_reproduced.png',dpi=180)
c=R/'rerun/estimation/cumulative/coefficients.dta'
if c.exists():
 z=pd.read_stata(c);design=pd.read_csv(R/'expected/cumulative_design.csv');z=z.merge(design[['model_id','variant','control','H']],on='model_id',validate='1:1');z=z[z.variant.eq('Original')&z.control.eq('full')].sort_values('H')
 fig,ax=plt.subplots(figsize=(8,5));ax.errorbar(z.H,z.b,yerr=np.array([z.b-z.lo,z.hi-z.b]),fmt='o',ls='none',capsize=4);ax.axhline(0,color='gray',ls='--');ax.set_xticks([12,24,36]);ax.set_xlabel('Months per pre/post window');ax.set_ylabel('Change in cumulative promotion gap (pp)');ax.set_title('Horizon-specific samples | 95% intervals');fig.tight_layout();fig.savefig(out/'cumulative_reproduced.png',dpi=180)
print(out)
