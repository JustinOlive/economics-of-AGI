"""Reproduction + Monte Carlo of the GDoc 'Back-of-napkin calculations'."""
import numpy as np
from scipy import stats
rng = np.random.default_rng(20260614)
SEP = "=" * 78
def line(label, original, recomputed, unit="", note=""):
    print(f"  {label:<46} doc={str(original):<12} calc={str(recomputed):<14}{unit} {note}")

print(SEP); print("PART A - DETERMINISTIC REPRODUCTION OF GDOC FIGURES"); print(SEP)
print("\n[2026 BASELINE]")
H100_world = 20e6; h100_per_copy_2026 = 24
copies_2026 = H100_world / h100_per_copy_2026
line("Concurrent copies (20M/24)", "830,000", f"{copies_2026:,.0f}")
industry_llm = 100e9
line("Macro rev per H100 ($100B/20M)", "$5,000", f"${industry_llm/H100_world:,.0f}")
anthropic_arr = 45e9; anthropic_h100 = 1e6
line("Anthropic rev/chip ($45B/1M)", "$45,000", f"${anthropic_arr/anthropic_h100:,.0f}")
models_anth = anthropic_h100 / h100_per_copy_2026
line("Anthropic #models (1M/24)", "42,000", f"{models_anth:,.0f}")
rev_per_model_anth = anthropic_arr / models_anth
line("Anthropic rev/model/yr", "$1.07M", f"${rev_per_model_anth/1e6:,.3f}M")
tps_per_gpu = 2100; price_blended = 3.5; sec_per_year = 365*24*3600
line("Seconds per year", "31.5M", f"{sec_per_year/1e6:,.3f}M")
tokens_per_gpu_yr = tps_per_gpu * sec_per_year
rev_per_gpu_full = tokens_per_gpu_yr/1e6*price_blended
line("DeepSeek rev/GPU/yr @100%util", "$230k", f"${rev_per_gpu_full/1e3:,.1f}k")
rev_per_gpu_40 = rev_per_gpu_full*0.40
line("DeepSeek rev/GPU/yr @40%util", "$90k", f"${rev_per_gpu_40/1e3:,.1f}k")
line("DeepSeek rev/model/yr (90k*24)", "$2.16M", f"${rev_per_gpu_40*24/1e6:,.3f}M")

print("\n[2031 PROJECTION]")
growth=3.0; years=5; H100_2031=H100_world*growth**years
line("H100e in 2031 (20M*3^5)", "4.8B", f"{H100_2031/1e9:,.2f}B")
copies_2031 = H100_2031/200
line("Copies 2031 (4.8B/200)", "24.3M", f"{copies_2031/1e6:,.1f}M")
line("  ratio vs 2026 830k", "29x", f"{copies_2031/copies_2026:,.1f}x")
line("GPU-based rev @ $90k/chip", "$180T", f"${2e9*90e3/1e12:,.1f}T")
line("GPU-based rev @ $5k/chip", "$10T", f"${2e9*5e3/1e12:,.1f}T")
line("Model-based (10M*$200k)", "$2T", f"${10e6*200e3/1e12:,.2f}T")
print("    NOTE: 2026 per-model case studies were $1.07M & $2.16M, NOT $200k")
print(f"          If 'same as today'=$1.07M: 10M*$1.07M = ${10e6*rev_per_model_anth/1e12:,.1f}T")
tokens_per_sec_2031=1e12; util=0.10; eff=tokens_per_sec_2031*util
line("Eff tokens/sec @10%util", "100B", f"{eff/1e9:,.0f}B")
tpm = eff*60
line("Tokens/min", "6T", f"{tpm/1e12:,.1f}T")
implied = 5e6/(tpm/1e6)
print(f"    NOTE: $5M/min implies ${implied:.2f}/M tokens, NOT the $3.5/M in DeepSeek calc")
line("Token-based rev/yr ($5M/min)", "$2.6T", f"${5e6*60*24*365/1e12:,.3f}T")
print(f"    If $3.5/M : ${(tpm/1e6*3.5)*60*24*365/1e12:,.1f}T/yr | If $0.50/M: ${(tpm/1e6*0.5)*60*24*365/1e12:,.2f}T/yr")
internet=500e12
line("Internet-equiv every", "few hours", f"{internet/tpm/60:,.1f} hrs")
wc=1.5e9; hr=1000; human=wc*hr
line("Human tok-equiv/min (1.5B*1000)", "1.5T", f"{human/1e12:,.2f}T")
line("LLM/human ratio", "4x", f"{tpm/human:,.1f}x")
epoch_day=240e3
print(f"    Epoch human basis 240k/day*1.5B={wc*epoch_day/1e12:,.0f}T/day; LLM {tpm*1440/1e12:,.0f}T/day -> {tpm*1440/(wc*epoch_day):,.0f}x")
cagr=(2e12/100e9)**(1/5)-1
print(f"\n[TRAJECTORY] $100B->$2T implies {cagr*100:,.0f}%/yr CAGR; compute 243x but rev 20x -> rev/compute falls {243/20:,.0f}x")
for g in [3,2,1.7]: print(f"    $100B at {g}x/yr: ${100e9*g**5/1e12:,.1f}T")

