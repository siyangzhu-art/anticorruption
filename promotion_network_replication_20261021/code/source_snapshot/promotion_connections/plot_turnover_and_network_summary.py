"""One figure combining the already-computed turnover and network summaries."""
from pathlib import Path
import sys,shutil
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20\patron_retention_audit_2026_10_21')
O=B/'combined_turnover_network_figure';O.mkdir(exist_ok=True)
r=pd.read_csv(B/'symmetric_retention_summary.csv');r=r[r['sample'].eq('Paired clear rosters')].copy()
n=pd.read_csv(B/'departed_leaders/departed_comparison.csv')
r['departure_pct']=100*r.not_recorded_S_or_G/r.baseline_leaders
assert len(r)==6 and len(n)==6
assert not r.duplicated(['horizon_months','phase']).any() and not n.duplicated(['horizon_months','phase']).any()
for h in [12,24,36]:
    assert r[r.horizon_months.eq(h)].baseline_leaders.nunique()==1
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,2,figsize=(15,7.6),gridspec_kw={'width_ratios':[1,1.08]})
colors={'Before':'#287f9d','After':'#ce8730'}
for phase,offset in [('Before',-.18),('After',.18)]:
    q=r[r.phase.eq(phase)].sort_values('horizon_months');x=np.arange(3)+offset
    bars=axs[0].bar(x,q.departure_pct,width=.30,color=colors[phase],alpha=.93,zorder=3)
    for bar,z in zip(bars,q.itertuples()):
        axs[0].text(bar.get_x()+bar.get_width()/2,bar.get_height()+1.3,
            f'{z.departure_pct:.1f}%\n({z.not_recorded_S_or_G}/{z.baseline_leaders})',
            ha='center',va='bottom',fontsize=10,color='#333333')
    q=n[n.phase.eq(phase)].sort_values('horizon_months');x=np.arange(3)+offset
    axs[1].errorbar(x,q.mean_connections,yerr=[q.mean_connections-q.mean_ci_low,q.mean_ci_high-q.mean_connections],
        fmt='o' if phase=='Before' else 's',linestyle='none',capsize=5,markersize=7,color=colors[phase],zorder=3)
    for xx,z in zip(x,q.itertuples()):
        axs[1].annotate(f'{z.mean_connections:.2f}',xy=(xx,z.mean_connections),xytext=(0,11),
            textcoords='offset points',ha='center',fontsize=10,color=colors[phase],
            bbox=dict(facecolor='white',edgecolor='none',alpha=.85,pad=1))
axs[0].set_title('A. Provincial leaders no longer in either office',loc='left',fontsize=12,pad=14)
axs[0].set_ylabel('Departure rate (%)');axs[0].set_ylim(0,78);axs[0].set_yticks(np.arange(0,81,20))
axs[0].set_xticks(range(3),['12 months','24 months','36 months'])
axs[1].set_title('B. Departing leaders: city-official connections',loc='left',fontsize=12,pad=14)
axs[1].set_ylabel('Mean confirmed connections per departing leader')
axs[1].set_xticks(range(3),['12 months\nn = 8 / 7','24 months\nn = 22 / 16','36 months\nn = 29 / 29'])
axs[1].set_ylim(0,4.65);axs[1].set_yticks(np.arange(0,4.6,1))
for ax in axs:
    ax.grid(axis='y',color='#e7ebee',lw=.8,zorder=0);ax.set_axisbelow(True);ax.set_xlim(-.60,2.60)
fig.suptitle('Provincial leadership turnover and departing leaders\N{RIGHT SINGLE QUOTATION MARK} networks',fontsize=19,x=.5,y=.965)
fig.text(.5,.901,'Before versus after first central inspection | Equal-length 12-, 24- and 36-month windows',ha='center',fontsize=12,color='#555555')
fig.legend(handles=[Patch(facecolor=colors['Before'],label='Before inspection'),Patch(facecolor=colors['After'],label='After inspection')],
           loc='upper center',bbox_to_anchor=(.5,.875),ncol=2,frameon=False,fontsize=11)
fig.subplots_adjust(top=.75,bottom=.30,left=.075,right=.98,wspace=.28)
foot=[
 'A: All exit reasons combined. Governor-to-secretary moves within the same province count as retained. Counts shown in parentheses.',
 'B: Dots/squares show means; whiskers are 95% province-block bootstrap percentile CIs. n = departing leaders, before / after.',
 'Connections: prior cowork ties of at least six months, formed before 2012 and before the joint current assignment; measured at window start.',
 'Unknown ties are not coded zero. Municipalities lack a comparable city-principal pool and are excluded from B.',
 'Province frames (12 / 24 / 36 months): A = 30 / 27 / 26; B = 27 / 24 / 22. Frames are matched before/after within each horizon.',
 'Descriptive comparisons; neither overlapping CIs nor insignificant differences establish equality. First inspection is not a common 2012 cutoff.'
]
for i,line in enumerate(foot):fig.text(.06,.205-i*.027,line,fontsize=9,color='#444444',va='top')
png=O/'provincial_turnover_and_connections_before_after.png'
fig.savefig(png,dpi=200,facecolor='white');fig.savefig(O/'provincial_turnover_and_connections_before_after.svg',facecolor='white');plt.close(fig)
r.to_csv(O/'panel_A_turnover_rates.csv',index=False,encoding='utf-8-sig');n.to_csv(O/'panel_B_departing_leader_connections.csv',index=False,encoding='utf-8-sig')
shutil.copy2(__file__,O/Path(__file__).name)
print(png)
