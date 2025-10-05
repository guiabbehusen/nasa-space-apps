import httpx
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

# Credenciais Meteomatics
METEOMATICS_USER = os.getenv("METEOMATICS_USER")
METEOMATICS_PASSWORD = os.getenv("METEOMATICS_PASSWORD")

print("=" * 60)
print("🌤️  TESTE DA API METEOMATICS")
print("=" * 60)
print(f"User: {METEOMATICS_USER}")
print(f"Password: {'*' * len(METEOMATICS_PASSWORD) if METEOMATICS_PASSWORD else 'Not set'}")
print("=" * 60)

if not METEOMATICS_USER or not METEOMATICS_PASSWORD:
    print("❌ Erro: Configure METEOMATICS_USER e METEOMATICS_PASSWORD no .env")
    exit(1)

# Coordenadas de teste (São Paulo)
LAT = -23.5505
LON = -46.6333


def test_weather_data():
    """Testa obtenção de dados meteorológicos"""
    print("\n🌡️  TESTE 1: DADOS METEOROLÓGICOS")
    print("-" * 60)

    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Parâmetros meteorológicos
        params = [
            "t_2m:C",  # temperatura
            "t_apparent:C",  # sensação térmica
            "relative_humidity_2m:p",  # umidade
            "wind_speed_10m:kmh",  # velocidade do vento
            "wind_dir_10m:d",  # direção do vento
            "wind_gusts_10m_1h:kmh",  # rajadas
            "msl_pressure:hPa",  # pressão
            "visibility:km",  # visibilidade
            "total_cloud_cover:p",  # nuvens
            "uv:idx"  # UV index
        ]

        params_str = ",".join(params)
        url = f"https://api.meteomatics.com/{timestamp}/{params_str}/{LAT},{LON}/json"

        print(f"📍 Localização: São Paulo ({LAT}, {LON})")
        print(f"🕐 Timestamp: {timestamp}")
        print(f"🔗 URL: {url}\n")

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, auth=(METEOMATICS_USER, METEOMATICS_PASSWORD))

            print(f"Status Code: {response.status_code}")

            if response.status_code == 401:
                print("❌ Erro 401: Credenciais inválidas!")
                print("Verifique METEOMATICS_USER e METEOMATICS_PASSWORD")
                return False

            if response.status_code == 200:
                data = response.json()

                print("✅ Dados recebidos com sucesso!\n")

                # Extrair e exibir os valores
                def get_value(index):
                    try:
                        return data["data"][index]["coordinates"][0]["dates"][0]["value"]
                    except:
                        return None

                print("📊 RESULTADOS:")
                print(f"  🌡️  Temperatura:       {get_value(0):.1f}°C")
                print(f"  🤚 Sensação Térmica:  {get_value(1):.1f}°C")
                print(f"  💧 Umidade:           {get_value(2):.1f}%")
                print(f"  💨 Vento:             {get_value(3):.1f} km/h")
                print(f"  🧭 Direção do Vento:  {get_value(4):.0f}°")
                print(f"  🌪️  Rajadas:           {get_value(5):.1f} km/h")
                print(f"  🔽 Pressão:           {get_value(6):.1f} hPa")
                print(f"  👁️  Visibilidade:      {get_value(7):.1f} km")
                print(f"  ☁️  Cobertura Nuvens:  {get_value(8):.1f}%")
                print(f"  ☀️  Índice UV:         {get_value(9):.1f}")

                print("\n📄 JSON completo:")
                print(json.dumps(data, indent=2))
                return True
            else:
                print(f"❌ Erro {response.status_code}")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_air_quality():
    """Testa obtenção de dados de qualidade do ar"""
    print("\n\n🌫️  TESTE 2: QUALIDADE DO AR")
    print("-" * 60)

    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Parâmetros de qualidade do ar
        params = [
            "pm2p5_conc_sfc:ugm3",  # PM2.5
            "pm10_conc_sfc:ugm3",  # PM10
            "no2_conc_sfc:ugm3",  # NO2
            "o3_conc_sfc:ugm3",  # O3
            "co_conc_sfc:mgm3",  # CO
            "so2_conc_sfc:ugm3"  # SO2
        ]

        params_str = ",".join(params)
        url = f"https://api.meteomatics.com/{timestamp}/{params_str}/{LAT},{LON}/json"

        print(f"📍 Localização: São Paulo ({LAT}, {LON})")
        print(f"🕐 Timestamp: {timestamp}")
        print(f"🔗 URL: {url}\n")

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, auth=(METEOMATICS_USER, METEOMATICS_PASSWORD))

            print(f"Status Code: {response.status_code}")

            if response.status_code == 401:
                print("❌ Erro 401: Credenciais inválidas!")
                return False

            if response.status_code == 200:
                data = response.json()

                print("✅ Dados recebidos com sucesso!\n")

                # Extrair e exibir os valores
                def get_value(index):
                    try:
                        return data["data"][index]["coordinates"][0]["dates"][0]["value"]
                    except:
                        return None

                print("📊 RESULTADOS:")
                print(f"  PM2.5:  {get_value(0):.2f} µg/m³")
                print(f"  PM10:   {get_value(1):.2f} µg/m³")
                print(f"  NO2:    {get_value(2):.2f} µg/m³")
                print(f"  O3:     {get_value(3):.2f} µg/m³")
                print(f"  CO:     {get_value(4):.3f} mg/m³")
                print(f"  SO2:    {get_value(5):.2f} µg/m³")

                print("\n📄 JSON completo:")
                print(json.dumps(data, indent=2))
                return True
            else:
                print(f"❌ Erro {response.status_code}")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_simple_request():
    """Teste simples - apenas temperatura"""
    print("\n\n🔥 TESTE 3: REQUISIÇÃO SIMPLES (Apenas Temperatura)")
    print("-" * 60)

    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"https://api.meteomatics.com/{timestamp}/t_2m:C/{LAT},{LON}/json"

        print(f"🔗 URL: {url}\n")

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, auth=(METEOMATICS_USER, METEOMATICS_PASSWORD))

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                temp = data["data"][0]["coordinates"][0]["dates"][0]["value"]
                print(f"✅ Temperatura: {temp:.1f}°C")
                print(f"\n📄 JSON: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Erro: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


# Executar testes
if __name__ == "__main__":
    results = []

    results.append(("Teste Simples", test_simple_request()))
    results.append(("Dados Meteorológicos", test_weather_data()))
    results.append(("Qualidade do Ar", test_air_quality()))

    # Resumo
    print("\n\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")

    print("=" * 60)

    # Status final
    all_passed = all(result for _, result in results)
    if all_passed:
        print("🎉 Todos os testes passaram!")
        print("\nVocê pode usar a API Meteomatics normalmente.")
        print("Execute 'python main.py' para iniciar o servidor FastAPI.")
    else:
        print("⚠️  Alguns testes falharam.")
        print("\nVerifique:")
        print("1. Suas credenciais no arquivo .env")
        print("2. Conexão com internet")
        print("3. Se sua conta Meteomatics está ativa")