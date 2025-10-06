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

DATA_PATH = "./data/tempo.csv"  # seu CSV atual
INDEX_PATH = "./storage_faiss/faiss_geo_index.bin"
LAT_COL = "latitude"
LON_COL = "longitude"
JSON_MODEL = "qwen2.5:0.5b"

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
    Força a SLM a retornar JSON válido:
      - format="json"
      - system: responder apenas JSON
      - temperature=0
      - valida/retenta 1x se necessário
    """
    dados_pontos = df_resultado.to_dict(orient="records")

    system_msg = (
        "Você é um gerador de JSON. Responda SOMENTE com um JSON válido, "
        "sem texto adicional, sem explicações, sem markdown."
    )

    # Especificação de estrutura esperada (instrução textual; Ollama não valida schema)
    schema_hint = {
        "coordenada_consulta": {"latitude": "float", "longitude": "float"},
        "resumo_geral": "string",
        "avaliacoes": [
            {
                "lat": "float",
                "lon": "float",
                "distancia": "float",
                "compostos": {
                    "<nome_composto>": {"valor": "float", "nivel": "Good|Moderate|USG|Unhealthy|Very Unhealthy|Hazardous"}
                },
                "indice_geral": "string"
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
        "Gere um JSON estruturado a partir dos dados abaixo.\n\n"
        f"Coordenada consultada: lat={lat}, lon={lon}\n\n"
        "Pontos próximos (lista de registros):\n"
        f"{json.dumps(dados_pontos, ensure_ascii=False)}\n\n"
        "Considere que cada registro pode conter compostos químicos (ex.: PM2.5, NO2, SO2, O3, CO...). "
        "Classifique cada composto segundo o sistema TRAPS (categorias Good, Moderate, USG, Unhealthy, Very Unhealthy, Hazardous):\n"
        f"{traps_text}\n"
        "Se não houver um composto em um registro, ignore-o nesse registro.\n\n"
        "Estrutura esperada do JSON (apenas referência, não inclua comentários):\n"
        f"{json.dumps(schema_hint, ensure_ascii=False)}\n\n"
        "IMPORTANTE: Responda SOMENTE com JSON válido, sem texto extra, sem markdown."
    )

    # 1ª tentativa
    print("[gerar_json_via_slm] Tentativa 1 com format=json...")
    resp = client.chat(
        model=JSON_MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": 0},
        format="json",  # força o modelo a responder JSON
    )
    raw = resp["message"]["content"]

    try:
        parsed = _parse_json_or_raise(raw)
        return json.dumps(parsed, ensure_ascii=False, indent=2)
    except Exception:
        # 2ª tentativa, instrução ainda mais rígida
        print("[gerar_json_via_slm] Tentativa 1 falhou em JSON. Reforçando instruções (Tentativa 2).")
        harder_user_prompt = user_prompt + "\n\nRETORNE APENAS JSON VÁLIDO. NADA MAIS."
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

