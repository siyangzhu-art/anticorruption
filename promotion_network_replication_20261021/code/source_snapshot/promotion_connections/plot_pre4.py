from pathlib import Path
import sys
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20\event_study_individual_FE')
O=B/'display_pre4';O.mkdir(exist_ok=True)
R=pd.read_csv(B/'event_coefficients_validated.csv')
M=pd.read_csv(B/'model_summary.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False})
selected=[]
for mid,name,label in [(7,'01_individual_year_pre4.png','Individual + year fixed effects'),(8,'02_individual_province_year_pre4.png','Individual + province-by-year fixed effects')]:
 q=R[(R.model_id==mid)&(R.estimand=='change')&(R.relative_year>=-4)].sort_values('relative_year').copy()
 assert list(q.relative_year)==list(range(-4,5))
 selected.append(q)
 z=q[~q.reference];m=M[M.model_id==mid].iloc[0]
 fig,ax=plt.subplots(figsize=(11,7))
 ax.axhline(0,color='gray',ls='--',lw=1)
 ax.axvline(-.5,color='#b58a34',ls=':',lw=1)
 ax.errorbar(z.relative_year,z.b,yerr=[z.b-z.lo,z.hi-z.b],fmt='o',ls='none',ms=6,capsize=4,color='#287c9e')
 ax.plot(-1,0,marker='o',ls='none',mfc='white',mec='#287c9e',ms=7)
 ax.set_xticks(range(-4,5));ax.set_xlim(-4.4,4.4)
 ax.set_xlabel('Years relative to first provincial inspection')
 ax.set_ylabel('Change in connection-related promotion gap (pp)')
 ax.grid(axis='y',alpha=.15)
 ax.set_title(label+'\nReference: k = -1 | 95% province-clustered CIs',fontsize=14,pad=17)
 fig.subplots_adjust(left=.13,right=.97,top=.83,bottom=.26)
 fig.text(.07,.035,f'Display: four pre-inspection periods (-4 to -1). Full-sample estimates unchanged; N={int(m.N):,}.\nControls: age profile, tenure, rank and current role; either provincial-leader tie.\nk=+4 is supported by the 2013 inspection cohort only. Reference has no estimated CI.\nPointwise CIs; no connecting lines. Conditional associations, not causal inspection effects.',fontsize=9)
 fig.savefig(O/name,dpi=180,facecolor='white');plt.close(fig)
pd.concat(selected).to_csv(O/'displayed_coefficients.csv',index=False,encoding='utf-8-sig')
(O/'README.txt').write_text('Display crop only: model 7 and 8 full-sample estimates; k=-4,...,+4. Four pre periods include reference -1. No regression re-estimation. +4 has only 2013-cohort support.\n',encoding='utf8')
print(O)
