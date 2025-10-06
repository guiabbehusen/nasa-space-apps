import os
import json
import numpy as np
import pandas as pd
import faiss
from ollama import Client

# ----------------------------------------
# CONFIG
# ----------------------------------------
client = Client()

DATA_PATH = "./services/data/tempo.csv"  # seu CSV atual
INDEX_PATH = "./services/storage_faiss/faiss_geo_index.bin"
LAT_COL = "latitude"
LON_COL = "longitude"
JSON_MODEL = "qwen2.5:1.5b"

# ----------------------------------------
# CSV & FAISS
# ----------------------------------------
def carregar_dados_csv():
    print(f"[carregar_dados_csv] Lendo arquivo: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"[carregar_dados_csv] Total de linhas: {len(df)}")
    return df

def criar_index_geo(df):
    print("[criar_index_geo] Criando índice FAISS geoespacial...")
    coords = df[[LAT_COL, LON_COL]].to_numpy().astype("float32")
    index = faiss.IndexFlatL2(2)
    index.add(coords)
    print(f"[criar_index_geo] Total de coordenadas indexadas: {index.ntotal}")
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    return index

def carregar_ou_criar_index(df):
    if os.path.exists(INDEX_PATH):
        print(f"[carregar_ou_criar_index] Carregando índice existente: {INDEX_PATH}")
        index = faiss.read_index(INDEX_PATH)
    else:
        index = criar_index_geo(df)
    return index

def buscar_pontos_proximos(lat, lon, index, df, k=10):
    print(f"[buscar_pontos_proximos] Buscando {k} pontos mais próximos de ({lat}, {lon})")
    query = np.array([[lat, lon]], dtype="float32")
    D, I = index.search(query, k)
    resultados = df.iloc[I[0]].copy()
    resultados["distancia"] = D[0]
    print(f"[buscar_pontos_proximos] {len(resultados)} pontos retornados.")
    return resultados

# ----------------------------------------
# Utilitários JSON
# ----------------------------------------
def _strip_code_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        # remove a primeira cerca
        s = s.split("```", 1)[1]
        # remove possível linguagem no início
        s = s.lstrip("json").lstrip()
        # pega o que vem antes da próxima cerca
        if "```" in s:
            s = s.split("```", 1)[0]
    return s.strip()

def _parse_json_or_raise(s: str) -> dict:
    s = _strip_code_fences(s)
    return json.loads(s)

# ----------------------------------------
# Geração via SLM (FORÇANDO JSON)
# ----------------------------------------
def gerar_json_via_slm(lat, lon, df_resultado):
    """
    Forces the SLM to return valid JSON:
      - format="json"
      - system: respond only with JSON
      - temperature=0
      - validates/retries once if necessary
    """
    dados_pontos = df_resultado.to_dict(orient="records")

    system_msg = (
        "You are a JSON generator. Respond ONLY with valid JSON — "
        "no extra text, no explanations, no markdown."
    )

    schema_hint = {
        "query_coordinates": {"latitude": "float", "longitude": "float"},
        "summary": "string",
        "evaluations": [
            {
                "lat": "float",
                "lon": "float",
                "distance": "float",
                "compounds": {
                    "<compound_name>": {"value": "float", "level": "Good|Moderate|USG|Unhealthy|Very Unhealthy|Hazardous"}
                },
                "overall_index": "string"
            }
        ]
    }

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

    user_prompt = (
        "Generate a structured JSON from the data below.\n\n"
        f"Queried coordinates: lat={lat}, lon={lon}\n\n"
        "Nearby points (list of records):\n"
        f"{json.dumps(dados_pontos, ensure_ascii=False)}\n\n"
        "Each record may contain chemical compounds (e.g., PM2.5, NO2, SO2, O3, CO...). "
        "Classify each compound according to the TRAPS system (categories: Good, Moderate, USG, Unhealthy, Very Unhealthy, Hazardous):\n"
        f"{traps_text}\n"
        "If a compound is missing in a record, ignore it for that record.\n\n"
        "Expected JSON structure (for reference only, do not include comments):\n"
        f"{json.dumps(schema_hint, ensure_ascii=False)}\n\n"
        "IMPORTANT: Return ONLY valid JSON. No extra text. No markdown."
    )

    print("[gerar_json_via_slm] Attempt 1 with format=json...")
    resp = client.chat(
        model=JSON_MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": 0},
        format="json",
    )
    raw = resp["message"]["content"]

    try:
        parsed = _parse_json_or_raise(raw)
        return json.dumps(parsed, ensure_ascii=False, indent=2)
    except Exception:
        print("[gerar_json_via_slm] Attempt 1 failed. Retrying with stricter instructions (Attempt 2).")
        harder_user_prompt = user_prompt + "\n\nRETURN ONLY VALID JSON. NOTHING ELSE."
        resp2 = client.chat(
            model=JSON_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": harder_user_prompt},
            ],
            options={"temperature": 0},
            format="json",
        )
        raw2 = resp2["message"]["content"]
        parsed2 = _parse_json_or_raise(raw2)
        return json.dumps(parsed2, ensure_ascii=False, indent=2)


# ----------------------------------------
# MAIN
# ----------------------------------------

if __name__ == "__main__":
    df = carregar_dados_csv()
    index = carregar_ou_criar_index(df)

    # Coordenada de exemplo (você pode parametrizar via input() ou argumento CLI)
    latitude = -23.5505
    longitude = -46.6333

    # Busca pontos próximos
    df_resultado = buscar_pontos_proximos(latitude, longitude, index, df, k=10)

    # Gera JSON via SLM
    json_final = gerar_json_via_slm(latitude, longitude, df_resultado)

    # Caminho para salvar o arquivo
    output_path = f"./data/resultado_{latitude}_{longitude}.json"

    # Salva em arquivo .json
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json_final)

    print(f"\n✅ JSON salvo com sucesso em: {output_path}")

