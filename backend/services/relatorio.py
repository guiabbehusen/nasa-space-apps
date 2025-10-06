import json
import pandas as pd
from ollama import Client

# ----------------------------------------
# CONFIGURAÇÕES
# ----------------------------------------
client = Client()

TEMPO_API_JSON = "./data/resultado_-23.5505_-46.6333.json"  # JSON completo do AQI
CHEM_EFFECTS_CSV = "./data/chemical_effects.csv"            # CSV com compostos e efeitos
AQI_ABOUT = "./data/about_aqi.txt"                          # Texto explicativo sobre AQI
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
    Usa a SLM para gerar um texto em português, amigável,
    descrevendo os riscos à saúde com base no AQI, nos compostos e no perfil humano.
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
Você é um especialista em saúde ambiental.

Com base nas informações fornecidas, escreva um **relatório textual em português**,
em tom **amigável e compreensível**, que possa ser enviado por **email** para o usuário.

NUMERO DA AQI ( AIR QUALITY INDEX ) NO LOCAL EXATO: {aqi_index}
### Dados de qualidade do ar (AQI - JSON completo):
{json.dumps(aqi_json, ensure_ascii=False, indent=2)}

### Dados de efeitos químicos (CSV):
{json.dumps(chem_effects, ensure_ascii=False, indent=2)}

### Texto explicativo sobre o AQI:
{about_aqi_text}

### Perfil da pessoa:
{perfil}

Use o sistema TRAPS para interpretar o nível de cada composto químico:
{traps_text}

Sua tarefa:
1. Analise os compostos e níveis do AQI.
2. Relacione os compostos e concentrações aos efeitos listados no CSV.
3. Use também o texto explicativo sobre AQI para embasar sua análise.
4. Descreva de forma clara o que essa qualidade do ar pode causar ao corpo de uma pessoa com esse perfil.
5. Evite linguagem técnica — o texto deve soar natural, empático e claro.
6. A saída deve ser **somente texto corrido**, pronto para ser enviado por email.

Exemplo de tom:
"Olá! A qualidade do ar na sua região hoje está moderada, com presença elevada de PM2.5 e CO. Para gestantes, isso pode causar leve desconforto respiratório e cansaço, sendo importante evitar atividades ao ar livre prolongadas."
"""

    print("[gerar_relatorio_amigavel] Gerando texto via SLM...")
    response = client.chat(
        model=SLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um assistente especializado em saúde ambiental. "
                    "Responda apenas com texto corrido em português, sem JSON ou código."
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