print("\n"+SEP); print("PART B - MONTE CARLO"); print(SEP)
N=300000
def lr(lo,hi,p=0.90):
    z={0.90:1.645,0.80:1.282}[p]
    return (np.log(lo)+np.log(hi))/2,(np.log(hi)-np.log(lo))/(2*z)
g_draw=rng.normal(3.0,0.45,N).clip(1.8,4.5)
h26=rng.uniform(16e6,24e6,N); H31=h26*g_draw**5
rev_chip=rng.lognormal(*lr(5e3,60e3),N); decl=rng.uniform(0.25,0.9,N); shr=rng.uniform(0.25,0.55,N)
m1=H31*shr*rev_chip*decl
cp=rng.lognormal(*lr(3e6,30e6),N); rpc=rng.lognormal(*lr(80e3,1.2e6),N); m2=cp*rpc
tps=rng.lognormal(*lr(2e11,5e12,0.80),N); u=rng.uniform(0.05,0.30,N); pr=rng.lognormal(*lr(0.4,3.5),N)
m3=tps*u*pr/1e6*sec_per_year
for nm,a in [("Method1 GPU/chip",m1),("Method2 model",m2),("Method3 token",m3)]:
    p=np.percentile(a,[5,25,50,75,95])/1e12
    print(f"  {nm:<18} P5={p[0]:6.2f} P25={p[1]:6.2f} P50={p[2]:6.2f} P75={p[3]:6.2f} P95={p[4]:6.2f} ($T)")
pool=np.concatenate([m1,m2,m3]); p=np.percentile(pool,[5,25,50,75,95])/1e12
print(f"  {'POOLED':<18} P5={p[0]:6.2f} P25={p[1]:6.2f} P50={p[2]:6.2f} P75={p[3]:6.2f} P95={p[4]:6.2f}")
print(f"  P(rev>$2T)={np.mean(pool>2e12)*100:.1f}%  P(rev>$1T)={np.mean(pool>1e12)*100:.1f}%  P(rev>$10T)={np.mean(pool>10e12)*100:.1f}%")
print("\n[SENSITIVITY token method, Spearman rho]")
for lab,x in [("tokens/sec capacity",tps),("utilisation",u),("price $/Mtok",pr)]:
    print(f"  {lab:<22} rho={stats.spearmanr(x,m3).correlation:+.3f}")
print("\n[HUMAN-PARITY 2031]")
tpm2=tps*u*60; wcm=rng.uniform(1.0e9,1.6e9,N); hrm=rng.uniform(400,1200,N); ratio=tpm2/(wcm*hrm)
p=np.percentile(ratio,[5,25,50,75,95])
print(f"  ratio P5={p[0]:.2f} P25={p[1]:.2f} P50={p[2]:.2f} P75={p[3]:.2f} P95={p[4]:.2f}; P(>1)={np.mean(ratio>1)*100:.1f}%")
print("\nDONE.")
