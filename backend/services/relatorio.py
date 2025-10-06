import json
import pandas as pd
from ollama import Client

# ----------------------------------------
# CONFIGURAÇÕES
# ----------------------------------------
client = Client()

TEMPO_API_JSON = "./services/data/resultado_-23.5505_-46.6333.json"  # JSON completo do AQI
CHEM_EFFECTS_CSV = "./services/data/chemical_effects.csv"            # CSV com compostos e efeitos
AQI_ABOUT = "./services/data/about_aqi.txt"                          # Texto explicativo sobre AQI
PROFILE = "gestante"                                        # pode ser "idoso", "criança", etc.
SLM_MODEL = "qwen2.5:1.5b"

# ----------------------------------------
# FUNÇÕES
# ----------------------------------------
def carregar_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_csv(path):
    df = pd.read_csv(path)
    return df.to_dict(orient="records")

def carregar_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def gerar_relatorio_amigavel(aqi_index, aqi_json, chem_effects, about_aqi_text, perfil):
    """
    Uses the SLM to generate a friendly English report text
    describing the health risks based on AQI, compounds, and human profile.
    """
    traps_text = """
traps = {
    "Good":          _mk_trap(minv, minv, q10, q10 + d),
    "Moderate":      _mk_trap(q10 - d, q10, q35, q35 + d),
    "USG":           _mk_trap(q35 - d, q35, q65, q65 + d),
    "Unhealthy":     _mk_trap(q65 - d, q65, q85, q85 + d),
    "Very Unhealthy":_mk_trap(q85 - d, q85, q97, q97 + d),
    "Hazardous":     _mk_trap(q97 - d, q97, maxv, maxv)
}
"""

    prompt = f"""
You are an environmental health specialist.

Based on the information provided, write a **friendly and easy-to-read report in English**
that can be **sent by email** to the user.

AIR QUALITY INDEX (AQI) VALUE FOR THE EXACT LOCATION: {aqi_index}
### Air quality data (AQI - full JSON):
{json.dumps(aqi_json, ensure_ascii=False, indent=2)}

### Chemical effects data (CSV):
{json.dumps(chem_effects, ensure_ascii=False, indent=2)}

### About AQI:
{about_aqi_text}

### User profile:
{perfil}

Use the TRAPS system to interpret each chemical compound level:
{traps_text}

Your task:
1. Analyze the AQI compounds and levels.
2. Relate the compounds and concentrations to the effects listed in the CSV.
3. Use the explanatory text about AQI to support your reasoning.
4. Clearly describe what this air quality could cause to a person with this profile.
5. Avoid technical jargon — the text should sound natural, empathetic, and clear.
6. The output must be **plain text only**, ready to send via email.

Example tone:
"Hello! The air quality in your area today is moderate, with elevated PM2.5 and CO levels. For pregnant individuals, this may cause mild respiratory discomfort and fatigue, so it’s best to avoid prolonged outdoor activities."
"""

    print("[gerar_relatorio_amigavel] Generating text via SLM...")
    response = client.chat(
        model=SLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant specialized in environmental health. "
                    "Respond only with plain text in English, no JSON or code."
                )
            },
            {"role": "user", "content": prompt}
        ],
        options={"temperature": 0.7}
    )
    return response["message"]["content"]

# ----------------------------------------
# MAIN
# ----------------------------------------
if __name__ == "__main__":
    aqi_json = carregar_json(TEMPO_API_JSON)
    chem_effects = carregar_csv(CHEM_EFFECTS_CSV)
    about_aqi_text = carregar_txt(AQI_ABOUT)

    texto_relatorio = gerar_relatorio_amigavel(150, aqi_json, chem_effects, about_aqi_text, PROFILE)

    output_path = f"./data/relatorio_email_{PROFILE}.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(texto_relatorio)

    print(f"\n✅ Relatório gerado e salvo em: {output_path}\n")
    print("=== PRÉVIA ===\n")
    print(texto_relatorio)
