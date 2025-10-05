import httpx
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

METEOMATICS_USER = os.getenv("METEOMATICS_USER")
METEOMATICS_PASSWORD = os.getenv("METEOMATICS_PASSWORD")

LAT = -23.5505
LON = -46.6333

print("=" * 80)
print("🔍 TESTANDO PARÂMETROS DE QUALIDADE DO AR DISPONÍVEIS NO METEOMATICS")
print("=" * 80)

# Lista de possíveis parâmetros de qualidade do ar
air_quality_params = [
    # PM2.5 - Diferentes nomenclaturas
    ("PM2.5 (ugm3)", "pm2p5_conc_sfc:ugm3"),
    ("PM2.5 (ug/m3)", "pm2p5:ugm3"),
    ("PM2.5 (conc)", "pm2p5_concentration:ugm3"),
    ("PM2.5 (simple)", "pm2p5:ug/m3"),

    # PM10
    ("PM10 (ugm3)", "pm10_conc_sfc:ugm3"),
    ("PM10 (ug/m3)", "pm10:ugm3"),
    ("PM10 (conc)", "pm10_concentration:ugm3"),

    # NO2
    ("NO2 (ugm3)", "no2_conc_sfc:ugm3"),
    ("NO2 (ug/m3)", "no2:ugm3"),
    ("NO2 (ppb)", "no2:ppb"),
    ("NO2 (conc)", "no2_concentration:ugm3"),

    # O3
    ("O3 (ugm3)", "o3_conc_sfc:ugm3"),
    ("O3 (ug/m3)", "o3:ugm3"),
    ("O3 (ppb)", "o3:ppb"),
    ("O3 (conc)", "o3_concentration:ugm3"),

    # CO
    ("CO (mgm3)", "co_conc_sfc:mgm3"),
    ("CO (mg/m3)", "co:mgm3"),
    ("CO (ppm)", "co:ppm"),
    ("CO (conc)", "co_concentration:mgm3"),

    # SO2
    ("SO2 (ugm3)", "so2_conc_sfc:ugm3"),
    ("SO2 (ug/m3)", "so2:ugm3"),
    ("SO2 (ppb)", "so2:ppb"),

    # AQI direto (se disponível)
    ("AQI (US)", "air_quality_index_us:idx"),
    ("AQI (EU)", "air_quality_index_eu:idx"),
    ("AQI (simple)", "aqi:idx"),
]

successful_params = []
failed_params = []

timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

with httpx.Client(timeout=30.0) as client:
    for param_name, param_code in air_quality_params:
        print(f"\n{'=' * 80}")
        print(f"🧪 Testando: {param_name}")
        print(f"📝 Parâmetro: {param_code}")
        print(f"{'=' * 80}")

        url = f"https://api.meteomatics.com/{timestamp}/{param_code}/{LAT},{LON}/json"

        try:
            response = client.get(url, auth=(METEOMATICS_USER, METEOMATICS_PASSWORD))

            if response.status_code == 200:
                data = response.json()
                value = data["data"][0]["coordinates"][0]["dates"][0]["value"]
                print(f"✅ SUCESSO! Valor: {value}")
                successful_params.append((param_name, param_code, value))
            elif response.status_code == 404:
                error_msg = response.json().get("message", "Not available")
                print(f"❌ NÃO DISPONÍVEL: {error_msg}")
                failed_params.append((param_name, param_code, "404"))
            else:
                print(f"⚠️  Erro {response.status_code}: {response.text}")
                failed_params.append((param_name, param_code, str(response.status_code)))
        except Exception as e:
            print(f"💥 ERRO: {e}")
            failed_params.append((param_name, param_code, str(e)))

# Resumo final
print("\n\n" + "=" * 80)
print("📊 RESUMO DOS TESTES")
print("=" * 80)

print(f"\n✅ PARÂMETROS DISPONÍVEIS ({len(successful_params)}):")
print("-" * 80)
if successful_params:
    for param_name, param_code, value in successful_params:
        print(f"  ✓ {param_name:30} | {param_code:40} | Valor: {value}")
else:
    print("  Nenhum parâmetro de qualidade do ar encontrado.")

print(f"\n❌ PARÂMETROS NÃO DISPONÍVEIS ({len(failed_params)}):")
print("-" * 80)
for param_name, param_code, error in failed_params[:5]:  # Mostrar apenas os 5 primeiros
    print(f"  ✗ {param_name:30} | {param_code}")

if len(failed_params) > 5:
    print(f"  ... e mais {len(failed_params) - 5} parâmetros")

# Gerar código para usar os parâmetros disponíveis
if successful_params:
    print("\n\n" + "=" * 80)
    print("🔧 CÓDIGO PYTHON PARA USAR OS PARÂMETROS DISPONÍVEIS:")
    print("=" * 80)
    print("\nparams = [")
    for _, param_code, _ in successful_params:
        print(f'    "{param_code}",')
    print("]")

    print(
        "\n\nurl = f\"https://api.meteomatics.com/{{timestamp}}/{','.join([p[1] for p in successful_params])}/{{lat}},{{lon}}/json\"")

print("\n" + "=" * 80)