import os
base=r"C:/Users/luizi/agente_convert_moeda_fintech"
import os
os.makedirs(os.path.join(base, "docs/monetization"), exist_ok=True)
with open(os.path.join(base, "docs/monetization/MONETIZATION_STRATEGY.md"), "w", encoding="utf-8") as f:
    f.write("# Monetizacao CambioBot\n\nModelo: B2C + B2B + Afiliados")
print("OK")