"""Economics of TAI - 2031 frontier-AI revenue model.
Single source of truth: parameters.csv. Pure functions; no headline numbers hardcoded here.
Four estimation FRAMINGS (not statistically independent - they share output price & seconds),
plus a Monte Carlo. Run `python model.py` for a self-test on the default parameters.
"""
import csv, math
import numpy as np

TOKENS_PER_M = 1e6   # unit conversion locked to the "$/Mtok" price unit

def load_params(path="parameters.csv"):
    P={}
    for r in csv.DictReader(open(path)):
        f=lambda x: float(x) if x not in ("",None) else None
        rec=dict(value=f(r["value"]),low=f(r["low"]),high=f(r["high"]),dist=r["dist"],
                 unit=r["unit"],parameter=r["parameter"],source=r["source"],url=r["url"],
                 note=r["note"],group=r["group"])
        # validation: low <= value <= high for non-point rows
        if rec["dist"]!="point" and rec["low"] is not None:
            assert rec["low"]<=rec["value"]<=rec["high"], f"{r['id']}: need low<=value<=high (got {rec['low']},{rec['value']},{rec['high']})"
        P[r["id"]]=rec
    return P

def central(P): return {k:v["value"] for k,v in P.items()}

def sample(P, n, seed=0):
    rng=np.random.default_rng(seed); out={}
    for k,v in P.items():
        d=v["dist"]
        if d=="point" or v["low"] is None: out[k]=np.full(n,v["value"])
        elif d=="uniform": out[k]=rng.uniform(v["low"],v["high"],n)
        elif d=="triangular": out[k]=rng.triangular(v["low"],v["value"],v["high"],n)
        elif d=="lognormal":
            # value is the MEDIAN; low/high approximate the 90% interval (P5/P95)
            mu=math.log(v["value"]); sig=(math.log(v["high"])-math.log(v["low"]))/(2*1.645)
            out[k]=rng.lognormal(mu,sig,n)
        else: out[k]=np.full(n,v["value"])
    return out




def derive(s):
    d={}
    
    d["stock_2031"]=s["stock_2026"]*s["growth"]**s["years"]                                   # Compute stock prediction for 2031 (H100 equivalents)
    gpc=lambda p: np.ceil(p*s["bytes_per_param"]*s["mem_overhead"]/s["gpu_mem_bytes"])        # GPUs per model copy
    d["gpus_2026"]=gpc(s["ds_total_params"]); d["gpus_2031"]=gpc(s["model_params_2031"])      # Apply gpc to 2026 DeepSeek and 2031 frontier models      
    d["peak_tps_flop"]=s["h100_flops_fp8"]/(2*s["ds_active_params"])                          # FLOP-based peak tokens/sec cross-check (active params)                         
    d["blended_mkt"]=(s["price_in_mkt"]*s["io_ratio"]+s["price_out_mkt"])/(s["io_ratio"]+1)   # Blended $/Mtok price, weighted by input:output ratio   
    d["industry_2026"]=s["arr_anthropic"]+s["arr_openai"]+s["arr_others"]                     # Total 2026 industry ARR across providers
    d["rev_per_gpu_macro"]=d["industry_2026"]/s["stock_2026"]                                 # Industry-average annual revenue per GPU
    d["out_tok_per_inf_gpu_yr"]=s["single_stream_tps"]*s["eff_concurrency"]*s["seconds_per_year"]  # Annual output tokens per inference GPU
    # output-token revenue only (input revenue excluded); the per-GPU method is an upper bound anyway
    d["rev_per_gpu_deepseek"]=d["out_tok_per_inf_gpu_yr"]*s["price_out_mkt"]/TOKENS_PER_M     # Annual output-token revenue per inference GPU
    d["anthropic_inf_fleet"]=s["anthropic_total_fleet"]*s["anthropic_inf_share"]              # Anthropic GPUs allocated to inference
    d["anthropic_rev_per_model"]=s["arr_anthropic"]/(d["anthropic_inf_fleet"]/d["gpus_2026"])  # Anthropic ARR per running model copy
    d["inf_gpus_2031"]=d["stock_2031"]*s["inference_fraction_2031"]                           # 2031 GPUs devoted to inference
    d["copies_2031"]=d["inf_gpus_2031"]/d["gpus_2031"]                                        # Concurrent model copies the 2031 fleet runs
    return d

def m_deepseek(s,d): return d["inf_gpus_2031"]*d["rev_per_gpu_deepseek"]
def m_macro(s,d):    return d["stock_2031"]*d["rev_per_gpu_macro"]
def m_model(s,d):    return d["copies_2031"]*d["anthropic_rev_per_model"]   # assumes rev/copy invariant to model size (stationarity)
def m_epoch(s,d):    return s["epoch_token_capacity_2031"]*s["inference_fraction_2031"]*s["seconds_per_year"]*s["price_out_mkt"]/TOKENS_PER_M

METHODS=[("DeepSeek bottom-up (GPU = token)",m_deepseek),("GPU macro average",m_macro),
         ("Anthropic model-based",m_model),("Epoch token-capacity",m_epoch)]

def run_central(P):
    s=central(P); d=derive(s); return s,d,{n:fn(s,d) for n,fn in METHODS}

def run_mc(P,n=200000,seed=20260615):
    rng=np.random.default_rng(seed)
    s=sample(P,n,seed); d=derive(s)
    res={n_:fn(s,d) for n_,fn in METHODS}
    # pooled = equal-weight discrete mixture of the two credible framings; independent selector
    sel=np.random.default_rng(seed+1).random(n)<0.5
    res["Pooled (model + Epoch)"]=np.where(sel,res["Anthropic model-based"],res["Epoch token-capacity"])
    return s,d,res

def selftest():
    P=load_params(); s,d,cen=run_central(P)
    checks=[("gpus_2026",d["gpus_2026"],24),("gpus_2031",d["gpus_2031"],192),
            ("rev_per_gpu_macro",d["rev_per_gpu_macro"],5000)]
    for name,got,exp in checks:
        flag="ok" if abs(got-exp)<max(1,exp*0.01) else "CHANGED (expected on edited params)"
        print(f"  {name}: {got:,.4g} [{flag}]")
    return s,d,cen

if __name__=="__main__":
    s,d,cen=selftest()
    print("=== 2031 revenue (central, US$ T) ===")
    for k,v in cen.items(): print(f"  {k:34} {v/1e12:8.2f}")
    _,_,mc=run_mc(load_params())
    print("=== Monte Carlo (US$ T: P5/P50/P95) ===")
    for k,v in mc.items():
        p=np.percentile(v,[5,50,95])/1e12; print(f"  {k:34} {p[0]:7.2f}{p[1]:8.2f}{p[2]:8.2f}")
