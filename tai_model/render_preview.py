"""Generates charts + a standalone report_preview.html from model.py + parameters.csv.
The Quarto report (report.qmd) mirrors this exactly; this is the viewable twin."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import model as M

P=M.load_params(); s,d,cen=M.run_central(P); _,_,mc=M.run_mc(P,200000)
NAVY='#1f3864'; ACC='#c00000'; GRN='#2e7d32'; AMB='#b8860b'; LT='#e9eef6'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':'#888'})

# ---- chart 1: method comparison (P5-P95 ranges, log x) ----
order=["DeepSeek bottom-up (GPU = token)","GPU macro average","Epoch token-capacity","Anthropic model-based","Pooled (model + Epoch)"]
fig,ax=plt.subplots(figsize=(7.2,3.0))
for i,name in enumerate(order):
    v=mc[name]/1e12; p5,p50,p95=np.percentile(v,[5,50,95])
    col=ACC if 'DeepSeek' in name else (NAVY if 'Pooled' in name else '#5b7aa8')
    ax.plot([p5,p95],[i,i],color=col,lw=4,alpha=.5,solid_capstyle='round')
    ax.plot(p50,i,'o',color=col,ms=8)
    ax.text(p95*1.05,i,f"${p50:.0f}T",va='center',fontsize=8,color=col)
ax.axvline(2,color='#999',ls='--',lw=1); ax.text(2,-0.7,'doc $2T',fontsize=7,color='#999',ha='center')
ax.set_yticks(range(len(order))); ax.set_yticklabels([n.replace(' (GPU = token)','').replace(' (model + Epoch)','') for n in order])
ax.set_xscale('log'); ax.set_xlabel('2031 revenue (US$ trillions, log scale) - dot = median, bar = P5-P95')
ax.set_title('2031 frontier-AI revenue by method',color=NAVY,weight='bold',fontsize=11)
ax.spines[['top','right']].set_visible(False); ax.invert_yaxis()
plt.tight_layout(); plt.savefig('fig_methods.png',dpi=160); plt.close()

# ---- chart 2: pooled distribution ----
fig,ax=plt.subplots(figsize=(7.2,3.0))
v=np.clip(mc["Pooled (model + Epoch)"]/1e12,0,80)
ax.hist(v,bins=80,color=NAVY,alpha=.85)
p5,p50,p95=np.percentile(mc["Pooled (model + Epoch)"]/1e12,[5,50,95]); mean=(mc["Pooled (model + Epoch)"]/1e12).mean()
ax.axvline(p50,color=GRN,ls='--',lw=1.8,label=f'median ${p50:.0f}T')
ax.axvline(mean,color=AMB,ls=':',lw=1.8,label=f'mean ${mean:.0f}T')
ax.axvspan(p5,p95,color=GRN,alpha=.07,label=f'P5-P95 ${p5:.0f}-{p95:.0f}T')
ax.set_xlabel('US$ trillions'); ax.set_ylabel('trials')
ax.set_title('Pooled 2031 revenue (model-based + Epoch)',color=NAVY,weight='bold',fontsize=11)
ax.legend(fontsize=8); ax.spines[['top','right']].set_visible(False)
plt.tight_layout(); plt.savefig('fig_pooled.png',dpi=160); plt.close()
print("charts written")

# ---- HTML preview ----
def fmt(x):
    ax=abs(x)
    if ax>=1e12: return f"${x/1e12:,.1f}T"
    if ax>=1e9: return f"${x/1e9:,.1f}B"
    if ax>=1e3: return f"${x:,.0f}"
    return f"{x:,.3g}"
# raw data table
rows=""
for k,v in P.items():
    rng = "" if v["low"] is None else f"{v['low']:,.4g} - {v['high']:,.4g}"
    src = f'<a href="{v["url"]}">{v["source"]}</a>' if v["url"] else v["source"]
    val = f"{v['value']:,.4g}"
    rows+=f"<tr><td>{v['group']}</td><td>{v['parameter']}</td><td style='text-align:right'>{val}</td><td style='text-align:right'>{rng}</td><td>{v['dist']}</td><td>{v['unit']}</td><td>{src}</td><td style='font-size:11px;color:#555'>{v['note']}</td></tr>"
# results table
resrows=""
for name,fn in M.METHODS:
    c=cen[name]; v=mc[name]; p=np.percentile(v,[5,50,95])
    resrows+=f"<tr><td>{name}</td><td style='text-align:right'>{c/1e12:,.1f}</td><td style='text-align:right'>{p[0]/1e12:,.1f}</td><td style='text-align:right'>{p[1]/1e12:,.1f}</td><td style='text-align:right'>{p[2]/1e12:,.1f}</td></tr>"
pv=mc["Pooled (model + Epoch)"]; pp=np.percentile(pv,[5,50,95])
resrows+=f"<tr style='font-weight:bold;background:{LT}'><td>Pooled (model + Epoch)</td><td style='text-align:right'>-</td><td style='text-align:right'>{pp[0]/1e12:,.1f}</td><td style='text-align:right'>{pp[1]/1e12:,.1f}</td><td style='text-align:right'>{pp[2]/1e12:,.1f}</td></tr>"
html=f"""<!doctype html><html><head><meta charset=utf-8><title>Economics of TAI - 2031 revenue</title>
<style>body{{font-family:Georgia,serif;max-width:920px;margin:40px auto;color:#222;line-height:1.5}}
h1,h2{{font-family:Arial;color:{NAVY}}} table{{border-collapse:collapse;width:100%;font-family:Arial;font-size:12px;margin:12px 0}}
th{{background:{NAVY};color:#fff;padding:6px;text-align:left}} td{{border-bottom:1px solid #ddd;padding:5px}}
img{{max-width:100%;margin:10px 0}} a{{color:#0563c1}} .note{{background:{LT};padding:10px 14px;border-left:4px solid {NAVY}}}</style></head><body>
<h1>The Economics of Transformative AI</h1>
<p><i>2031 frontier-AI serving-revenue model - preview rendered from parameters.csv. Edit that file to change the simulation.</i></p>
<div class=note><b>Headline:</b> credible methods (Anthropic model-based + Epoch token-capacity) give a pooled median of <b>${pp[1]/1e12:,.0f}T</b> (P5-P95 ${pp[0]/1e12:,.0f}-{pp[2]/1e12:,.0f}T). The per-GPU/token bottom-up runs hot (>world GDP) and is shown only as an upper bound.</div>
<h2>2031 revenue by method</h2><img src=fig_methods.png>
<table><tr><th>Method</th><th>Central $T</th><th>P5 $T</th><th>Median $T</th><th>P95 $T</th></tr>{resrows}</table>
<img src=fig_pooled.png>
<h2>Raw data &amp; sources</h2><table><tr><th>Group</th><th>Parameter</th><th>Value</th><th>Range</th><th>Dist</th><th>Unit</th><th>Source</th><th>Note</th></tr>{rows}</table>
<p style='font-size:12px;color:#666'>Generated by render_preview.py from model.py + parameters.csv. The Quarto twin is report.qmd.</p>
</body></html>"""
open("report_preview.html","w").write(html)
print("report_preview.html written")
