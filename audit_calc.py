print("=== AUDIT RE-DERIVATIONS (corrected inputs) ===")
sec=31_536_000
# F4/F5: DeepSeek rev/GPU at corrected price & utilisation
tps=2100
for price,plabel in [(3.5,"doc $3.5/M (pre-discount output)"),(2.17,"current blended $2.17/M"),(0.87,"current output $0.87/M")]:
    for u in [0.40,0.30,0.10]:
        rev=tps*sec/1e6*price*u
        print(f"  rev/GPU/yr  price={plabel:<34} util={u:>4.0%}  -> ${rev/1e3:6.1f}k")
print()
# F7: model-based with consistent per-copy
for rpc,lbl in [(200e3,"doc $200k"),(1.07e6,"2026 Anthropic $1.07M"),(2.16e6,"2026 DeepSeek $2.16M")]:
    print(f"  model-based 10M copies * {lbl:<22} = ${10e6*rpc/1e12:5.2f}T")
print()
# F8: token method at the three prices
tpm=6e12
for price in [3.5,2.17,0.87,0.83,0.50]:
    print(f"  token-method @ ${price}/M -> ${tpm/1e6*price*60*24*365/1e12:5.2f}T/yr")
print()
# F18: 2028 revenue implied by scenarios vs Dario
print("  2028 revenue check (from $100B 2026):")
for g in [3,2.5,10]:
    print(f"    {g}x/yr -> ${100e9*g**2/1e12:.2f}T by 2028")
print("    Dario (Dwarkesh): 'low hundreds of billions by 2028' i.e. ~$0.2-0.5T")
print()
# F19: % of wages
for rev in [2e12,2.6e12,2.5e12]:
    print(f"  ${rev/1e12:.1f}T as % of $50T wages = {rev/50e12*100:.1f}%")
print()
# F6: GPU method vs world GDP
print(f"  GPU-method $180T  vs world GDP ~$110T -> {180/110:.2f}x GDP (non-credible)")
# F2/F1 deltas
print(f"  Combined OpenAI+Anthropic: $45B+$25B=$70B (doc said $80B); industry round to $100B OK")
