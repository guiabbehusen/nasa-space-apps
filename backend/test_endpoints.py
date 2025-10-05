import httpx
import json
from datetime import datetime

# URL base da API (certifique-se que o servidor está rodando)
BASE_URL = "http://localhost:8000"

# Coordenadas de teste
TEST_LOCATIONS = [
    {"name": "São Paulo, Brazil", "lat": -23.5505, "lon": -46.6333},
    {"name": "New York, USA", "lat": 40.7128, "lon": -74.0060},
    {"name": "Tokyo, Japan", "lat": 35.6762, "lon": 139.6503},
]


def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_section(title):
    """Imprime seção formatada"""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print("─" * 80)


def print_json(data, indent=2):
    """Imprime JSON formatado"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def test_root():
    """Testa endpoint raiz"""
    print_section("📡 Testando GET /")

    try:
        response = httpx.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Resposta recebida com sucesso!\n")
            print_json(data)
            return True
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False


def test_health():
    """Testa endpoint de health check"""
    print_section("🏥 Testando GET /health")

    try:
        response = httpx.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passou!\n")
            print_json(data)

            # Verificar serviços
            services = data.get("services", {})
            print(f"\n📊 Status dos Serviços:")
            print(f"  Meteomatics: {'✅' if services.get('meteomatics') == 'ok' else '❌'}")
            print(f"  Firebase: {'✅' if services.get('firebase') == 'ok' else '⚠️  (opcional)'}")

            return True
        else:
            print(f"❌ Erro: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False


def test_weather(location):
    """Testa endpoint de weather"""
    print_section(f"🌤️  Testando GET /weather - {location['name']}")

    try:
        url = f"{BASE_URL}/weather"
        params = {"lat": location["lat"], "lon": location["lon"]}

        print(f"URL: {url}")
        print(f"Parâmetros: lat={params['lat']}, lon={params['lon']}\n")

        response = httpx.get(url, params=params, timeout=30.0)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Dados meteorológicos recebidos!\n")

            # Exibir dados formatados
            print("📊 Dados Meteorológicos:")
            print(f"  🌡️  Temperatura:      {data.get('temperature')}°C")
            print(f"  🤚 Sensação Térmica: {data.get('feelsLike')}°C")
            print(f"  💧 Umidade:          {data.get('humidity')}%")
            print(f"  💨 Vento:            {data.get('windSpeed')} km/h")
            print(f"  🧭 Direção:          {data.get('windDirection')}°")
            print(f"  🌪️  Rajadas:          {data.get('windGust')} km/h")
            print(f"  🔽 Pressão:          {data.get('pressure')} hPa")
            print(f"  👁️  Visibilidade:     {data.get('visibility')} km")
            print(f"  ☁️  Nuvens:           {data.get('cloudCover')}%")
            print(f"  ☀️  Índice UV:        {data.get('uvIndex')}")
            print(f"  🕐 Timestamp:        {data.get('timestamp')}")

            print("\n📄 JSON completo:")
            print_json(data)

            return True
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False


def test_air_quality(location):
    """Testa endpoint de qualidade do ar"""
    print_section(f"🌫️  Testando GET /air - {location['name']}")

    try:
        url = f"{BASE_URL}/air"
        params = {"lat": location["lat"], "lon": location["lon"]}

        print(f"URL: {url}")
        print(f"Parâmetros: lat={params['lat']}, lon={params['lon']}\n")

        response = httpx.get(url, params=params, timeout=30.0)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Dados de qualidade do ar recebidos!\n")

            # Exibir dados formatados
            location_info = data.get("location", {})
            pollutants = data.get("pollutants", {})
            aqi = data.get("aqi")
            category = data.get("category")

            print("📍 Localização:")
            print(f"  Nome: {location_info.get('name')}")
            print(f"  Lat:  {location_info.get('lat')}")
            print(f"  Lng:  {location_info.get('lng')}")

            print(f"\n📊 Índice de Qualidade do Ar:")
            print(f"  AQI:       {aqi}")
            print(f"  Categoria: {category}")

            print(f"\n🧪 Poluentes:")
            print(f"  PM2.5: {pollutants.get('pm25')} µg/m³")
            print(f"  NO2:   {pollutants.get('no2')} µg/m³")
            print(f"  O3:    {pollutants.get('o3')} µg/m³")

            print(f"\n🕐 Timestamp: {data.get('timestamp')}")

            print("\n📄 JSON completo:")
            print_json(data)

            return True
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False


def test_subscribe():
    """Testa endpoint de inscrição"""
    print_section("📧 Testando POST /subscribe")

    test_data = {
        "email": "test@example.com",
        "name": "Teste Usuario",
        "location": "São Paulo, Brazil",
        "profile": "general",
        "thresholds": {"aqi": 100}
    }

    try:
        print(f"Dados a enviar:")
        print_json(test_data)
        print()

        response = httpx.post(
            f"{BASE_URL}/subscribe",
            json=test_data,
            timeout=30.0
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Inscrição realizada com sucesso!\n")
            print_json(data)
            return True
        elif response.status_code == 503:
            print("⚠️  Firebase não configurado (esperado)")
            print(response.json())
            return True  # Não é um erro se Firebase não estiver configurado
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False


def test_invalid_coordinates():
    """Testa validação de coordenadas inválidas"""
    print_section("🚫 Testando Validação de Coordenadas Inválidas")

    invalid_tests = [
        {"name": "Latitude muito alta", "lat": 91, "lon": 0},
        {"name": "Latitude muito baixa", "lat": -91, "lon": 0},
        {"name": "Longitude muito alta", "lat": 0, "lon": 181},
        {"name": "Longitude muito baixa", "lat": 0, "lon": -181},
    ]

    all_passed = True

    for test in invalid_tests:
        print(f"\n  Testando: {test['name']}")
        print(f"  Coordenadas: lat={test['lat']}, lon={test['lon']}")

        try:
            response = httpx.get(
                f"{BASE_URL}/weather",
                params={"lat": test["lat"], "lon": test["lon"]},
                timeout=10.0
            )

            if response.status_code == 400:
                print(f"  ✅ Validação funcionou corretamente (400)")
            else:
                print(f"  ❌ Esperado 400, recebeu {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            all_passed = False

    return all_passed


def run_all_tests():
    """Executa todos os testes"""
    print_header("🧪 TESTE COMPLETO DA API - Weather & Air Quality")
    print(f"Base URL: {BASE_URL}")
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Teste 1: Root endpoint
    results.append(("Root Endpoint", test_root()))

    # Teste 2: Health check
    results.append(("Health Check", test_health()))

    # Teste 3: Weather para múltiplas localizações
    for location in TEST_LOCATIONS:
        results.append((f"Weather - {location['name']}", test_weather(location)))

    # Teste 4: Air quality para múltiplas localizações
    for location in TEST_LOCATIONS:
        results.append((f"Air Quality - {location['name']}", test_air_quality(location)))

    # Teste 5: Subscribe
    results.append(("Subscribe", test_subscribe()))

    # Teste 6: Validação de coordenadas
    results.append(("Validação de Coordenadas", test_invalid_coordinates()))

    # Resumo final
    print_header("📊 RESUMO DOS TESTES")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTotal de testes: {total}")
    print(f"Passou: {passed}")
    print(f"Falhou: {total - passed}")
    print(f"Taxa de sucesso: {(passed / total * 100):.1f}%\n")

    print("Detalhes:")
    print("─" * 80)
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<50} {status}")

    print("=" * 80)

    if passed == total:
        print("🎉 Todos os testes passaram! API funcionando perfeitamente!")
    else:
        print("⚠️  Alguns testes falharam. Verifique os detalhes acima.")

    print(f"\nFinalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    print("\n⚠️  IMPORTANTE: Certifique-se que o servidor FastAPI está rodando!")
    print("Execute em outro terminal: python main.py\n")

    try:
        # Verificar se o servidor está rodando
        test_response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
        print("✅ Servidor detectado! Iniciando testes...\n")

        run_all_tests()

    except httpx.ConnectError:
        print("❌ ERRO: Não foi possível conectar ao servidor!")
        print(f"   Certifique-se que o servidor está rodando em {BASE_URL}")
        print("   Execute: python main.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")