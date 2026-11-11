from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
out=Path(__file__).resolve().parents[1] / 'figures'
out.mkdir(parents=True, exist_ok=True)
fig, ax=plt.subplots(figsize=(12,6.8))
ax.set_xlim(0,12);ax.set_ylim(0,7);ax.axis('off')
fig.patch.set_facecolor('white')

def box(x,y,w,h,text):
    patch=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02,rounding_size=.11',
                         linewidth=1.3,edgecolor='#26354b',facecolor='#f5f7fb')
    ax.add_patch(patch)
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=10.5,color='#182237')

def arr(x0,y0,x1,y1):
    ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1),arrowstyle='-|>',mutation_scale=15,
                                 linewidth=1.4,color='#4a6578'))
ax.text(6,6.55,'Reproducible log anomaly detection pipeline',ha='center',fontsize=16,weight='bold')
box(.25,4.95,2.1,1.0,'Sanitized synthetic\nauthentication logs')
box(2.95,4.95,1.9,1.,'Strict log parser')
box(5.45,4.95,2.3,1.,'30-minute windows\n+ six features')
box(8.48,5.6,2.5,.86,'Rule-based detector')
box(8.48,4.3,2.5,.86,'Real Isolation Forest')
box(9.0,2.82,1.6,.72,'OR hybrid')
box(3.6,2.72,2.48,1.,'Injection labels\n(5 known bursts)')
box(7.55,1.28,3.5,.76,'Evaluation: TP / FP / FN / TN + P / R / F1')
box(3.48,1.28,2.5,.76,'CSV + figures')
arr(2.35,5.45,2.95,5.45)
arr(4.85,5.45,5.45,5.45)
arr(7.75,5.45,8.48,5.98)
arr(7.75,5.45,8.48,4.72)
# Route rule output around the model boxes instead of through the lower box.
ax.plot([10.98, 11.48, 11.48], [6.03, 6.03, 3.16], color='#4a6578', linewidth=1.4)
arr(11.48,3.16,10.60,3.16)
arr(9.7,4.3,9.8,3.54)
arr(9.8,2.82,9.36,2.04)
arr(6.08,3.17,7.55,1.72)
arr(7.55,1.66,5.98,1.66)
ax.text(6,0.42,'Exploratory in-sample evaluation; no held-out test split',ha='center',fontsize=10.5,style='italic')
fig.tight_layout()
for ext in ['png','svg']:
 fig.savefig(out/f'00_pipeline_architecture.{ext}',bbox_inches='tight',dpi=180)
plt.close(fig)
